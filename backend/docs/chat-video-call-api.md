# 💬 Chat & Video Call API Documentation

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
  <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">Chat & Video Call API</h1>
  <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">Complete API reference for messaging and real-time communication</p>
</div>

---

## 📋 Table of Contents

- [**Chat Messaging API**](#-chat-messaging-api)
  - [Message Management](#message-management)
  - [Conversation Management](#conversation-management)
  - [Real-time Messaging](#real-time-messaging)
- [**Video & Audio Calls API**](#-video--audio-calls-api)
  - [Call Management](#call-management)
  - [WebRTC Signaling](#webrtc-signaling)
  - [Call History](#call-history)
- [**Data Types & Schemas**](#-data-types--schemas)
- [**WebSocket Events**](#-websocket-events)
- [**Error Codes**](#-error-codes)

---

## 💬 Chat Messaging API

### Message Management

#### **Get Messages**

```http
GET /api/v1/messages/
```

**Query Parameters:**

- `conversation_id` (UUID, required) - Conversation to retrieve messages from
- `skip` (int, default: 0) - Number of messages to skip for pagination
- `limit` (int, default: 100, max: 100) - Maximum messages to return

**Response:**

```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "conversation_id": "456e7890-e89b-12d3-a456-426614174001",
      "sender_id": "789e0123-e89b-12d3-a456-426614174002",
      "ciphertext": "encrypted_message_content",
      "ciphertext_nonce": "nonce_value",
      "encryption_algo": "aes-256-gcm",
      "message_type": "text",
      "preview_text_hash": "hash_for_notifications",
      "is_edited": false,
      "is_deleted": false,
      "created_at": "2025-09-08T10:30:00Z",
      "updated_at": "2025-09-08T10:30:00Z",
      "encrypted_keys": [
        {
          "recipient_user_id": "user_uuid",
          "recipient_device_id": "device_uuid",
          "encrypted_key": "encrypted_content_key",
          "key_algo": "x25519-aead",
          "nonce": "key_nonce"
        }
      ],
      "attachments": [
        {
          "id": "attachment_uuid",
          "file_name": "document.pdf",
          "file_size": 1024000,
          "content_type": "application/pdf",
          "storage_id": "storage_uuid"
        }
      ],
      "statuses": [
        {
          "user_id": "user_uuid",
          "status": "delivered",
          "status_at": "2025-09-08T10:30:05Z"
        }
      ]
    }
  ],
  "count": 25
}
```

#### **Send Message**

```http
POST /api/v1/messages/
```

**Request Body:**

```json
{
  "conversation_id": "456e7890-e89b-12d3-a456-426614174001",
  "ciphertext": "encrypted_message_content",
  "message_type": "text",
  "recipient_keys": [
    {
      "recipient_user_id": "user_uuid",
      "recipient_device_id": "device_uuid",
      "encrypted_key": "encrypted_content_key",
      "key_algo": "x25519-aead",
      "nonce": "key_nonce"
    }
  ],
  "attachments": [
    {
      "file_name": "image.jpg",
      "file_size": 512000,
      "content_type": "image/jpeg",
      "storage_id": "storage_uuid"
    }
  ]
}
```

**Message Types:**

- `text` - Plain text message
- `image` - Image attachment
- `audio` - Audio message/file
- `video` - Video file
- `document` - Document attachment
- `location` - Location sharing
- `contact` - Contact card
- `system` - System notification

### Conversation Management

#### **Get Conversations**

```http
GET /api/v1/conversations/
```

**Query Parameters:**

- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 100, max: 100) - Maximum conversations to return

**Response:**

```json
{
  "data": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "title": "Project Team Chat",
      "type": "group",
      "visibility": "private",
      "creator_id": "creator_uuid",
      "member_count": 4,
      "last_message_id": "last_message_uuid",
      "last_activity": "2025-09-08T10:30:00Z",
      "archived": false,
      "created_at": "2025-09-01T09:00:00Z",
      "updated_at": "2025-09-08T10:30:00Z"
    }
  ],
  "count": 12
}
```

#### **Create Conversation**

```http
POST /api/v1/conversations/
```

**Request Body:**

```json
{
  "title": "New Group Chat",
  "type": "group",
  "visibility": "private",
  "description": "Discussion about project updates",
  "participants": ["user_uuid_1", "user_uuid_2", "user_uuid_3"]
}
```

**Conversation Types:**

- `direct` - One-on-one conversation
- `group` - Group conversation (3+ members)
- `channel` - Broadcast channel
- `support` - Customer support conversation

#### **Add/Remove Members**

```http
POST /api/v1/conversations/{conversation_id}/members
DELETE /api/v1/conversations/{conversation_id}/members/{user_id}
```

### Real-time Messaging

#### **WebSocket Connection**

```javascript
const socket = new WebSocket('wss://api.example.com/api/v1/chat/ws/device_id?token=JWT_TOKEN');

// Authentication
socket.send(JSON.stringify({
  type: 'auth',
  token: 'jwt_token_here'
}));

// Join conversation
socket.send(JSON.stringify({
  type: 'join_conversation',
  conversation_id: 'conversation_uuid'
}));

// Send message
socket.send(JSON.stringify({
  type: 'send_message',
  conversation_id: 'conversation_uuid',
  ciphertext: 'encrypted_content',
  message_type: 'text',
  recipient_keys: [...]
}));
```

---

## 📞 Video & Audio Calls API

### Call Management

#### **Initiate Call**

```http
POST /api/v1/calls/initiate
```

**Request Body:**

```json
{
  "participants": ["user_uuid_1", "user_uuid_2"],
  "call_type": "video"
}
```

**Call Types:**

- `audio` - Voice-only call
- `video` - Video call with audio

**Response:**

```json
{
  "call_id": "call_uuid",
  "status": "initiated",
  "participants": ["caller_uuid", "user_uuid_1", "user_uuid_2"],
  "type": "video",
  "signaling_url": "/api/v1/calls/call_uuid/signaling"
}
```

#### **Join Call**

```http
POST /api/v1/calls/{call_id}/join
```

**Response:**

```json
{
  "call_id": "call_uuid",
  "status": "joined",
  "signaling_url": "/api/v1/calls/call_uuid/signaling"
}
```

#### **End Call**

```http
POST /api/v1/calls/{call_id}/end
```

**Response:**

```json
{
  "message": "Call ended"
}
```

#### **Get Call Info**

```http
GET /api/v1/calls/{call_id}
```

**Response:**

```json
{
  "id": "call_uuid",
  "caller_id": "caller_uuid",
  "participants": ["user1", "user2", "user3"],
  "type": "video",
  "status": "ongoing",
  "started_at": "2025-09-08T10:30:00Z",
  "ended_at": null
}
```

#### **Get Active Calls**

```http
GET /api/v1/calls/
```

**Response:**

```json
{
  "active_calls": [
    {
      "id": "call_uuid",
      "caller_id": "caller_uuid",
      "participants": ["user1", "user2"],
      "type": "video",
      "status": "ongoing",
      "started_at": "2025-09-08T10:30:00Z"
    }
  ]
}
```

### WebRTC Signaling

#### **WebSocket Signaling**

```javascript
const signalingWs = new WebSocket(
  "wss://api.example.com/api/v1/chat/ws/device_id?token=JWT_TOKEN"
);

// Send SDP Offer
signalingWs.send(
  JSON.stringify({
    type: "offer",
    sdp: "offer_sdp_here",
    user_id: "sender_uuid",
  })
);

// Send SDP Answer
signalingWs.send(
  JSON.stringify({
    type: "answer",
    sdp: "answer_sdp_here",
    user_id: "sender_uuid",
  })
);

// Send ICE Candidate
signalingWs.send(
  JSON.stringify({
    type: "ice-candidate",
    candidate: "ice_candidate_here",
    user_id: "sender_uuid",
  })
);

// Mute/Unmute
signalingWs.send(
  JSON.stringify({
    type: "mute",
    user_id: "sender_uuid",
    muted: true,
  })
);

// Toggle Video
signalingWs.send(
  JSON.stringify({
    type: "video_toggle",
    user_id: "sender_uuid",
    video_enabled: false,
  })
);
```

**Received Events:**

```javascript
signalingWs.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case "offer":
      // Handle incoming SDP offer
      break;
    case "answer":
      // Handle incoming SDP answer
      break;
    case "ice-candidate":
      // Handle incoming ICE candidate
      break;
    case "participant_muted":
      // Handle participant mute status
      break;
    case "participant_video":
      // Handle participant video status
      break;
  }
};
```

### Call History

#### **Get Call Logs**

```http
GET /api/v1/calls/history
```

**Query Parameters:**

- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 50, max: 100) - Maximum logs to return
- `conversation_id` (UUID, optional) - Filter by conversation

**Response:**

```json
{
  "data": [
    {
      "id": "log_uuid",
      "conversation_id": "conversation_uuid",
      "caller_id": "caller_uuid",
      "callee_id": "callee_uuid",
      "call_type": "video",
      "status": "ended",
      "started_at": "2025-09-08T10:30:00Z",
      "ended_at": "2025-09-08T10:45:00Z",
      "duration": 900,
      "call_metadata": {
        "quality": "good",
        "connection_type": "wifi",
        "bandwidth_avg": "2.5mbps"
      }
    }
  ],
  "count": 15
}
```

---

## 🗃️ Data Types & Schemas

### Message Schema

```typescript
interface Message {
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

type MessageType =
  | "text"
  | "image"
  | "audio"
  | "video"
  | "document"
  | "location"
  | "contact"
  | "system";

interface MessageEncryptedKey {
  recipient_user_id: string;
  recipient_device_id: string;
  encrypted_key: string;
  key_algo: string;
  nonce: string;
}

interface MessageAttachment {
  id: string;
  file_name: string;
  file_size: number;
  content_type: string;
  storage_id: string;
}

interface MessageStatus {
  user_id: string;
  device_id?: string;
  status: MessageStatusType;
  status_at: string;
}

type MessageStatusType = "sent" | "delivered" | "read" | "failed";
```

### Conversation Schema

```typescript
interface Conversation {
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

type ConversationType = "direct" | "group" | "channel" | "support";
type ConversationVisibility = "private" | "public" | "invite_only";

interface ConversationMember {
  id: string;
  conversation_id: string;
  user_id: string;
  role: MemberRole;
  joined_at: string;
  last_read_message_id?: string;
  unread_count: number;
  is_muted: boolean;
}

type MemberRole = "admin" | "moderator" | "member";
```

### Call Schema

```typescript
interface Call {
  id: string;
  caller_id: string;
  participants: string[];
  type: CallType;
  status: CallStatus;
  started_at: string;
  ended_at?: string;
}

type CallType = "audio" | "video";
type CallStatus =
  | "initiating"
  | "ringing"
  | "ongoing"
  | "ended"
  | "missed"
  | "declined"
  | "failed";

interface CallLog {
  id: string;
  conversation_id: string;
  caller_id: string;
  callee_id: string;
  call_type: CallType;
  status: CallStatus;
  started_at: string;
  ended_at?: string;
  duration?: number;
  call_metadata?: CallMetadata;
}

interface CallMetadata {
  quality?: "poor" | "fair" | "good" | "excellent";
  connection_type?: string;
  bandwidth_avg?: string;
  packet_loss?: number;
  latency_avg?: number;
}
```

---

## 📡 WebSocket Events

### Message Events

```typescript
// Incoming message
{
  type: 'message_received',
  data: {
    message: Message,
    conversation_id: string
  }
}

// Message status update
{
  type: 'message_status_update',
  data: {
    message_id: string,
    status: MessageStatusType,
    user_id: string
  }
}

// Typing indicator
{
  type: 'typing',
  data: {
    conversation_id: string,
    user_id: string,
    is_typing: boolean
  }
}

// User online status
{
  type: 'user_status',
  data: {
    user_id: string,
    status: 'online' | 'offline' | 'away' | 'busy',
    last_seen?: string
  }
}
```

### Call Events

```typescript
// Incoming call
{
  type: 'incoming_call',
  data: {
    call_id: string,
    caller_id: string,
    call_type: CallType,
    participants: string[]
  }
}

// Call status update
{
  type: 'call_status_update',
  data: {
    call_id: string,
    status: CallStatus,
    participant_id?: string
  }
}

// Participant joined/left
{
  type: 'participant_update',
  data: {
    call_id: string,
    user_id: string,
    action: 'joined' | 'left'
  }
}
```

---

## ⚠️ Error Codes

### HTTP Status Codes

| Code  | Description      | Common Causes                              |
| ----- | ---------------- | ------------------------------------------ |
| `400` | Bad Request      | Invalid request data, user already in call |
| `401` | Unauthorized     | Missing or invalid authentication token    |
| `403` | Forbidden        | Not authorized to access resource          |
| `404` | Not Found        | Call/conversation/message not found        |
| `409` | Conflict         | Duplicate operation, conflicting state     |
| `422` | Validation Error | Request data validation failed             |
| `429` | Rate Limited     | Too many requests                          |
| `500` | Internal Error   | Server error                               |

### WebSocket Close Codes

| Code   | Description            |
| ------ | ---------------------- |
| `4001` | Authentication Failed  |
| `4002` | Invalid Message Format |
| `4003` | Rate Limited           |
| `4004` | Resource Not Found     |
| `4005` | Permission Denied      |

### Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "extra_info": {
    "field": "Additional context"
  }
}
```

---

## 🔒 Security Considerations

### End-to-End Encryption

- All messages are encrypted client-side before sending
- Server never has access to plaintext message content
- Each message uses unique encryption keys
- Forward secrecy through key rotation

### Authentication

- Bearer token authentication for all API endpoints
- JWT tokens with expiration
- WebSocket authentication required before joining

### Rate Limiting

- Message sending: 60 messages per minute
- Call initiation: 10 calls per hour
- WebSocket connections: 5 per user

### Privacy

- Call metadata stored for quality improvement
- Message content never logged or stored in plaintext
- User location data encrypted when shared

---

## 🚀 Integration Examples

### JavaScript/TypeScript Client

```typescript
class ChatClient {
  private ws: WebSocket;
  private signalingWs: WebSocket;

  async sendMessage(conversationId: string, content: string) {
    const encrypted = await this.encryptMessage(content);

    const response = await fetch("/api/v1/messages/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        ciphertext: encrypted.ciphertext,
        message_type: "text",
        recipient_keys: encrypted.keys,
      }),
    });

    return response.json();
  }

  async initiateCall(participants: string[], type: "audio" | "video") {
    const response = await fetch("/api/v1/calls/initiate", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ participants, call_type: type }),
    });

    const callData = await response.json();
    this.setupSignaling(callData.call_id);
    return callData;
  }
}
```

### React Native Example

```typescript
import { WebRTCClient } from "./webrtc-client";

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [activeCall, setActiveCall] = useState(null);

  const sendMessage = async (text: string) => {
    const encrypted = await encryptMessage(text);
    // Send via API
  };

  const startVideoCall = async (userId: string) => {
    const call = await chatClient.initiateCall([userId], "video");
    setActiveCall(call);
    // Initialize WebRTC
  };

  return { messages, sendMessage, startVideoCall, activeCall };
};
```

This comprehensive API documentation covers all chat messaging and video call functionality in your E2E encrypted chat backend. The API supports modern real-time communication features with proper security and privacy considerations.
