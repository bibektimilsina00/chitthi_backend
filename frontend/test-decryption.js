/**
 * Test script to verify message decryption logic
 * Run with: node test-decryption.js
 */

// Mock the functions since this is just for testing
function getMessageDisplayContent(ciphertext, messageType, encryptionAlgo) {
    if (messageType !== "text") {
        return `📄 ${messageType} message`;
    }

    // Handle different types of ciphertext
    if (!ciphertext) {
        return "[No content]";
    }

    // If it starts with "encrypted_", extract the content after the prefix
    if (ciphertext.startsWith("encrypted_")) {
        return ciphertext.substring(10); // Remove "encrypted_" prefix
    }

    // If it's a short message without special prefixes, likely plain text for testing
    if (ciphertext.length < 200 &&
        !ciphertext.includes("==") && // Not base64
        !/^[A-Za-z0-9+/=]+$/.test(ciphertext)) { // Not base64 pattern
        return ciphertext;
    }

    // Try to decode if it looks like base64
    try {
        if (ciphertext.includes("==") || /^[A-Za-z0-9+/]+={0,2}$/.test(ciphertext)) {
            const decoded = atob(ciphertext);
            // If decoded successfully and looks like readable text, return it
            if (decoded && /^[\x20-\x7E\s]*$/.test(decoded)) {
                return decoded;
            }
        }
    } catch {
        // Not valid base64, continue to show as encrypted
    }

    // For actual encrypted content, show a user-friendly message
    return `🔒 Encrypted message (${encryptionAlgo})`;
}

// Test messages from your API response
const testMessages = [
    {
        ciphertext: "hi",
        message_type: "text",
        encryption_algo: "xchacha20_poly1305"
    },
    {
        ciphertext: "hello",
        message_type: "text",
        encryption_algo: "xchacha20_poly1305"
    },
    {
        ciphertext: "Hello from WebSocket test!",
        message_type: "text",
        encryption_algo: "xchacha20_poly1305"
    },
    {
        ciphertext: "encrypted_I've prepared the initial requirements document. What do you think?",
        message_type: "text",
        encryption_algo: "aes-256-gcm"
    },
    {
        ciphertext: "SGVsbG8gZXZlcnlvbmUh", // Base64 for "Hello everyone!"
        message_type: "text",
        encryption_algo: "aes-256-gcm"
    }
];

console.log("Testing message decryption logic:\n");

testMessages.forEach((msg, index) => {
    const displayContent = getMessageDisplayContent(
        msg.ciphertext,
        msg.message_type,
        msg.encryption_algo
    );

    console.log(`Message ${index + 1}:`);
    console.log(`  Original: ${msg.ciphertext}`);
    console.log(`  Algorithm: ${msg.encryption_algo}`);
    console.log(`  Display: ${displayContent}`);
    console.log("");
});
