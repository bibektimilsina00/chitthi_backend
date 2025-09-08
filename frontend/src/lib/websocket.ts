import { tokenManager } from "./token-manager";
import {
  WebSocketMessage,
  MessageReceivedEvent,
  MessageStatusUpdateEvent,
  TypingEvent,
  UserStatusEvent,
  MessageCreate,
} from "@/types/chat";

export type WebSocketEventType =
  | "message_received"
  | "message_status_update"
  | "typing"
  | "user_status"
  | "conversation_updated"
  | "incoming_call"
  | "call_status_update"
  | "participant_update";

export type WebSocketEventHandler = (event: WebSocketMessage) => void;

/**
 * WebSocket manager for real-time chat functionality
 */
class WebSocketManager {
  private ws: WebSocket | null = null;
  private eventHandlers: Map<WebSocketEventType, WebSocketEventHandler[]> =
    new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private isConnecting = false;
  private deviceId: string | null = null;
  private connectionListeners: ((connected: boolean) => void)[] = [];

  constructor() {
    // Initialize event handler maps
    this.eventHandlers = new Map();
  }

  /**
   * Connect to WebSocket server
   */
  async connect(deviceId: string): Promise<boolean> {
    if (this.isConnecting || this.isConnected()) {
      return true;
    }

    this.isConnecting = true;
    this.deviceId = deviceId;

    try {
      const token = tokenManager.getValidToken();
      if (!token) {
        throw new Error("No valid authentication token");
      }

      const baseUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
      const wsUrl = `${baseUrl}/api/v1/chat/ws/${deviceId}?token=${token}`;

      this.ws = new WebSocket(wsUrl);

      return new Promise((resolve, reject) => {
        if (!this.ws) {
          reject(new Error("Failed to create WebSocket"));
          return;
        }

        this.ws.onopen = () => {
          console.log("✅ WebSocket connected");
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          this.notifyConnectionListeners(true);
          resolve(true);
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };

        this.ws.onclose = (event) => {
          console.log("❌ WebSocket disconnected:", event.code, event.reason);
          this.isConnecting = false;
          this.notifyConnectionListeners(false);

          // Attempt to reconnect unless it's a permanent failure
          if (
            event.code !== 4001 &&
            this.reconnectAttempts < this.maxReconnectAttempts
          ) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error("🚨 WebSocket error:", error);
          this.isConnecting = false;
          reject(error);
        };

        // Timeout the connection attempt
        setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            reject(new Error("Connection timeout"));
          }
        }, 10000);
      });
    } catch (error) {
      this.isConnecting = false;
      console.error("Failed to connect WebSocket:", error);
      return false;
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, "User disconnected");
      this.ws = null;
    }
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
    this.notifyConnectionListeners(false);
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Send a message through WebSocket
   */
  send(message: WebSocketMessage): boolean {
    if (!this.isConnected()) {
      console.warn("Cannot send message: WebSocket not connected");
      return false;
    }

    try {
      this.ws!.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error("Failed to send WebSocket message:", error);
      return false;
    }
  }

  /**
   * Join a conversation
   */
  joinConversation(conversationId: string): boolean {
    return this.send({
      type: "join_conversation",
      data: { conversation_id: conversationId },
    });
  }

  /**
   * Leave a conversation
   */
  leaveConversation(conversationId: string): boolean {
    return this.send({
      type: "leave_conversation",
      data: { conversation_id: conversationId },
    });
  }

  /**
   * Send a message
   */
  sendMessage(messageData: MessageCreate): boolean {
    return this.send({
      type: "send_message",
      data: messageData,
    });
  }

  /**
   * Send typing indicator
   */
  sendTyping(conversationId: string, isTyping: boolean): boolean {
    return this.send({
      type: "typing",
      data: {
        conversation_id: conversationId,
        is_typing: isTyping,
      },
    });
  }

  /**
   * Update user status
   */
  updateStatus(status: "online" | "away" | "busy"): boolean {
    return this.send({
      type: "status_update",
      data: { status },
    });
  }

  /**
   * Add event listener for specific event types
   */
  addEventListener(
    eventType: WebSocketEventType,
    handler: WebSocketEventHandler
  ): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  /**
   * Remove event listener
   */
  removeEventListener(
    eventType: WebSocketEventType,
    handler: WebSocketEventHandler
  ): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Add connection status listener
   */
  addConnectionListener(listener: (connected: boolean) => void): void {
    this.connectionListeners.push(listener);
  }

  /**
   * Remove connection status listener
   */
  removeConnectionListener(listener: (connected: boolean) => void): void {
    const index = this.connectionListeners.indexOf(listener);
    if (index > -1) {
      this.connectionListeners.splice(index, 1);
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log("📨 WebSocket message received:", message.type);

      // Emit to specific event handlers
      const handlers = this.eventHandlers.get(
        message.type as WebSocketEventType
      );
      if (handlers) {
        handlers.forEach((handler) => {
          try {
            handler(message);
          } catch (error) {
            console.error(`Error in ${message.type} handler:`, error);
          }
        });
      }
    } catch (error) {
      console.error("Failed to parse WebSocket message:", error);
    }
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnection attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      30000
    );

    console.log(
      `🔄 Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`
    );

    setTimeout(() => {
      if (this.deviceId && !this.isConnected()) {
        console.log(
          `🔄 Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`
        );
        this.connect(this.deviceId);
      }
    }, delay);
  }

  /**
   * Notify connection listeners
   */
  private notifyConnectionListeners(connected: boolean): void {
    this.connectionListeners.forEach((listener) => {
      try {
        listener(connected);
      } catch (error) {
        console.error("Error in connection listener:", error);
      }
    });
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): {
    connected: boolean;
    connecting: boolean;
    reconnectAttempts: number;
  } {
    return {
      connected: this.isConnected(),
      connecting: this.isConnecting,
      reconnectAttempts: this.reconnectAttempts,
    };
  }
}

// Create and export singleton instance
export const webSocketManager = new WebSocketManager();

// Export types for external use
export type {
  WebSocketMessage,
  MessageReceivedEvent,
  MessageStatusUpdateEvent,
  TypingEvent,
  UserStatusEvent,
};
