import { Message, MessageAttachment } from "@/types/chat";

/**
 * Utility functions for handling messages safely
 */

/**
 * Safely get attachments from a message, ensuring it's always an array
 */
export function getMessageAttachments(message: Message): MessageAttachment[] {
  return message.attachments || [];
}

/**
 * Check if a message has attachments
 */
export function hasAttachments(message: Message): boolean {
  return getMessageAttachments(message).length > 0;
}

/**
 * Normalize a message object to ensure all required fields exist
 */
export function normalizeMessage(message: Message): Message {
  return {
    ...message,
    attachments: message.attachments || [],
    statuses: message.statuses || [],
    encrypted_keys: message.encrypted_keys || [],
  };
}

/**
 * Format file size in a human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";

  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}
