const jwt = require('jsonwebtoken');

// Secret for JWT signing (use environment variable in production)
const JWT_SECRET = process.env.JWT_SECRET || 'loggin-genie-secret-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';

/**
 * Generate JWT token for user
 */
function generateToken(user) {
  return jwt.sign(
    { 
      username: user.username,
      role: user.role || 'user'
    },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

/**
 * Verify JWT token
 */
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

/**
 * Authentication middleware
 */
function authMiddleware(req, res, next) {
  // Get token from header or cookie
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith('Bearer ') 
    ? authHeader.substring(7) 
    : req.cookies?.token;

  if (!token) {
    return res.status(401).json({ 
      error: 'Authentication required',
      message: 'No token provided'
    });
  }

  const decoded = verifyToken(token);
  
  if (!decoded) {
    return res.status(401).json({ 
      error: 'Invalid token',
      message: 'Token is invalid or expired'
    });
  }

  // Attach user info to request
  req.user = decoded;
  next();
}

/**
 * Optional auth middleware (doesn't fail if no token)
 */
function optionalAuthMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith('Bearer ') 
    ? authHeader.substring(7) 
    : req.cookies?.token;

  if (token) {
    const decoded = verifyToken(token);
    if (decoded) {
      req.user = decoded;
    }
  }
  
  next();
}

module.exports = {
  generateToken,
  verifyToken,
  authMiddleware,
  optionalAuthMiddleware
};
