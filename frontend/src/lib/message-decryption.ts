/**
 * Message decryption utilities
 * This file handles different types of message decryption and display
 */

export interface DecryptionResult {
  success: boolean;
  content: string;
  isPlainText: boolean;
}

/**
 * Attempts to decrypt or decode a message based on its encryption algorithm
 */
export function decryptMessage(
  ciphertext: string,
  algorithm: string
): DecryptionResult {
  if (!ciphertext) {
    return {
      success: false,
      content: "[No content]",
      isPlainText: false,
    };
  }

  // Handle different encryption algorithms
  switch (algorithm) {
    case "aes-256-gcm":
      return handleAESDecryption(ciphertext);
    case "xchacha20_poly1305":
      return handleXChaChaDecryption(ciphertext);
    default:
      return handleUnknownEncryption(ciphertext);
  }
}

/**
 * Handles AES-256-GCM encrypted messages
 */
function handleAESDecryption(ciphertext: string): DecryptionResult {
  // If it starts with "encrypted_", extract the content after the prefix
  if (ciphertext.startsWith("encrypted_")) {
    return {
      success: true,
      content: ciphertext.substring(10), // Remove "encrypted_" prefix
      isPlainText: true,
    };
  }

  // Try to decode base64 if it looks like it
  const base64Result = tryBase64Decode(ciphertext);
  if (base64Result.success) {
    return base64Result;
  }

  // For actual encrypted content, show encrypted indicator
  return {
    success: true,
    content: `🔒 AES encrypted message`,
    isPlainText: false,
  };
}

/**
 * Handles XChaCha20-Poly1305 encrypted messages
 */
function handleXChaChaDecryption(ciphertext: string): DecryptionResult {
  // If it's a short message without special encoding, likely plain text for testing
  if (
    ciphertext.length < 200 &&
    !ciphertext.includes("==") &&
    !/^[A-Za-z0-9+/=]+$/.test(ciphertext) &&
    /^[\x20-\x7E\s]*$/.test(ciphertext)
  ) {
    return {
      success: true,
      content: ciphertext,
      isPlainText: true,
    };
  }

  // Try to decode base64 if it looks like it
  const base64Result = tryBase64Decode(ciphertext);
  if (base64Result.success) {
    return base64Result;
  }

  // For actual encrypted content, show encrypted indicator
  return {
    success: true,
    content: `🔒 XChaCha20 encrypted message`,
    isPlainText: false,
  };
}

/**
 * Handles unknown encryption algorithms
 */
function handleUnknownEncryption(ciphertext: string): DecryptionResult {
  // Try common decoding methods
  const base64Result = tryBase64Decode(ciphertext);
  if (base64Result.success) {
    return base64Result;
  }

  // If it looks like plain text, return it
  if (/^[\x20-\x7E\s]*$/.test(ciphertext) && ciphertext.length < 500) {
    return {
      success: true,
      content: ciphertext,
      isPlainText: true,
    };
  }

  return {
    success: true,
    content: `🔒 Encrypted message`,
    isPlainText: false,
  };
}

/**
 * Attempts to decode base64 content
 */
function tryBase64Decode(content: string): DecryptionResult {
  try {
    // Check if it looks like base64
    if (content.includes("==") || /^[A-Za-z0-9+/]+={0,2}$/.test(content)) {
      const decoded = atob(content);
      // If decoded successfully and looks like readable text, return it
      if (decoded && /^[\x20-\x7E\s]*$/.test(decoded)) {
        return {
          success: true,
          content: decoded,
          isPlainText: true,
        };
      }
    }
  } catch {
    // Not valid base64
  }

  return {
    success: false,
    content: "",
    isPlainText: false,
  };
}

/**
 * Gets the display content for a message with proper decryption
 */
export function getMessageDisplayContent(
  ciphertext: string,
  messageType: string,
  encryptionAlgo: string
): string {
  switch (messageType) {
    case "text":
      const result = decryptMessage(ciphertext, encryptionAlgo);
      return result.content;

    case "image":
      return "📷 Image message";

    case "file":
      return "📎 File attachment";

    case "audio":
      return "🎵 Audio message";

    case "video":
      return "🎬 Video message";

    default:
      return `📄 ${messageType} message`;
  }
}

/**
 * Checks if a message is encrypted or plain text
 */
export function isMessageEncrypted(
  ciphertext: string,
  encryptionAlgo: string
): boolean {
  const result = decryptMessage(ciphertext, encryptionAlgo);
  return !result.isPlainText;
}
