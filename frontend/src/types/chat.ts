// Message types
export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  ciphertext: string;
  ciphertext_nonce: string;
  encryption_algo: string;
  message_type: MessageType;
  preview_text_hash?: string;
  is_edited: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  encrypted_keys: MessageEncryptedKey[];
  attachments: MessageAttachment[];
  statuses: MessageStatus[];
}

export type MessageType =
  | "text"
  | "image"
  | "audio"
  | "video"
  | "document"
  | "location"
  | "contact"
  | "system";

export interface MessageEncryptedKey {
  recipient_user_id: string;
  recipient_device_id: string;
  encrypted_key: string;
  key_algo: string;
  nonce: string;
}

export interface MessageAttachment {
  id: string;
  file_name: string;
  file_size: number;
  content_type: string;
  storage_id: string;
}

export interface MessageStatus {
  user_id: string;
  device_id?: string;
  status: MessageStatusType;
  status_at: string;
}

export type MessageStatusType = "sent" | "delivered" | "read" | "failed";

// Message creation types
export interface MessageCreate {
  conversation_id: string;
  ciphertext: string;
  message_type: MessageType;
  recipient_keys: MessageEncryptedKey[];
  attachments?: MessageAttachment[];
}

export interface MessagesResponse {
  data: Message[];
  count: number;
}

// Conversation types
export interface Conversation {
  id: string;
  title?: string;
  type: ConversationType;
  visibility: ConversationVisibility;
  creator_id: string;
  member_count: number;
  last_message_id?: string;
  last_activity?: string;
  archived: boolean;
  created_at: string;
  updated_at: string;
}

export type ConversationType = "direct" | "group" | "channel" | "support";
export type ConversationVisibility = "private" | "public" | "invite_only";

export interface ConversationMember {
  id: string;
  conversation_id: string;
  user_id: string;
  role: MemberRole;
  joined_at: string;
  last_read_message_id?: string;
  unread_count: number;
  is_muted: boolean;
}

export type MemberRole = "admin" | "moderator" | "member";

export interface ConversationCreate {
  title?: string;
  type: ConversationType;
  visibility: ConversationVisibility;
  description?: string;
  participants: string[];
}

export interface ConversationsResponse {
  data: Conversation[];
  count: number;
}

// Contact types
export interface Contact {
  id: string;
  user_id: string;
  contact_user_id: string;
  display_name?: string;
  is_favorite: boolean;
  is_blocked: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContactCreate {
  contact_user_id: string;
  display_name?: string;
}

export interface ContactsResponse {
  data: Contact[];
  count: number;
}

// WebSocket event types
export interface WebSocketMessage {
  type: string;
  data?: unknown;
}

export interface MessageReceivedEvent {
  type: "message_received";
  data: {
    message: Message;
    conversation_id: string;
  };
}

export interface MessageStatusUpdateEvent {
  type: "message_status_update";
  data: {
    message_id: string;
    status: MessageStatusType;
    user_id: string;
  };
}

export interface TypingEvent {
  type: "typing";
  data: {
    conversation_id: string;
    user_id: string;
    is_typing: boolean;
  };
}

export interface UserStatusEvent {
  type: "user_status";
  data: {
    user_id: string;
    status: "online" | "offline" | "away" | "busy";
    last_seen?: string;
  };
}

// Call types
export interface Call {
  id: string;
  caller_id: string;
  participants: string[];
  type: CallType;
  status: CallStatus;
  started_at: string;
  ended_at?: string;
}

export type CallType = "audio" | "video";
export type CallStatus =
  | "initiating"
  | "ringing"
  | "ongoing"
  | "ended"
  | "missed"
  | "declined"
  | "failed";

export interface CallCreate {
  participants: string[];
  call_type: CallType;
}

export interface CallResponse {
  call_id: string;
  status: CallStatus;
  participants: string[];
  type: CallType;
  signaling_url: string;
}

// Device types
export interface Device {
  id: string;
  user_id: string;
  device_name: string;
  device_type: string;
  platform: string;
  platform_version?: string;
  app_version?: string;
  last_active: string;
  is_active: boolean;
  created_at: string;
}

export interface DeviceCreate {
  device_name: string;
  device_type: string;
  platform: string;
  platform_version?: string;
  app_version?: string;
}

// Utility types for UI state
export interface ChatState {
  conversations: Conversation[];
  currentConversationId?: string;
  messages: Record<string, Message[]>;
  isLoading: boolean;
  isConnected: boolean;
  typingUsers: Record<string, string[]>; // conversation_id -> user_ids
}

export interface MessageDraft {
  conversation_id: string;
  content: string;
  attachments: File[];
}
