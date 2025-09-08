import React, { useState } from "react";
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PhoneIcon,
  VideoCameraIcon,
  EllipsisVerticalIcon,
} from "@heroicons/react/24/outline";
import { ConversationList } from "./conversation-list";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { VideoCall } from "@/components/calls/video-call";
import { useChat } from "@/hooks/use-chat";
import { useCalls } from "@/hooks/use-calls";
import { ConversationCreate } from "@/types/chat";

export function ChatInterface() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showNewConversationModal, setShowNewConversationModal] =
    useState(false);
  const [showVideoCall, setShowVideoCall] = useState(false);

  const {
    conversations,
    messages,
    currentConversationId,
    currentConversation,
    isLoading,
    isConnected,
    selectConversation,
    createConversation,
    sendMessage,
  } = useChat();

  const {
    callState,
    isCallActive,
    isIncomingCall,
    initiateCall,
    error: callError,
    clearError: clearCallError,
  } = useCalls();

  const filteredConversations = conversations.filter(
    (conv) =>
      conv.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateConversation = async (data: ConversationCreate) => {
    try {
      const newConversation = await createConversation(data);
      selectConversation(newConversation.id);
      setShowNewConversationModal(false);
    } catch (error) {
      console.error("Failed to create conversation:", error);
    }
  };

  const handleInitiateCall = async (callType: "audio" | "video") => {
    if (!currentConversation) return;

    try {
      clearCallError();
      // For now, use conversation participants. In a real app, you'd get this from the conversation members
      const participants = ["sample-user-id"]; // This should be replaced with actual conversation participants
      await initiateCall(participants, callType);
      setShowVideoCall(true);
    } catch (error) {
      console.error(`Failed to initiate ${callType} call:`, error);
    }
  };

  const handleCloseCall = () => {
    setShowVideoCall(false);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Error notification */}
      {callError && (
        <div className="fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50">
          <div className="flex items-center justify-between">
            <span>{callError}</span>
            <button
              onClick={clearCallError}
              className="ml-2 text-white hover:text-gray-200"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Video Call Modal */}
      {(showVideoCall || isCallActive || isIncomingCall) && (
        <VideoCall callId={callState.callId} onClose={handleCloseCall} />
      )}

      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold text-gray-900">Chats</h1>
            <button
              onClick={() => setShowNewConversationModal(true)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
              title="New conversation"
            >
              <PlusIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Connection status */}
        <div className="px-4 py-2 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-green-500" : "bg-red-500"
              }`}
            />
            <span className="text-xs text-gray-500">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>

        {/* Conversations list */}
        <ConversationList
          conversations={filteredConversations}
          currentConversationId={currentConversationId}
          onSelectConversation={selectConversation}
          isLoading={isLoading}
        />
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {currentConversation ? (
          <>
            {/* Chat header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-medium">
                      {currentConversation.title?.charAt(0).toUpperCase() ||
                        "C"}
                    </span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {currentConversation.title || "Untitled Conversation"}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {currentConversation.type === "group"
                        ? `${currentConversation.member_count} members`
                        : "Direct message"}
                    </p>
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleInitiateCall("audio")}
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                    title="Voice call"
                  >
                    <PhoneIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleInitiateCall("video")}
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                    title="Video call"
                  >
                    <VideoCameraIcon className="w-5 h-5" />
                  </button>
                  <button
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                    title="More options"
                  >
                    <EllipsisVerticalIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <MessageList messages={messages} isLoading={isLoading} />

            {/* Message input */}
            <MessageInput
              conversationId={currentConversationId!}
              onSendMessage={async (messageData) => {
                await sendMessage(messageData);
              }}
              disabled={!isConnected}
            />
          </>
        ) : (
          /* Empty state */
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center max-w-md mx-auto px-6">
              <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">💬</span>
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                Welcome to Chitthi
              </h2>
              <p className="text-gray-600 mb-6">
                Select a conversation from the sidebar to start chatting, or
                create a new one to begin a secure, end-to-end encrypted
                conversation.
              </p>
              <button
                onClick={() => setShowNewConversationModal(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Start New Conversation
              </button>
            </div>
          </div>
        )}
      </div>

      {/* New Conversation Modal */}
      {showNewConversationModal && (
        <NewConversationModal
          onClose={() => setShowNewConversationModal(false)}
          onCreateConversation={handleCreateConversation}
        />
      )}
    </div>
  );
}

interface NewConversationModalProps {
  onClose: () => void;
  onCreateConversation: (data: ConversationCreate) => void;
}

function NewConversationModal({
  onClose,
  onCreateConversation,
}: NewConversationModalProps) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState<"direct" | "group">("direct");
  const [participants, setParticipants] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const participantList = participants
      .split(",")
      .map((p) => p.trim())
      .filter((p) => p.length > 0);

    const conversationData: ConversationCreate = {
      type,
      visibility: "private",
      participants: participantList,
    };

    if (title.trim()) {
      conversationData.title = title.trim();
    }

    onCreateConversation(conversationData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Create New Conversation
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Conversation Title (optional)
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter conversation title..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as "direct" | "group")}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="direct">Direct Message</option>
              <option value="group">Group Chat</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Participants (User IDs, comma-separated)
            </label>
            <textarea
              value={participants}
              onChange={(e) => setParticipants(e.target.value)}
              placeholder="user1, user2, user3..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter the user IDs of people you want to add to this conversation
            </p>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={participants.trim().length === 0}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Conversation
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
