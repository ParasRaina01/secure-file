/**
 * Utility functions for client-side encryption using Web Crypto API
 */

/**
 * Generate a random encryption key for AES-256-GCM
 */
export async function generateKey(): Promise<CryptoKey> {
  return await window.crypto.subtle.generateKey(
    {
      name: 'AES-GCM',
      length: 256
    },
    true, // extractable
    ['encrypt', 'decrypt']
  );
}

/**
 * Export a CryptoKey to raw bytes
 */
export async function exportKey(key: CryptoKey): Promise<ArrayBuffer> {
  return await window.crypto.subtle.exportKey('raw', key);
}

/**
 * Import raw bytes as a CryptoKey
 */
export async function importKey(keyData: ArrayBuffer): Promise<CryptoKey> {
  return await window.crypto.subtle.importKey(
    'raw',
    keyData,
    'AES-GCM',
    true,
    ['encrypt', 'decrypt']
  );
}

/**
 * Generate a random IV for AES-GCM
 */
export function generateIV(): Uint8Array {
  return window.crypto.getRandomValues(new Uint8Array(12));
}

/**
 * Encrypt a file using AES-256-GCM
 */
export async function encryptFile(
  file: File
): Promise<{
  encryptedFile: File;
  key: ArrayBuffer;
  iv: Uint8Array;
}> {
  // Generate encryption key and IV
  const key = await generateKey();
  const iv = generateIV();
  
  // Read file as ArrayBuffer
  const fileData = await file.arrayBuffer();
  
  // Encrypt the file data
  const encryptedData = await window.crypto.subtle.encrypt(
    {
      name: 'AES-GCM',
      iv
    },
    key,
    fileData
  );
  
  // Export the key for transmission
  const exportedKey = await exportKey(key);
  
  // Create a new file with encrypted data
  const encryptedFile = new File([encryptedData], file.name, {
    type: 'application/octet-stream',
    lastModified: file.lastModified
  });
  
  return {
    encryptedFile,
    key: exportedKey,
    iv
  };
}

/**
 * Decrypt a file using AES-256-GCM
 */
export async function decryptFile(
  encryptedFile: File,
  keyData: ArrayBuffer,
  iv: Uint8Array
): Promise<File> {
  // Import the encryption key
  const key = await importKey(keyData);
  
  // Read encrypted file data
  const encryptedData = await encryptedFile.arrayBuffer();
  
  // Decrypt the file data
  const decryptedData = await window.crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv
    },
    key,
    encryptedData
  );
  
  // Create a new file with decrypted data
  return new File([decryptedData], encryptedFile.name.replace('.encrypted', ''), {
    type: 'application/octet-stream',
    lastModified: encryptedFile.lastModified
  });
}

/**
 * Convert ArrayBuffer to Base64 string
 */
export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Convert Base64 string to ArrayBuffer
 */
export function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
} 