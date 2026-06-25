/**
 * Web Crypto API Encryption Utilities
 * 
 * Provides secure client-side encryption for IndexedDB storage.
 * Uses AES-GCM with key derivation from user credentials.
 */

const ALGORITHM = 'AES-GCM';
const KEY_LENGTH = 256;
const IV_LENGTH = 12; // 96 bits for AES-GCM
const SALT_LENGTH = 16;
const ITERATIONS = 100000; // PBKDF2 iterations

/**
 * Generate a cryptographic key from a password
 * @param {string} password - User password or passphrase
 * @param {Uint8Array} salt - Salt for key derivation
 * @returns {Promise<CryptoKey>} Derived encryption key
 */
async function deriveKey(password, salt) {
  const encoder = new TextEncoder();
  const passwordBuffer = encoder.encode(password);
  
  // Import password as base key
  const baseKey = await crypto.subtle.importKey(
    'raw',
    passwordBuffer,
    'PBKDF2',
    false,
    ['deriveBits', 'deriveKey']
  );
  
  // Derive AES key using PBKDF2
  const key = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: ITERATIONS,
      hash: 'SHA-256'
    },
    baseKey,
    {
      name: ALGORITHM,
      length: KEY_LENGTH
    },
    false, // Not extractable
    ['encrypt', 'decrypt']
  );
  
  return key;
}

/**
 * Encrypt data
 * @param {any} data - Data to encrypt (will be JSON stringified)
 * @param {string} password - Encryption password
 * @returns {Promise<{encrypted: string, salt: string, iv: string}>}
 */
export async function encryptData(data, password) {
  try {
    // Generate random salt and IV
    const salt = crypto.getRandomValues(new Uint8Array(SALT_LENGTH));
    const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));
    
    // Derive encryption key
    const key = await deriveKey(password, salt);
    
    // Convert data to string and then to buffer
    const encoder = new TextEncoder();
    const dataString = JSON.stringify(data);
    const dataBuffer = encoder.encode(dataString);
    
    // Encrypt data
    const encryptedBuffer = await crypto.subtle.encrypt(
      {
        name: ALGORITHM,
        iv: iv
      },
      key,
      dataBuffer
    );
    
    // Convert to base64 for storage
    const encryptedArray = new Uint8Array(encryptedBuffer);
    const encrypted = btoa(String.fromCharCode(...encryptedArray));
    const saltB64 = btoa(String.fromCharCode(...salt));
    const ivB64 = btoa(String.fromCharCode(...iv));
    
    return {
      encrypted,
      salt: saltB64,
      iv: ivB64
    };
  } catch (error) {
    console.error('[Crypto] Encryption failed:', error);
    throw new Error('Encryption failed');
  }
}

/**
 * Decrypt data
 * @param {string} encrypted - Encrypted data (base64)
 * @param {string} saltB64 - Salt (base64)
 * @param {string} ivB64 - IV (base64)
 * @param {string} password - Decryption password
 * @returns {Promise<any>} Decrypted data
 */
export async function decryptData(encrypted, saltB64, ivB64, password) {
  try {
    // Convert from base64
    const encryptedArray = new Uint8Array(
      atob(encrypted).split('').map(c => c.charCodeAt(0))
    );
    const salt = new Uint8Array(
      atob(saltB64).split('').map(c => c.charCodeAt(0))
    );
    const iv = new Uint8Array(
      atob(ivB64).split('').map(c => c.charCodeAt(0))
    );
    
    // Derive decryption key
    const key = await deriveKey(password, salt);
    
    // Decrypt data
    const decryptedBuffer = await crypto.subtle.decrypt(
      {
        name: ALGORITHM,
        iv: iv
      },
      key,
      encryptedArray
    );
    
    // Convert back to original data
    const decoder = new TextDecoder();
    const decryptedString = decoder.decode(decryptedBuffer);
    const data = JSON.parse(decryptedString);
    
    return data;
  } catch (error) {
    console.error('[Crypto] Decryption failed:', error);
    throw new Error('Decryption failed - incorrect password or corrupted data');
  }
}

/**
 * Generate a secure random password for session
 * @returns {string} Random password
 */
export function generateSessionKey() {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array));
}

/**
 * Hash data (for integrity checking)
 * @param {string} data - Data to hash
 * @returns {Promise<string>} SHA-256 hash in hex
 */
export async function hashData(data) {
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);
  const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Store encryption key in sessionStorage (memory only, cleared on tab close)
 * @param {string} key - Encryption key
 */
export function storeEncryptionKey(key) {
  sessionStorage.setItem('__enc_key', key);
}

/**
 * Get encryption key from sessionStorage
 * @returns {string|null} Encryption key or null
 */
export function getEncryptionKey() {
  return sessionStorage.getItem('__enc_key');
}

/**
 * Clear encryption key
 */
export function clearEncryptionKey() {
  sessionStorage.removeItem('__enc_key');
}

/**
 * Check if Web Crypto API is available
 * @returns {boolean}
 */
export function isCryptoAvailable() {
  return typeof crypto !== 'undefined' && 
         typeof crypto.subtle !== 'undefined';
}

export default {
  encryptData,
  decryptData,
  generateSessionKey,
  hashData,
  storeEncryptionKey,
  getEncryptionKey,
  clearEncryptionKey,
  isCryptoAvailable
};
