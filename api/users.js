const bcrypt = require('bcryptjs');
const crypto = require('crypto');

// In-memory user store (use database in production)
// Password: admin (hashed with bcrypt)
const users = new Map([
  ['admin', {
    username: 'admin',
    // bcrypt hash of 'admin'
    passwordHash: '$2a$10$rBV2uL5Z5Z5Z5Z5Z5Z5Z5eqK8mYvK7qX0qX0qX0qX0qX0qX0qX0qO',
    role: 'admin',
    encryptionKey: null, // Stored encryption key
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }]
]);

/**
 * Hash password
 */
async function hashPassword(password) {
  return await bcrypt.hash(password, 10);
}

/**
 * Verify password
 */
async function verifyPassword(password, hash) {
  return await bcrypt.compare(password, hash);
}

/**
 * Find user by username
 */
function findUser(username) {
  return users.get(username);
}

/**
 * Create new user
 */
async function createUser(username, password, role = 'user') {
  if (users.has(username)) {
    throw new Error('User already exists');
  }

  const passwordHash = await hashPassword(password);
  const user = {
    username,
    passwordHash,
    role,
    createdAt: new Date().toISOString()
  };

  users.set(username, user);
  return user;
}

/**
 * Authenticate user
 */
async function authenticateUser(username, password) {
  const user = findUser(username);
  
  if (!user) {
    return null;
  }

  const isValid = await verifyPassword(password, user.passwordHash);
  
  if (!isValid) {
    return null;
  }

  // Return user without password hash
  const { passwordHash, ...userWithoutPassword } = user;
  return userWithoutPassword;
}

/**
 * Initialize default admin user
 */
async function initializeDefaultUsers() {
  // Create admin user with password 'admin'
  const adminHash = await hashPassword('admin');
  users.set('admin', {
    username: 'admin',
    passwordHash: adminHash,
    role: 'admin',
    encryptionKey: null,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  });

  console.log('✅ Default admin user initialized (username: admin, password: admin)');
}

/**
 * Update user's encryption key
 */
function updateEncryptionKey(username, encryptionKey) {
  const user = users.get(username);
  
  if (!user) {
    throw new Error('User not found');
  }

  user.encryptionKey = encryptionKey;
  user.updatedAt = new Date().toISOString();
  users.set(username, user);
  
  return true;
}

/**
 * Get user's encryption key
 */
function getEncryptionKey(username) {
  const user = users.get(username);
  return user?.encryptionKey || null;
}

/**
 * Get redacted encryption key (show only first 8 and last 4 chars)
 */
function getRedactedKey(encryptionKey) {
  if (!encryptionKey || encryptionKey.length < 12) {
    return null;
  }
  
  const first = encryptionKey.substring(0, 8);
  const last = encryptionKey.substring(encryptionKey.length - 4);
  const middle = '*'.repeat(Math.min(32, encryptionKey.length - 12));
  
  return `${first}${middle}${last}`;
}

/**
 * Get user profile (without sensitive data)
 */
function getUserProfile(username) {
  const user = users.get(username);
  
  if (!user) {
    return null;
  }

  const { passwordHash, encryptionKey, ...profile } = user;
  
  return {
    ...profile,
    hasEncryptionKey: !!encryptionKey,
    encryptionKeyRedacted: encryptionKey ? getRedactedKey(encryptionKey) : null
  };
}

module.exports = {
  hashPassword,
  verifyPassword,
  findUser,
  createUser,
  authenticateUser,
  initializeDefaultUsers,
  updateEncryptionKey,
  getEncryptionKey,
  getRedactedKey,
  getUserProfile
};
