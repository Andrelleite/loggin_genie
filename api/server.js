const express = require('express');
const cors = require('cors');
const multer = require('multer');
const cookieParser = require('cookie-parser');
const rateLimit = require('express-rate-limit');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');
const morgan = require('morgan');
require('dotenv').config();

const { generateToken, authMiddleware, optionalAuthMiddleware } = require('./auth');
const { authenticateUser, initializeDefaultUsers, updateEncryptionKey, getEncryptionKey, getUserProfile } = require('./users');

const app = express();
const PORT = process.env.PORT || 3000;

// Trust proxy (needed for rate limiting behind nginx)
app.set('trust proxy', 1);

// Initialize default users
initializeDefaultUsers();

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 login attempts per 15 minutes
  message: 'Too many login attempts, please try again later'
});

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || true,
  credentials: true
}));
app.use(express.json());
app.use(cookieParser());
app.use(morgan('combined'));
app.use('/api/', limiter);

// Storage configuration for multer
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'uploads');
    await fs.mkdir(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ 
  storage,
  limits: { fileSize: 50 * 1024 * 1024 }, // 50MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/json' || 
        file.mimetype === 'text/plain' ||
        file.originalname.endsWith('.json') ||
        file.originalname.endsWith('.ndjson')) {
      cb(null, true);
    } else {
      cb(new Error('Only JSON and NDJSON files are allowed'));
    }
  }
});

// In-memory job storage (use Redis in production)
const jobs = new Map();

// Validation schemas
const decryptFileSchema = Joi.object({
  encryptionKey: Joi.string().optional().allow(''), // Now optional - can use stored key
  algorithm: Joi.string().valid('AES-256-CBC', 'AES-128-CBC', 'AES-256-GCM', 'AES-128-GCM').default('AES-256-CBC'),
  field: Joi.string().default('message'),
  outputFormat: Joi.string().valid('json', 'text', 'table').default('json')
});

const decryptKibanaSchema = Joi.object({
  elasticsearchUrl: Joi.string().uri().required(),
  index: Joi.string().required(),
  encryptionKey: Joi.string().optional().allow(''), // Now optional - can use stored key
  algorithm: Joi.string().valid('AES-256-CBC', 'AES-128-CBC', 'AES-256-GCM', 'AES-128-GCM').default('AES-256-CBC'),
  field: Joi.string().default('message'),
  query: Joi.object().optional(),
  size: Joi.number().integer().min(1).max(10000).default(100),
  username: Joi.string().optional(),
  password: Joi.string().optional(),
  apiKey: Joi.string().optional(),
  outputFormat: Joi.string().valid('json', 'text').default('json')
});

// Helper function to run Python script
function runPythonDecryption(args) {
  return new Promise((resolve, reject) => {
    const pythonPath = process.env.PYTHON_PATH || 'python3';
    // In Docker, the script is in /app/loggin_genie.py
    const scriptPath = process.env.NODE_ENV === 'production' 
      ? '/app/loggin_genie.py' 
      : path.join(__dirname, '..', 'loggin_genie.py');
    
    const pythonProcess = spawn(pythonPath, [scriptPath, ...args]);
    
    let stdout = '';
    let stderr = '';
    
    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(new Error(`Python process exited with code ${code}: ${stderr}`));
      }
    });
    
    pythonProcess.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
  });
}

// Routes

// Health check (public)
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'Loggin Genie API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    authenticated: !!req.user
  });
});

// Login endpoint
app.post('/api/auth/login', loginLimiter, async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ 
        error: 'Username and password required' 
      });
    }

    const user = await authenticateUser(username, password);

    if (!user) {
      return res.status(401).json({ 
        error: 'Invalid credentials',
        message: 'Username or password is incorrect'
      });
    }

    // Generate JWT token
    const token = generateToken(user);

    // Set cookie
    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
      sameSite: 'lax'
    });

    res.json({
      success: true,
      message: 'Login successful',
      user: {
        username: user.username,
        role: user.role
      },
      token
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// Logout endpoint
app.post('/api/auth/logout', (req, res) => {
  res.clearCookie('token');
  res.json({ 
    success: true, 
    message: 'Logged out successfully' 
  });
});

// Check auth status
app.get('/api/auth/status', optionalAuthMiddleware, (req, res) => {
  if (req.user) {
    res.json({
      authenticated: true,
      user: {
        username: req.user.username,
        role: req.user.role
      }
    });
  } else {
    res.json({
      authenticated: false
    });
  }
});

// Get user profile (PROTECTED)
app.get('/api/profile', authMiddleware, (req, res) => {
  try {
    const profile = getUserProfile(req.user.username);
    
    if (!profile) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json({
      success: true,
      profile
    });
  } catch (error) {
    console.error('Error fetching profile:', error);
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
});

// Update encryption key (PROTECTED)
app.put('/api/profile/encryption-key', authMiddleware, async (req, res) => {
  try {
    const { encryptionKey } = req.body;
    
    // Validate encryption key format (should be hex string)
    if (!encryptionKey || typeof encryptionKey !== 'string') {
      return res.status(400).json({ error: 'Invalid encryption key format' });
    }
    
    // Check if it's a valid hex string (optional but recommended)
    const hexPattern = /^[0-9a-fA-F]+$/;
    if (!hexPattern.test(encryptionKey)) {
      return res.status(400).json({ error: 'Encryption key must be a valid hexadecimal string' });
    }
    
    // Update the key
    updateEncryptionKey(req.user.username, encryptionKey);
    
    // Return updated profile
    const profile = getUserProfile(req.user.username);
    
    res.json({
      success: true,
      message: 'Encryption key updated successfully',
      profile
    });
  } catch (error) {
    console.error('Error updating encryption key:', error);
    res.status(500).json({ error: 'Failed to update encryption key' });
  }
});

// Delete encryption key (PROTECTED)
app.delete('/api/profile/encryption-key', authMiddleware, (req, res) => {
  try {
    updateEncryptionKey(req.user.username, null);
    
    const profile = getUserProfile(req.user.username);
    
    res.json({
      success: true,
      message: 'Encryption key deleted successfully',
      profile
    });
  } catch (error) {
    console.error('Error deleting encryption key:', error);
    res.status(500).json({ error: 'Failed to delete encryption key' });
  }
});

// Upload and decrypt log file (PROTECTED)
app.post('/api/decrypt/file', authMiddleware, upload.single('logFile'), async (req, res) => {
  const jobId = uuidv4();
  
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    // Validate request body
    const { error, value } = decryptFileSchema.validate(req.body);
    if (error) {
      await fs.unlink(req.file.path).catch(() => {});
      return res.status(400).json({ error: error.details[0].message });
    }
    
    let { encryptionKey, algorithm, field, outputFormat } = value;
    
    // If no key provided, use stored key
    if (!encryptionKey || encryptionKey.trim() === '') {
      encryptionKey = getEncryptionKey(req.user.username);
      if (!encryptionKey) {
        await fs.unlink(req.file.path).catch(() => {});
        return res.status(400).json({ 
          error: 'No encryption key provided and no key stored in profile. Please provide a key or save one in your profile.' 
        });
      }
    }
    
    // Create job
    jobs.set(jobId, {
      id: jobId,
      status: 'processing',
      createdAt: new Date().toISOString(),
      fileName: req.file.originalname
    });
    
    // Return job ID immediately
    res.json({
      jobId,
      status: 'processing',
      message: 'Decryption job started',
      statusUrl: `/api/jobs/${jobId}`
    });
    
    // Process in background
    (async () => {
      try {
        const outputPath = path.join(__dirname, 'output', `${jobId}.json`);
        await fs.mkdir(path.join(__dirname, 'output'), { recursive: true });
        
        const args = [
          '--file', req.file.path,
          '--key', encryptionKey,
          '--algorithm', algorithm,
          '--field', field,
          '--format', outputFormat,
          '--output', outputPath
        ];
        
        await runPythonDecryption(args);
        
        // Read decrypted output
        const decryptedData = await fs.readFile(outputPath, 'utf-8');
        
        // Update job status
        jobs.set(jobId, {
          ...jobs.get(jobId),
          status: 'completed',
          completedAt: new Date().toISOString(),
          result: outputFormat === 'json' ? JSON.parse(decryptedData) : decryptedData,
          downloadUrl: `/api/jobs/${jobId}/download`
        });
        
        // Cleanup uploaded file
        await fs.unlink(req.file.path).catch(() => {});
        
      } catch (error) {
        jobs.set(jobId, {
          ...jobs.get(jobId),
          status: 'failed',
          error: error.message,
          completedAt: new Date().toISOString()
        });
        
        // Cleanup
        await fs.unlink(req.file.path).catch(() => {});
      }
    })();
    
  } catch (error) {
    if (req.file) {
      await fs.unlink(req.file.path).catch(() => {});
    }
    res.status(500).json({ error: error.message });
  }
});

// Decrypt from Kibana (PROTECTED)
app.post('/api/decrypt/kibana', authMiddleware, async (req, res) => {
  const jobId = uuidv4();
  
  try {
    // Validate request
    const { error, value } = decryptKibanaSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }
    
    let { 
      elasticsearchUrl, 
      index, 
      encryptionKey, 
      algorithm, 
      field, 
      query, 
      size,
      username,
      password,
      apiKey,
      outputFormat 
    } = value;
    
    // If no key provided, use stored key
    if (!encryptionKey || encryptionKey.trim() === '') {
      encryptionKey = getEncryptionKey(req.user.username);
      if (!encryptionKey) {
        return res.status(400).json({ 
          error: 'No encryption key provided and no key stored in profile. Please provide a key or save one in your profile.' 
        });
      }
    }
    
    // Create job
    jobs.set(jobId, {
      id: jobId,
      status: 'processing',
      createdAt: new Date().toISOString(),
      source: 'kibana',
      index
    });
    
    // Return job ID immediately
    res.json({
      jobId,
      status: 'processing',
      message: 'Decryption job started',
      statusUrl: `/api/jobs/${jobId}`
    });
    
    // Process in background
    (async () => {
      try {
        const outputPath = path.join(__dirname, 'output', `${jobId}.json`);
        await fs.mkdir(path.join(__dirname, 'output'), { recursive: true });
        
        const args = [
          '--elasticsearch-url', elasticsearchUrl,
          '--index', index,
          '--key', encryptionKey,
          '--algorithm', algorithm,
          '--field', field,
          '--size', size.toString(),
          '--format', outputFormat,
          '--output', outputPath
        ];
        
        if (username) args.push('--username', username);
        if (password) args.push('--password', password);
        if (apiKey) args.push('--api-key', apiKey);
        if (query) args.push('--query', JSON.stringify(query));
        
        await runPythonDecryption(args);
        
        // Read decrypted output
        const decryptedData = await fs.readFile(outputPath, 'utf-8');
        
        // Update job status
        jobs.set(jobId, {
          ...jobs.get(jobId),
          status: 'completed',
          completedAt: new Date().toISOString(),
          result: outputFormat === 'json' ? JSON.parse(decryptedData) : decryptedData,
          downloadUrl: `/api/jobs/${jobId}/download`
        });
        
      } catch (error) {
        jobs.set(jobId, {
          ...jobs.get(jobId),
          status: 'failed',
          error: error.message,
          completedAt: new Date().toISOString()
        });
      }
    })();
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get job status (PROTECTED)
app.get('/api/jobs/:jobId', authMiddleware, (req, res) => {
  const { jobId } = req.params;
  const job = jobs.get(jobId);
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  // Don't send full result in status check, just metadata
  const { result, ...jobMetadata } = job;
  
  res.json({
    ...jobMetadata,
    hasResult: !!result,
    resultSize: result ? JSON.stringify(result).length : 0
  });
});

// Get job result (PROTECTED)
app.get('/api/jobs/:jobId/result', authMiddleware, (req, res) => {
  const { jobId } = req.params;
  const job = jobs.get(jobId);
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  if (job.status !== 'completed') {
    return res.status(400).json({ 
      error: 'Job not completed', 
      status: job.status 
    });
  }
  
  res.json(job.result);
});

// Download job result (PROTECTED)
app.get('/api/jobs/:jobId/download', authMiddleware, async (req, res) => {
  const { jobId } = req.params;
  const job = jobs.get(jobId);
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  if (job.status !== 'completed') {
    return res.status(400).json({ 
      error: 'Job not completed', 
      status: job.status 
    });
  }
  
  const outputPath = path.join(__dirname, 'output', `${jobId}.json`);
  
  try {
    await fs.access(outputPath);
    res.download(outputPath, `decrypted-logs-${jobId}.json`);
  } catch (error) {
    res.status(404).json({ error: 'Result file not found' });
  }
});

// List all jobs (PROTECTED)
app.get('/api/jobs', authMiddleware, (req, res) => {
  const allJobs = Array.from(jobs.values()).map(job => {
    const { result, ...jobMetadata } = job;
    return jobMetadata;
  });
  
  res.json({
    total: allJobs.length,
    jobs: allJobs
  });
});

// Delete job (PROTECTED)
app.delete('/api/jobs/:jobId', authMiddleware, async (req, res) => {
  const { jobId } = req.params;
  const job = jobs.get(jobId);
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  // Delete output file
  const outputPath = path.join(__dirname, 'output', `${jobId}.json`);
  await fs.unlink(outputPath).catch(() => {});
  
  // Remove from jobs
  jobs.delete(jobId);
  
  res.json({ message: 'Job deleted successfully' });
});

// Error handler
app.use((error, req, res, next) => {
  console.error('Error:', error);
  res.status(500).json({ 
    error: error.message || 'Internal server error' 
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🧞‍♂️ Loggin Genie API running on port ${PORT}`);
  console.log(`📝 API Documentation: http://localhost:${PORT}/health`);
});

module.exports = app;
