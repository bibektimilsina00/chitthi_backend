import React, { useState, useEffect } from "react";
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
import { useChat, useWebSocket } from "@/hooks/use-chat";
import { useCalls, useIncomingCalls } from "@/hooks/use-calls";
import { ConversationCreate, User, WebSocketMessage } from "@/types/chat";
import { usersApi, conversationsApi } from "@/lib/chat-api";

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
    refreshConversations,
  } = useChat();

  const { addEventListener, removeEventListener } = useWebSocket();

  const {
    callState,
    isCallActive,
    isIncomingCall,
    initiateCall,
    error: callError,
    clearError: clearCallError,
  } = useCalls();

  const { incomingCall, handleIncomingCall, clearIncomingCall } =
    useIncomingCalls();

  // Handle incoming call notifications from WebSocket
  useEffect(() => {
    const handleIncomingCallEvent = (event: WebSocketMessage) => {
      console.log("📞 ChatInterface: Incoming call event received", event);
      console.log("📞 ChatInterface: event.data type:", typeof event.data);
      console.log("📞 ChatInterface: event.data value:", event.data);

      const data = event.data as {
        type: string;
        call_id: string;
        caller_id: string;
        caller_name?: string;
        call_type: "audio" | "video";
      };

      console.log("📞 ChatInterface: Parsed data:", data);
      console.log("📞 ChatInterface: data.type:", data?.type);
      console.log(
        "📞 ChatInterface: Checking condition:",
        data && data.type === "incoming_call"
      );

      if (data && data.type === "incoming_call") {
        console.log("📞 ChatInterface: Processing incoming call:", data);
        console.log("📞 ChatInterface: Current callState before:", callState);
        console.log(
          "📞 ChatInterface: Current isIncomingCall before:",
          isIncomingCall
        );

        console.log("📞 ChatInterface: About to call handleIncomingCall");
        console.log(
          "📞 ChatInterface: handleIncomingCall function:",
          handleIncomingCall
        );

        try {
          handleIncomingCall(data.call_id, data.caller_id, data.call_type);
          console.log(
            "📞 ChatInterface: handleIncomingCall completed successfully"
          );
        } catch (error) {
          console.error(
            "📞 ChatInterface: Error calling handleIncomingCall:",
            error
          );
        }

        // Force show video call for debugging
        console.log("📞 ChatInterface: Setting showVideoCall to true");
        setShowVideoCall(true);

        // Log state after a brief delay to see if it updates
        setTimeout(() => {
          console.log(
            "📞 ChatInterface: Call state after handling:",
            callState
          );
          console.log(
            "📞 ChatInterface: isIncomingCall after handling:",
            isIncomingCall
          );
        }, 100);
      }
    };

    addEventListener("incoming_call", handleIncomingCallEvent);

    return () => {
      removeEventListener("incoming_call", handleIncomingCallEvent);
    };
  }, [
    addEventListener,
    removeEventListener,
    handleIncomingCall,
    callState,
    isIncomingCall,
  ]);

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

      // Get actual conversation participants (excluding current user)
      let participants: string[] = [];

      if (
        currentConversation.other_participants &&
        currentConversation.other_participants.length > 0
      ) {
        participants = currentConversation.other_participants.map(
          (user) => user.id
        );
      } else {
        console.warn("No participants found for call");
        return;
      }

      console.log(
        "Initiating call with participants:",
        participants,
        "type:",
        callType
      );
      await initiateCall(participants, callType);
      setShowVideoCall(true);
    } catch (error) {
      console.error(`Failed to initiate ${callType} call:`, error);
    }
  };

  const getConversationDisplayName = (
    conversation: typeof currentConversation
  ) => {
    if (conversation?.title) {
      return conversation.title;
    }

    if (
      conversation?.type === "direct" &&
      conversation.other_participants &&
      conversation.other_participants.length > 0
    ) {
      const otherUser = conversation.other_participants[0];
      return otherUser?.display_name || otherUser?.username;
    }

    if (conversation?.type === "group") {
      return `Group (${conversation.member_count} members)`;
    }

    return "Untitled Conversation";
  };

  const getConversationSubtitle = (
    conversation: typeof currentConversation
  ) => {
    if (conversation?.type === "group") {
      return `${conversation.member_count} members`;
    } else if (
      conversation?.type === "direct" &&
      conversation.other_participants &&
      conversation.other_participants.length > 0
    ) {
      return "Direct message";
    }
    return "Direct message";
  };

  const handleCloseCall = () => {
    setShowVideoCall(false);
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Debug info - Always visible */}
      <div className="fixed top-4 right-4 bg-black text-white p-2 rounded z-50 text-xs">
        showVideoCall: {showVideoCall.toString()}
        <br />
        isCallActive: {isCallActive.toString()}
        <br />
        isIncomingCall: {isIncomingCall.toString()}
        <br />
        callId: {callState.callId || "none"}
        <br />
        incomingCall: {incomingCall ? "yes" : "no"}
      </div>

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
                      {getConversationDisplayName(currentConversation)
                        ?.charAt(0)
                        .toUpperCase() || "C"}
                    </span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {getConversationDisplayName(currentConversation)}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {getConversationSubtitle(currentConversation)}
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
          selectConversation={selectConversation}
          refreshConversations={refreshConversations}
        />
      )}
    </div>
  );
}

interface NewConversationModalProps {
  onClose: () => void;
  onCreateConversation: (data: ConversationCreate) => void;
  selectConversation: (conversationId: string) => void;
  refreshConversations: () => Promise<unknown>;
}

function NewConversationModal({
  onClose,
  onCreateConversation,
  selectConversation,
  refreshConversations,
}: NewConversationModalProps) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState<"direct" | "group">("direct");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await usersApi.searchUsers(query.trim());
      setSearchResults(response.data);
    } catch (error) {
      console.error("Failed to search users:", error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleUserSelect = (user: User) => {
    if (type === "direct") {
      // For direct messages, create conversation immediately
      handleCreateDirectConversation(user);
    } else {
      // For group chats, add to selected users
      if (!selectedUsers.find((u) => u.id === user.id)) {
        setSelectedUsers([...selectedUsers, user]);
      }
      setSearchQuery("");
      setSearchResults([]);
    }
  };

  const handleCreateDirectConversation = async (user: User) => {
    try {
      const conversation = await conversationsApi.createDirectConversation(
        user.id
      );
      // Refresh the conversations list to include the new conversation
      await refreshConversations();
      // Navigate to the new conversation
      selectConversation(conversation.id);
      // Close the modal
      onClose();
    } catch (error) {
      console.error("Failed to create direct conversation:", error);
    }
  };

  const handleRemoveUser = (userId: string) => {
    setSelectedUsers(selectedUsers.filter((u) => u.id !== userId));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (type === "direct") {
      // This shouldn't happen as direct conversations are created immediately
      return;
    }

    if (selectedUsers.length === 0) {
      return;
    }

    const conversationData: ConversationCreate = {
      type,
      visibility: "private",
      participants: selectedUsers.map((u) => u.id),
    };

    if (title.trim()) {
      conversationData.title = title.trim();
    }

    onCreateConversation(conversationData);
  };

  const getDisplayName = (user: User) => {
    return user.display_name || user.username;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[80vh] overflow-y-auto">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {type === "direct" ? "Start New Chat" : "Create Group Chat"}
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Chat type selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chat Type
            </label>
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={() => {
                  setType("direct");
                  setSelectedUsers([]);
                  setTitle("");
                }}
                className={`px-3 py-2 text-sm rounded-md border ${
                  type === "direct"
                    ? "bg-blue-50 border-blue-200 text-blue-700"
                    : "bg-gray-50 border-gray-200 text-gray-700"
                }`}
              >
                Direct Message
              </button>
              <button
                type="button"
                onClick={() => setType("group")}
                className={`px-3 py-2 text-sm rounded-md border ${
                  type === "group"
                    ? "bg-blue-50 border-blue-200 text-blue-700"
                    : "bg-gray-50 border-gray-200 text-gray-700"
                }`}
              >
                Group Chat
              </button>
            </div>
          </div>

          {/* Group title (only for group chats) */}
          {type === "group" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Group Name
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter group name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          {/* User search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {type === "direct" ? "Search User" : "Add Participants"}
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search by username or email..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {isSearching && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
              )}
            </div>

            {/* Search results */}
            {searchResults.length > 0 && (
              <div className="mt-2 border border-gray-200 rounded-md max-h-40 overflow-y-auto">
                {searchResults.map((user) => (
                  <button
                    key={user.id}
                    type="button"
                    onClick={() => handleUserSelect(user)}
                    className="w-full px-3 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                  >
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-sm font-medium">
                          {getDisplayName(user).charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {getDisplayName(user)}
                        </div>
                        <div className="text-xs text-gray-500">
                          @{user.username}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Selected users (for group chats) */}
          {type === "group" && selectedUsers.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Selected Participants ({selectedUsers.length})
              </label>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {selectedUsers.map((user) => (
                  <div
                    key={user.id}
                    className="flex items-center justify-between bg-gray-50 rounded-md px-3 py-2"
                  >
                    <div className="flex items-center space-x-2">
                      <div className="w-6 h-6 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-medium">
                          {getDisplayName(user).charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span className="text-sm text-gray-900">
                        {getDisplayName(user)}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveUser(user.id)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            {type === "group" && (
              <button
                type="submit"
                disabled={selectedUsers.length === 0 || !title.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Group
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
