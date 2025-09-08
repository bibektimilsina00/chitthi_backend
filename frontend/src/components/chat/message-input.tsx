import React, { useState, useRef, useCallback } from "react";
import {
  PaperAirplaneIcon,
  PaperClipIcon,
  FaceSmileIcon,
  MicrophoneIcon,
} from "@heroicons/react/24/outline";
import { MessageCreate, MessageType } from "@/types/chat";

interface MessageInputProps {
  conversationId: string;
  onSendMessage: (messageData: MessageCreate) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  conversationId,
  onSendMessage,
  disabled = false,
  placeholder = "Type a message...",
}: MessageInputProps) {
  const [message, setMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, []);

  // Handle typing indicators
  const handleTypingStart = useCallback(() => {
    if (!isTyping) {
      setIsTyping(true);
      // In a real app, send typing indicator via WebSocket
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      // In a real app, send stop typing indicator via WebSocket
    }, 3000);
  }, [isTyping]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    adjustTextareaHeight();
    handleTypingStart();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSendMessage = async () => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage && attachments.length === 0) return;
    if (isSending || disabled) return;

    setIsSending(true);

    try {
      // For now, we'll create a mock encrypted message
      // In a real app, this would be encrypted client-side
      const messageData: MessageCreate = {
        conversation_id: conversationId,
        ciphertext: trimmedMessage || "File attachment",
        message_type:
          attachments.length > 0 && attachments[0]
            ? getMessageTypeFromAttachment(attachments[0])
            : "text",
        recipient_keys: [], // This would be populated with actual encrypted keys
        attachments: attachments.map((file) => ({
          id: crypto.randomUUID(),
          file_name: file.name,
          file_size: file.size,
          content_type: file.type,
          storage_id: crypto.randomUUID(), // This would come from file upload
        })),
      };

      await onSendMessage(messageData);

      // Clear input
      setMessage("");
      setAttachments([]);
      setIsTyping(false);

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }

      // Clear typing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      // Handle error (show toast, etc.)
    } finally {
      setIsSending(false);
    }
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAttachments((prev) => [...prev, ...files]);

    // Clear the input to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const getMessageTypeFromAttachment = (file: File): MessageType => {
    if (file.type.startsWith("image/")) return "image";
    if (file.type.startsWith("audio/")) return "audio";
    if (file.type.startsWith("video/")) return "video";
    return "document";
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  return (
    <div className="border-t bg-white p-4">
      {/* Attachments preview */}
      {attachments.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {attachments.map((file, index) => (
            <div
              key={index}
              className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-2 text-sm"
            >
              <span className="text-gray-600">📎</span>
              <span className="font-medium truncate max-w-32">{file.name}</span>
              <span className="text-gray-500">
                ({formatFileSize(file.size)})
              </span>
              <button
                onClick={() => removeAttachment(index)}
                className="text-red-500 hover:text-red-700 ml-1"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-end space-x-3">
        {/* Attachment button */}
        <button
          onClick={handleFileSelect}
          disabled={disabled}
          className="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
          title="Attach file"
        >
          <PaperClipIcon className="w-5 h-5" />
        </button>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileChange}
          className="hidden"
          accept="image/*,audio/*,video/*,.pdf,.doc,.docx,.txt"
        />

        {/* Message input */}
        <div className="flex-1 min-w-0">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isSending}
            rows={1}
            className="
              w-full px-4 py-2 border border-gray-300 rounded-lg resize-none
              focus:ring-2 focus:ring-blue-500 focus:border-transparent
              disabled:opacity-50 disabled:cursor-not-allowed
              placeholder-gray-500
            "
            style={{ minHeight: "40px", maxHeight: "120px" }}
          />
        </div>

        {/* Action buttons */}
        <div className="flex items-center space-x-2">
          {/* Emoji button (placeholder) */}
          <button
            disabled={disabled}
            className="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
            title="Add emoji"
          >
            <FaceSmileIcon className="w-5 h-5" />
          </button>

          {/* Voice message button (placeholder) */}
          <button
            disabled={disabled}
            className="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
            title="Voice message"
          >
            <MicrophoneIcon className="w-5 h-5" />
          </button>

          {/* Send button */}
          <button
            onClick={handleSendMessage}
            disabled={
              disabled ||
              isSending ||
              (!message.trim() && attachments.length === 0)
            }
            className="
              flex-shrink-0 p-2 bg-blue-500 text-white rounded-full 
              hover:bg-blue-600 transition-colors
              disabled:opacity-50 disabled:cursor-not-allowed
              disabled:hover:bg-blue-500
            "
            title="Send message"
          >
            {isSending ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <PaperAirplaneIcon className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Typing indicator (for current user) */}
      {isTyping && (
        <div className="text-xs text-gray-500 mt-2 px-4">You are typing...</div>
      )}
    </div>
  );
}
