import { useState, useEffect, useCallback, useRef } from "react";
import useSWR from "swr";
import { useAuth } from "./use-auth";
import { conversationsApi, messagesApi } from "@/lib/chat-api";
import { webSocketManager, type WebSocketEventType } from "@/lib/websocket";
import { useMockData } from "@/lib/mock-data";
import {
  type ConversationCreate,
  type MessageCreate,
  type WebSocketMessage,
  type MessageDraft,
} from "@/types/chat";

/**
 * Hook for managing conversations
 */
export function useConversations() {
  const { user } = useAuth();
  const { getMockConversations, shouldUseMockData } = useMockData();

  const {
    data: conversationsResponse,
    error,
    mutate,
    isLoading,
  } = useSWR(
    user ? "/conversations" : null,
    async () => {
      try {
        return await conversationsApi.getConversations();
      } catch (err) {
        // If API fails, return mock data structure
        if (shouldUseMockData(err, null)) {
          return {
            data: getMockConversations(),
            count: getMockConversations().length,
          };
        }
        throw err;
      }
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  );

  // Use mock data if no data and in development
  const finalData =
    conversationsResponse ||
    (shouldUseMockData(error, conversationsResponse)
      ? { data: getMockConversations(), count: getMockConversations().length }
      : { data: [], count: 0 });

  const createConversation = useCallback(
    async (data: ConversationCreate) => {
      const newConversation = await conversationsApi.createConversation(data);
      // Update the cache optimistically
      mutate();
      return newConversation;
    },
    [mutate]
  );

  const archiveConversation = useCallback(
    async (conversationId: string) => {
      await conversationsApi.archiveConversation(conversationId);
      mutate();
    },
    [mutate]
  );

  const leaveConversation = useCallback(
    async (conversationId: string) => {
      await conversationsApi.leaveConversation(conversationId);
      mutate();
    },
    [mutate]
  );

  return {
    conversations: finalData.data || [],
    count: finalData.count || 0,
    isLoading,
    error,
    createConversation,
    archiveConversation,
    leaveConversation,
    refreshConversations: mutate,
  };
}

/**
 * Hook for managing messages in a specific conversation
 */
export function useMessages(conversationId: string | null) {
  const { user } = useAuth();
  const { getMockMessages, shouldUseMockData } = useMockData();

  const {
    data: messagesResponse,
    error,
    mutate,
    isLoading,
  } = useSWR(
    user && conversationId ? `/messages/${conversationId}` : null,
    async () => {
      try {
        return await messagesApi.getMessages(conversationId!);
      } catch (err) {
        // If API fails, return mock data structure
        if (shouldUseMockData(err, null)) {
          return {
            data: getMockMessages(conversationId!),
            count: getMockMessages(conversationId!).length,
          };
        }
        throw err;
      }
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  );

  // Use mock data if no data and in development
  const finalData =
    messagesResponse ||
    (shouldUseMockData(error, messagesResponse)
      ? {
          data: getMockMessages(conversationId || ""),
          count: getMockMessages(conversationId || "").length,
        }
      : { data: [], count: 0 });

  const sendMessage = useCallback(
    async (messageData: MessageCreate) => {
      const newMessage = await messagesApi.sendMessage(messageData);
      // Optimistically update the cache
      mutate();
      return newMessage;
    },
    [mutate]
  );

  const editMessage = useCallback(
    async (messageId: string, ciphertext: string) => {
      const updatedMessage = await messagesApi.editMessage(
        messageId,
        ciphertext
      );
      mutate();
      return updatedMessage;
    },
    [mutate]
  );

  const deleteMessage = useCallback(
    async (messageId: string) => {
      await messagesApi.deleteMessage(messageId);
      mutate();
    },
    [mutate]
  );

  const reactToMessage = useCallback(
    async (messageId: string, reaction: string) => {
      await messagesApi.reactToMessage(messageId, reaction);
      mutate();
    },
    [mutate]
  );

  return {
    messages: finalData.data || [],
    count: finalData.count || 0,
    isLoading,
    error,
    sendMessage,
    editMessage,
    deleteMessage,
    reactToMessage,
    refreshMessages: mutate,
  };
}

/**
 * Hook for managing WebSocket connection and real-time events
 */
export function useWebSocket() {
  const { user } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const deviceIdRef = useRef<string | null>(null);

  // Generate a device ID if we don't have one
  useEffect(() => {
    if (user && !deviceIdRef.current) {
      // In a real app, this should be stored in localStorage or generated by device registration
      deviceIdRef.current = `web-${Date.now()}-${Math.random()
        .toString(36)
        .substr(2, 9)}`;
    }
  }, [user]);

  // Connect to WebSocket when user is authenticated
  useEffect(() => {
    if (user && deviceIdRef.current && !isConnected && !isConnecting) {
      setIsConnecting(true);
      webSocketManager
        .connect(deviceIdRef.current)
        .then((connected) => {
          setIsConnected(connected);
          setIsConnecting(false);
        })
        .catch((error) => {
          console.error("WebSocket connection failed:", error);
          setIsConnecting(false);
        });
    }

    return () => {
      if (!user) {
        webSocketManager.disconnect();
        setIsConnected(false);
      }
    };
  }, [user, isConnected, isConnecting]);

  // Listen for connection status changes
  useEffect(() => {
    const handleConnectionChange = (connected: boolean) => {
      setIsConnected(connected);
      if (!connected) {
        setIsConnecting(false);
      }
    };

    webSocketManager.addConnectionListener(handleConnectionChange);

    return () => {
      webSocketManager.removeConnectionListener(handleConnectionChange);
    };
  }, []);

  const joinConversation = useCallback((conversationId: string) => {
    return webSocketManager.joinConversation(conversationId);
  }, []);

  const leaveConversation = useCallback((conversationId: string) => {
    return webSocketManager.leaveConversation(conversationId);
  }, []);

  const sendMessage = useCallback((messageData: MessageCreate) => {
    return webSocketManager.sendMessage(messageData);
  }, []);

  const sendTyping = useCallback(
    (conversationId: string, isTyping: boolean) => {
      return webSocketManager.sendTyping(conversationId, isTyping);
    },
    []
  );

  const addEventListener = useCallback(
    (eventType: string, handler: (event: WebSocketMessage) => void) => {
      webSocketManager.addEventListener(
        eventType as WebSocketEventType,
        handler
      );
    },
    []
  );

  const removeEventListener = useCallback(
    (eventType: string, handler: (event: WebSocketMessage) => void) => {
      webSocketManager.removeEventListener(
        eventType as WebSocketEventType,
        handler
      );
    },
    []
  );

  return {
    isConnected,
    isConnecting,
    joinConversation,
    leaveConversation,
    sendMessage,
    sendTyping,
    addEventListener,
    removeEventListener,
  };
}

/**
 * Hook for managing overall chat state
 */
export function useChat() {
  const [currentConversationId, setCurrentConversationId] = useState<
    string | null
  >(null);
  const [typingUsers, setTypingUsers] = useState<Record<string, string[]>>({});
  const [drafts, setDrafts] = useState<Record<string, MessageDraft>>({});

  const {
    conversations,
    isLoading: conversationsLoading,
    createConversation,
  } = useConversations();
  const {
    messages,
    isLoading: messagesLoading,
    sendMessage,
  } = useMessages(currentConversationId);
  const { isConnected, isConnecting, addEventListener, removeEventListener } =
    useWebSocket();

  // Handle real-time message updates
  useEffect(() => {
    const handleMessageReceived = (event: WebSocketMessage) => {
      const data = event.data as { message: unknown; conversation_id: string };
      console.log("New message received:", data);
      // The messages will be updated automatically by SWR revalidation
    };

    const handleTypingUpdate = (event: WebSocketMessage) => {
      const data = event.data as {
        conversation_id: string;
        user_id: string;
        is_typing: boolean;
      };
      const { conversation_id, user_id, is_typing } = data;

      setTypingUsers((prev) => {
        const conversationTyping = prev[conversation_id] || [];

        if (is_typing) {
          // Add user to typing list if not already there
          if (!conversationTyping.includes(user_id)) {
            return {
              ...prev,
              [conversation_id]: [...conversationTyping, user_id],
            };
          }
        } else {
          // Remove user from typing list
          return {
            ...prev,
            [conversation_id]: conversationTyping.filter(
              (id) => id !== user_id
            ),
          };
        }

        return prev;
      });
    };

    addEventListener("message_received", handleMessageReceived);
    addEventListener("typing", handleTypingUpdate);

    return () => {
      removeEventListener("message_received", handleMessageReceived);
      removeEventListener("typing", handleTypingUpdate);
    };
  }, [addEventListener, removeEventListener]);

  // Auto-clear typing indicators after timeout
  useEffect(() => {
    const timeouts: Record<string, NodeJS.Timeout> = {};

    Object.entries(typingUsers).forEach(([conversationId, users]) => {
      users.forEach((userId) => {
        const key = `${conversationId}-${userId}`;

        // Clear existing timeout
        if (timeouts[key]) {
          clearTimeout(timeouts[key]);
        }

        // Set new timeout to clear typing indicator
        timeouts[key] = setTimeout(() => {
          setTypingUsers((prev) => ({
            ...prev,
            [conversationId]:
              prev[conversationId]?.filter((id) => id !== userId) || [],
          }));
        }, 3000);
      });
    });

    return () => {
      Object.values(timeouts).forEach(clearTimeout);
    };
  }, [typingUsers]);

  const selectConversation = useCallback((conversationId: string) => {
    setCurrentConversationId(conversationId);
  }, []);

  const saveDraft = useCallback(
    (conversationId: string, content: string, attachments: File[] = []) => {
      setDrafts((prev) => ({
        ...prev,
        [conversationId]: {
          conversation_id: conversationId,
          content,
          attachments,
        },
      }));
    },
    []
  );

  const clearDraft = useCallback((conversationId: string) => {
    setDrafts((prev) => {
      const newDrafts = { ...prev };
      delete newDrafts[conversationId];
      return newDrafts;
    });
  }, []);

  const getDraft = useCallback(
    (conversationId: string): MessageDraft | null => {
      return drafts[conversationId] || null;
    },
    [drafts]
  );

  return {
    // State
    conversations,
    messages,
    currentConversationId,
    currentConversation:
      conversations.find((c) => c.id === currentConversationId) || null,
    typingUsers,
    isLoading: conversationsLoading || messagesLoading,
    isConnected,
    isConnecting,

    // Actions
    selectConversation,
    createConversation,
    sendMessage,
    saveDraft,
    clearDraft,
    getDraft,
  };
}
