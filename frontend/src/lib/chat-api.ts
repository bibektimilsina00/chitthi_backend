import apiClient from "./api-client";
import {
  Conversation,
  ConversationsResponse,
  ConversationCreate,
  ConversationMember,
  Message,
  MessagesResponse,
  MessageCreate,
  Contact,
  ContactsResponse,
  ContactCreate,
  Call,
  CallCreate,
  CallResponse,
  Device,
  DeviceCreate,
  User,
  UsersResponse,
} from "@/types/chat";

/**
 * Users API service
 */
export const usersApi = {
  // Search users
  async searchUsers(
    search: string,
    skip = 0,
    limit = 20
  ): Promise<UsersResponse> {
    return apiClient.get<UsersResponse>("/users/search", {
      search,
      skip,
      limit,
    });
  },

  // Get user by ID
  async getUser(userId: string): Promise<User> {
    return apiClient.get<User>(`/users/${userId}`);
  },
};

/**
 * Conversations API service
 */
export const conversationsApi = {
  // Get user conversations
  async getConversations(
    skip = 0,
    limit = 100
  ): Promise<ConversationsResponse> {
    return apiClient.get<ConversationsResponse>("/conversations/", {
      skip,
      limit,
    });
  },

  // Create new conversation
  async createConversation(data: ConversationCreate): Promise<Conversation> {
    return apiClient.post<Conversation>("/conversations/", data);
  },

  // Create direct conversation with a specific user
  async createDirectConversation(userId: string): Promise<Conversation> {
    return apiClient.post<Conversation>(`/conversations/direct/${userId}`, {});
  },

  // Get conversation by ID
  async getConversation(conversationId: string): Promise<Conversation> {
    return apiClient.get<Conversation>(`/conversations/${conversationId}`);
  },

  // Update conversation
  async updateConversation(
    conversationId: string,
    data: Partial<ConversationCreate>
  ): Promise<Conversation> {
    return apiClient.patch<Conversation>(
      `/conversations/${conversationId}`,
      data
    );
  },

  // Delete conversation
  async deleteConversation(
    conversationId: string
  ): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(
      `/conversations/${conversationId}`
    );
  },

  // Archive conversation
  async archiveConversation(conversationId: string): Promise<Conversation> {
    return apiClient.patch<Conversation>(
      `/conversations/${conversationId}/archive`,
      {}
    );
  },

  // Leave conversation
  async leaveConversation(
    conversationId: string
  ): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(
      `/conversations/${conversationId}/leave`,
      {}
    );
  },

  // Get conversation members
  async getMembers(conversationId: string): Promise<ConversationMember[]> {
    return apiClient.get<ConversationMember[]>(
      `/conversations/${conversationId}/members`
    );
  },

  // Add member to conversation
  async addMember(
    conversationId: string,
    userId: string
  ): Promise<ConversationMember> {
    return apiClient.post<ConversationMember>(
      `/conversations/${conversationId}/members`,
      { user_id: userId }
    );
  },

  // Remove member from conversation
  async removeMember(
    conversationId: string,
    userId: string
  ): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(
      `/conversations/${conversationId}/members/${userId}`
    );
  },

  // Update member role
  async updateMemberRole(
    conversationId: string,
    userId: string,
    role: string
  ): Promise<ConversationMember> {
    return apiClient.patch<ConversationMember>(
      `/conversations/${conversationId}/members/${userId}`,
      { role }
    );
  },
};

/**
 * Messages API service
 */
export const messagesApi = {
  // Get messages for a conversation
  async getMessages(
    conversationId: string,
    skip = 0,
    limit = 100
  ): Promise<MessagesResponse> {
    return apiClient.get<MessagesResponse>("/messages/", {
      conversation_id: conversationId,
      skip,
      limit,
    });
  },

  // Send a message
  async sendMessage(data: MessageCreate): Promise<Message> {
    return apiClient.post<Message>("/messages/", data);
  },

  // Get message by ID
  async getMessage(messageId: string): Promise<Message> {
    return apiClient.get<Message>(`/messages/${messageId}`);
  },

  // Edit a message
  async editMessage(messageId: string, ciphertext: string): Promise<Message> {
    return apiClient.patch<Message>(`/messages/${messageId}`, { ciphertext });
  },

  // Delete a message
  async deleteMessage(messageId: string): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`/messages/${messageId}`);
  },

  // React to a message
  async reactToMessage(
    messageId: string,
    reaction: string
  ): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(
      `/messages/${messageId}/reactions`,
      {
        reaction,
      }
    );
  },

  // Remove reaction from message
  async removeReaction(messageId: string): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(
      `/messages/${messageId}/reactions`
    );
  },

  // Star/unstar a message
  async toggleStar(messageId: string): Promise<Message> {
    return apiClient.post<Message>(`/messages/${messageId}/star`, {});
  },

  // Mark message as read
  async markAsRead(messageId: string): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(
      `/messages/${messageId}/read`,
      {}
    );
  },
};

/**
 * Contacts API service
 */
export const contactsApi = {
  // Get user contacts
  async getContacts(skip = 0, limit = 100): Promise<ContactsResponse> {
    return apiClient.get<ContactsResponse>("/contacts/", {
      skip,
      limit,
    });
  },

  // Add a contact
  async addContact(data: ContactCreate): Promise<Contact> {
    return apiClient.post<Contact>("/contacts/", data);
  },

  // Get contact by ID
  async getContact(contactId: string): Promise<Contact> {
    return apiClient.get<Contact>(`/contacts/${contactId}`);
  },

  // Update contact
  async updateContact(
    contactId: string,
    data: Partial<ContactCreate>
  ): Promise<Contact> {
    return apiClient.patch<Contact>(`/contacts/${contactId}`, data);
  },

  // Delete contact
  async deleteContact(contactId: string): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`/contacts/${contactId}`);
  },

  // Block contact
  async blockContact(contactId: string): Promise<Contact> {
    return apiClient.post<Contact>(`/contacts/${contactId}/block`, {});
  },

  // Unblock contact
  async unblockContact(contactId: string): Promise<Contact> {
    return apiClient.post<Contact>(`/contacts/${contactId}/unblock`, {});
  },

  // Toggle favorite
  async toggleFavorite(contactId: string): Promise<Contact> {
    return apiClient.post<Contact>(`/contacts/${contactId}/favorite`, {});
  },

  // Search contacts
  async searchContacts(query: string): Promise<ContactsResponse> {
    return apiClient.get<ContactsResponse>("/contacts/search", { q: query });
  },
};

/**
 * Calls API service
 */
export const callsApi = {
  // Initiate a call
  async initiateCall(data: CallCreate): Promise<CallResponse> {
    return apiClient.post<CallResponse>("/calls/initiate", data);
  },

  // Join a call
  async joinCall(callId: string): Promise<CallResponse> {
    return apiClient.post<CallResponse>(`/calls/${callId}/join`, {});
  },

  // End a call
  async endCall(callId: string): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(`/calls/${callId}/end`, {});
  },

  // Get call info
  async getCall(callId: string): Promise<Call> {
    return apiClient.get<Call>(`/calls/${callId}`);
  },

  // Get active calls
  async getActiveCalls(): Promise<{ active_calls: Call[] }> {
    return apiClient.get<{ active_calls: Call[] }>("/calls/");
  },

  // Get call history
  async getCallHistory(
    skip = 0,
    limit = 50,
    conversationId?: string
  ): Promise<{ data: Call[]; count: number }> {
    const params: Record<string, unknown> = { skip, limit };
    if (conversationId) {
      params.conversation_id = conversationId;
    }
    return apiClient.get<{ data: Call[]; count: number }>(
      "/calls/history",
      params
    );
  },
};

/**
 * Devices API service
 */
export const devicesApi = {
  // Get user devices
  async getDevices(): Promise<{ data: Device[]; count: number }> {
    return apiClient.get<{ data: Device[]; count: number }>("/devices/");
  },

  // Register a device
  async registerDevice(data: DeviceCreate): Promise<Device> {
    return apiClient.post<Device>("/devices/", data);
  },

  // Get device by ID
  async getDevice(deviceId: string): Promise<Device> {
    return apiClient.get<Device>(`/devices/${deviceId}`);
  },

  // Update device
  async updateDevice(
    deviceId: string,
    data: Partial<DeviceCreate>
  ): Promise<Device> {
    return apiClient.patch<Device>(`/devices/${deviceId}`, data);
  },

  // Deactivate device
  async deactivateDevice(deviceId: string): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(
      `/devices/${deviceId}/deactivate`,
      {}
    );
  },

  // Delete device
  async deleteDevice(deviceId: string): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`/devices/${deviceId}`);
  },
};
