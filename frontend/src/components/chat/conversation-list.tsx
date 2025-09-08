import React from "react";
import {
  ChevronRightIcon,
  UserGroupIcon,
  ChatBubbleLeftIcon,
} from "@heroicons/react/24/outline";
import { Conversation } from "@/types/chat";

interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  isLoading?: boolean;
}

export function ConversationList({
  conversations,
  currentConversationId,
  onSelectConversation,
  isLoading = false,
}: ConversationListProps) {
  if (isLoading) {
    return (
      <div className="flex-1 p-4">
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="flex items-center space-x-3 p-3 rounded-lg animate-pulse"
            >
              <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <ChatBubbleLeftIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No conversations yet
          </h3>
          <p className="text-gray-500">
            Start a new conversation to begin chatting!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="space-y-1 p-2">
        {conversations.map((conversation) => (
          <ConversationItem
            key={conversation.id}
            conversation={conversation}
            isActive={conversation.id === currentConversationId}
            onClick={() => onSelectConversation(conversation.id)}
          />
        ))}
      </div>
    </div>
  );
}

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMinutes = Math.floor(
    (now.getTime() - date.getTime()) / (1000 * 60)
  );

  if (diffInMinutes < 1) return "Just now";
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays}d ago`;

  return date.toLocaleDateString();
}

function ConversationItem({
  conversation,
  isActive,
  onClick,
}: ConversationItemProps) {
  const displayName = conversation.title || "Untitled Conversation";
  const lastActivity = conversation.last_activity
    ? formatRelativeTime(conversation.last_activity)
    : "No activity";

  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center space-x-3 p-3 rounded-lg transition-colors text-left
        ${
          isActive
            ? "bg-blue-50 border-blue-200 border text-blue-900"
            : "hover:bg-gray-50 border border-transparent"
        }
      `}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
          {conversation.type === "group" ? (
            <UserGroupIcon className="w-6 h-6 text-white" />
          ) : (
            <ChatBubbleLeftIcon className="w-6 h-6 text-white" />
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900 truncate">
            {displayName}
          </h3>
          <div className="flex items-center space-x-1">
            <span className="text-xs text-gray-500">{lastActivity}</span>
            <ChevronRightIcon className="w-4 h-4 text-gray-400" />
          </div>
        </div>

        <div className="flex items-center justify-between mt-1">
          <p className="text-sm text-gray-500 truncate">
            {conversation.type === "group"
              ? `${conversation.member_count} members`
              : "Direct message"}
          </p>

          {/* Unread indicator - placeholder for now */}
          {Math.random() > 0.7 && (
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          )}
        </div>
      </div>
    </button>
  );
}
