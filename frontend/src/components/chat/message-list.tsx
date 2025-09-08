import React, { useEffect, useRef } from "react";
import { CheckIcon, ClockIcon } from "@heroicons/react/24/outline";
import { Message } from "@/types/chat";
import { useAuth } from "@/hooks/use-auth";
import {
  hasAttachments,
  getMessageAttachments,
  formatFileSize,
} from "@/lib/message-utils";
import { getMessageDisplayContent } from "@/lib/message-decryption";

// Custom double check icon since it's not in heroicons
function DoubleCheckIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4.5 12.75l6 6 9-13.5"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12.75l3 3 9-13.5"
      />
    </svg>
  );
}

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  typingUsers?: string[];
}

export function MessageList({
  messages,
  isLoading = false,
  typingUsers = [],
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading messages...</p>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">💬</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No messages yet
          </h3>
          <p className="text-gray-500">
            Send a message to start the conversation!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => {
        const previousMessage = index > 0 ? messages[index - 1] : null;
        const isConsecutive =
          previousMessage &&
          previousMessage.sender_id === message.sender_id &&
          new Date(message.created_at).getTime() -
            new Date(previousMessage.created_at).getTime() <
            60000; // 1 minute

        return (
          <MessageItem
            key={message.id}
            message={message}
            isOwnMessage={message.sender_id === user?.id}
            showAvatar={!isConsecutive}
            showTimestamp={!isConsecutive}
          />
        );
      })}

      {/* Typing indicators */}
      {typingUsers.length > 0 && (
        <div className="flex items-center space-x-2 px-4 py-2">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
          </div>
          <span className="text-sm text-gray-500">
            {typingUsers.length === 1
              ? "Someone is typing..."
              : `${typingUsers.length} people are typing...`}
          </span>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}

interface MessageItemProps {
  message: Message;
  isOwnMessage: boolean;
  showAvatar: boolean;
  showTimestamp: boolean;
}

function MessageItem({
  message,
  isOwnMessage,
  showAvatar,
  showTimestamp,
}: MessageItemProps) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const getMessageStatus = () => {
    if (!isOwnMessage) return null;

    // For now, we'll use a simple status based on message age
    // In a real app, this would come from the message.statuses array
    const messageAge = Date.now() - new Date(message.created_at).getTime();

    if (messageAge < 1000) {
      return <ClockIcon className="w-4 h-4 text-gray-400" title="Sending..." />;
    } else if (messageAge < 60000) {
      return <CheckIcon className="w-4 h-4 text-gray-400" title="Sent" />;
    } else {
      return <DoubleCheckIcon className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <div className={`flex ${isOwnMessage ? "justify-end" : "justify-start"}`}>
      <div
        className={`flex max-w-xs lg:max-w-md ${
          isOwnMessage ? "flex-row-reverse" : "flex-row"
        }`}
      >
        {/* Avatar */}
        {showAvatar && !isOwnMessage && (
          <div className="flex-shrink-0 mr-3">
            <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {message.sender_id.charAt(0).toUpperCase()}
              </span>
            </div>
          </div>
        )}

        {/* Message content */}
        <div
          className={`flex flex-col ${
            isOwnMessage ? "items-end" : "items-start"
          }`}
        >
          {showTimestamp && (
            <div className="text-xs text-gray-500 mb-1 px-2">
              {formatTime(message.created_at)}
            </div>
          )}

          <div
            className={`
              relative px-4 py-2 rounded-lg max-w-full break-words
              ${
                isOwnMessage
                  ? "bg-blue-500 text-white rounded-br-sm"
                  : "bg-gray-100 text-gray-900 rounded-bl-sm"
              }
            `}
          >
            <MessageContent message={message} />

            {/* Message status for own messages */}
            {isOwnMessage && (
              <div className="absolute -bottom-1 -right-1 bg-white rounded-full p-0.5">
                {getMessageStatus()}
              </div>
            )}
          </div>

          {/* Edited indicator */}
          {message.is_edited && (
            <div className="text-xs text-gray-400 mt-1 px-2">edited</div>
          )}
        </div>
      </div>
    </div>
  );
}

interface MessageContentProps {
  message: Message;
}

function MessageContent({ message }: MessageContentProps) {
  const attachments = getMessageAttachments(message);

  // Try to decode mock messages for development, otherwise show encrypted placeholder
  const getDisplayContent = () => {
    // Use the new decryption utility for text messages
    if (message.message_type === "text") {
      return getMessageDisplayContent(
        message.ciphertext,
        message.message_type,
        message.encryption_algo
      );
    }

    // Keep existing logic for other message types
    switch (message.message_type) {
      case "image":
        return (
          <div className="flex items-center space-x-2 text-sm">
            <span>📷</span>
            <span>Image</span>
          </div>
        );
      case "audio":
        return (
          <div className="flex items-center space-x-2 text-sm">
            <span>🎵</span>
            <span>Audio message</span>
          </div>
        );
      case "video":
        return (
          <div className="flex items-center space-x-2 text-sm">
            <span>🎥</span>
            <span>Video</span>
          </div>
        );
      case "document":
        return (
          <div className="flex items-center space-x-2 text-sm">
            <span>📄</span>
            <span>Document</span>
          </div>
        );
      case "system":
        return (
          <div className="italic text-sm opacity-75">{message.ciphertext}</div>
        );
      default:
        return "[Unsupported message type]";
    }
  };

  return (
    <div>
      {getDisplayContent()}

      {/* Attachments */}
      {hasAttachments(message) && (
        <div className="mt-2 space-y-1">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="flex items-center space-x-2 text-sm bg-black bg-opacity-10 rounded p-2"
            >
              <span>📎</span>
              <span className="truncate">{attachment.file_name}</span>
              <span className="text-xs opacity-75">
                ({formatFileSize(attachment.file_size)})
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
