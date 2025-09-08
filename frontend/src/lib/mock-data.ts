import { useState } from "react";
import { Conversation, Message } from "@/types/chat";

// Mock data for development/testing
const mockConversations: Conversation[] = [
  {
    id: "conv-1",
    title: "General Discussion",
    type: "group",
    visibility: "private",
    creator_id: "user-1",
    member_count: 5,
    last_message_id: "msg-3",
    last_activity: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    archived: false,
    created_at: new Date(Date.now() - 86400000 * 7).toISOString(), // 1 week ago
    updated_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "conv-2",
    title: "Project Alpha",
    type: "group",
    visibility: "private",
    creator_id: "user-2",
    member_count: 3,
    last_message_id: "msg-2",
    last_activity: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    archived: false,
    created_at: new Date(Date.now() - 86400000 * 3).toISOString(), // 3 days ago
    updated_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: "conv-3",
    type: "direct",
    visibility: "private",
    creator_id: "user-1",
    member_count: 2,
    last_message_id: "msg-1",
    last_activity: new Date(Date.now() - 14400000).toISOString(), // 4 hours ago
    archived: false,
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(), // 2 days ago
    updated_at: new Date(Date.now() - 14400000).toISOString(),
  },
];

const mockMessages: Record<string, Message[]> = {
  "conv-1": [
    {
      id: "msg-1",
      conversation_id: "conv-1",
      sender_id: "user-2",
      ciphertext: "SGVsbG8gZXZlcnlvbmUh", // Base64 for "Hello everyone!"
      ciphertext_nonce: "nonce123",
      encryption_algo: "aes-256-gcm",
      message_type: "text",
      is_edited: false,
      is_deleted: false,
      created_at: new Date(Date.now() - 14400000).toISOString(),
      updated_at: new Date(Date.now() - 14400000).toISOString(),
      encrypted_keys: [],
      attachments: [],
      statuses: [],
    },
    {
      id: "msg-2",
      conversation_id: "conv-1",
      sender_id: "user-3",
      ciphertext: "SGkgdGhlcmUh", // Base64 for "Hi there!"
      ciphertext_nonce: "nonce124",
      encryption_algo: "aes-256-gcm",
      message_type: "text",
      is_edited: false,
      is_deleted: false,
      created_at: new Date(Date.now() - 10800000).toISOString(),
      updated_at: new Date(Date.now() - 10800000).toISOString(),
      encrypted_keys: [],
      attachments: [],
      statuses: [],
    },
    {
      id: "msg-3",
      conversation_id: "conv-1",
      sender_id: "user-1", // Current user
      ciphertext: "SG93IGlzIGV2ZXJ5b25lIGRvaW5nPw==", // Base64 for "How is everyone doing?"
      ciphertext_nonce: "nonce125",
      encryption_algo: "aes-256-gcm",
      message_type: "text",
      is_edited: false,
      is_deleted: false,
      created_at: new Date(Date.now() - 3600000).toISOString(),
      updated_at: new Date(Date.now() - 3600000).toISOString(),
      encrypted_keys: [],
      attachments: [],
      statuses: [],
    },
  ],
  "conv-2": [
    {
      id: "msg-4",
      conversation_id: "conv-2",
      sender_id: "user-2",
      ciphertext: "UHJvamVjdCB1cGRhdGU=", // Base64 for "Project update"
      ciphertext_nonce: "nonce126",
      encryption_algo: "aes-256-gcm",
      message_type: "text",
      is_edited: false,
      is_deleted: false,
      created_at: new Date(Date.now() - 7200000).toISOString(),
      updated_at: new Date(Date.now() - 7200000).toISOString(),
      encrypted_keys: [],
      attachments: [],
      statuses: [],
    },
  ],
  "conv-3": [
    {
      id: "msg-5",
      conversation_id: "conv-3",
      sender_id: "user-4",
      ciphertext: "SGV5LCBob3cgYXJlIHlvdT8=", // Base64 for "Hey, how are you?"
      ciphertext_nonce: "nonce127",
      encryption_algo: "aes-256-gcm",
      message_type: "text",
      is_edited: false,
      is_deleted: false,
      created_at: new Date(Date.now() - 18000000).toISOString(),
      updated_at: new Date(Date.now() - 18000000).toISOString(),
      encrypted_keys: [],
      attachments: [],
      statuses: [],
    },
    {
      id: "msg-6",
      conversation_id: "conv-3",
      sender_id: "user-1", // Current user
      ciphertext: "SSdtIGRvaW5nIGdyZWF0IQ==", // Base64 for "I'm doing great!"
      ciphertext_nonce: "nonce128",
      encryption_algo: "aes-256-gcm",
      message_type: "text",
      is_edited: false,
      is_deleted: false,
      created_at: new Date(Date.now() - 14400000).toISOString(),
      updated_at: new Date(Date.now() - 14400000).toISOString(),
      encrypted_keys: [],
      attachments: [],
      statuses: [],
    },
  ],
};

/**
 * Hook to provide mock data when backend is not available or empty
 */
export function useMockData() {
  const [useMockMode, setUseMockMode] = useState(false);

  const shouldUseMockData = (error: unknown, data: unknown) => {
    // Use mock data if:
    // 1. There's a network error
    // 2. Backend returns empty data
    // 3. Development mode is enabled
    return (
      error ||
      !data ||
      (Array.isArray(data) && data.length === 0) ||
      process.env.NODE_ENV === "development"
    );
  };

  const getMockConversations = () => mockConversations;

  const getMockMessages = (conversationId: string) => {
    return mockMessages[conversationId] || [];
  };

  return {
    useMockMode,
    setUseMockMode,
    shouldUseMockData,
    getMockConversations,
    getMockMessages,
  };
}

/**
 * Utility to decode mock encrypted messages for display
 */
export function decodeMockMessage(ciphertext: string): string {
  try {
    return atob(ciphertext);
  } catch {
    return "[Encrypted Message]";
  }
}
