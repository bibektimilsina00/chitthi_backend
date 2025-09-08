import { callsApi } from "./chat-api";
import { tokenManager } from "./token-manager";

export interface SignalingMessage {
  type: string;
  user_id?: string | undefined;
  sdp?: string | undefined;
  candidate?: RTCIceCandidate | undefined;
  muted?: boolean | undefined;
  video_enabled?: boolean | undefined;
  [key: string]: unknown;
}

export interface WebRTCConfig {
  iceServers: RTCIceServer[];
}

export interface CallParticipant {
  userId: string;
  stream?: MediaStream | undefined;
  peerConnection?: RTCPeerConnection | undefined;
  isMuted?: boolean | undefined;
  isVideoEnabled?: boolean | undefined;
}

export interface CallState {
  callId?: string | undefined;
  isActive: boolean;
  isIncoming: boolean;
  participants: CallParticipant[];
  localStream?: MediaStream | undefined;
  callType: "audio" | "video";
  isMuted: boolean;
  isVideoEnabled: boolean;
}

export class WebRTCService {
  private ws?: WebSocket | undefined;
  private signalingSocket?: WebSocket | null;
  private localStream?: MediaStream | undefined;
  private peerConnections: Map<string, RTCPeerConnection> = new Map();
  private config: WebRTCConfig;
  private callState: CallState = {
    isActive: false,
    isIncoming: false,
    participants: [],
    callType: "audio",
    isMuted: false,
    isVideoEnabled: false,
  };
  private onStateChange?: ((state: CallState) => void) | undefined;

  constructor(config?: Partial<WebRTCConfig>) {
    this.config = {
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" },
        { urls: "stun:stun2.l.google.com:19302" },
        { urls: "stun:stun3.l.google.com:19302" },
        { urls: "stun:stun4.l.google.com:19302" },
      ],
      ...config,
    };
  }

  setOnStateChange(callback: (state: CallState) => void) {
    this.onStateChange = callback;
  }

  private updateState(updates: Partial<CallState>) {
    this.callState = { ...this.callState, ...updates };
    console.log("WebRTC state updated:", this.callState);
    this.onStateChange?.(this.callState);
  }

  async initiateCall(
    participants: string[],
    callType: "audio" | "video" = "audio"
  ): Promise<string> {
    try {
      console.log(
        "Initiating call with participants:",
        participants,
        "type:",
        callType
      );

      // Get user media
      await this.getLocalStream(callType === "video");

      // Call backend API to initiate call
      const response = await callsApi.initiateCall({
        participants,
        call_type: callType,
      });

      console.log("Call initiated successfully:", response);

      this.updateState({
        callId: response.call_id,
        isActive: true,
        isIncoming: false,
        callType,
        isVideoEnabled: callType === "video",
      });

      // Connect to signaling WebSocket
      await this.connectSignaling(response.call_id);

      return response.call_id;
    } catch (error) {
      console.error("Failed to initiate call:", error);
      throw error;
    }
  }

  async joinCall(callId: string): Promise<void> {
    try {
      // Call backend API to join call
      await callsApi.joinCall(callId);

      // Get user media
      await this.getLocalStream(this.callState.callType === "video");

      this.updateState({
        callId,
        isActive: true,
        isIncoming: false,
      });

      // Connect to signaling WebSocket
      await this.connectSignaling(callId);
    } catch (error) {
      console.error("Failed to join call:", error);
      throw error;
    }
  }

  async endCall(): Promise<void> {
    try {
      if (this.callState.callId) {
        await callsApi.endCall(this.callState.callId);
      }

      this.cleanup();
      this.updateState({
        isActive: false,
        isIncoming: false,
        participants: [],
      });
    } catch (error) {
      console.error("Failed to end call:", error);
      this.cleanup();
    }
  }

  async acceptIncomingCall(
    callId: string,
    callType: "audio" | "video"
  ): Promise<void> {
    this.updateState({
      callType,
      isVideoEnabled: callType === "video",
    });
    await this.joinCall(callId);
  }

  async declineIncomingCall(callId: string): Promise<void> {
    try {
      // For now, just end the call - could add a specific decline endpoint
      await callsApi.endCall(callId);
      this.updateState({
        isActive: false,
        isIncoming: false,
      });
    } catch (error) {
      console.error("Failed to decline call:", error);
    }
  }

  async toggleMute(): Promise<void> {
    if (this.localStream) {
      const audioTrack = this.localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        const isMuted = !audioTrack.enabled;

        this.updateState({ isMuted });

        // Get current user ID from token
        const tokenPayload = tokenManager.getTokenPayload();
        const userId = (tokenPayload?.sub as string) || "current_user";

        // Send mute status to other participants
        this.sendSignalingMessage({
          type: "mute",
          user_id: userId,
          muted: isMuted,
        });
      }
    }
  }

  async toggleVideo(): Promise<void> {
    if (this.localStream) {
      const videoTrack = this.localStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        const isVideoEnabled = videoTrack.enabled;

        this.updateState({ isVideoEnabled });

        // Get current user ID from token
        const tokenPayload = tokenManager.getTokenPayload();
        const userId = (tokenPayload?.sub as string) || "current_user";

        // Send video status to other participants
        this.sendSignalingMessage({
          type: "video_toggle",
          user_id: userId,
          video_enabled: isVideoEnabled,
        });
      }
    }
  }

  private async getLocalStream(includeVideo: boolean = false): Promise<void> {
    try {
      console.log("Requesting user media, includeVideo:", includeVideo);

      const constraints: MediaStreamConstraints = {
        audio: true,
        video: includeVideo
          ? {
              width: { ideal: 1280 },
              height: { ideal: 720 },
              frameRate: { ideal: 30 },
            }
          : false,
      };

      console.log("Media constraints:", constraints);

      this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log("Local stream obtained:", this.localStream);

      this.updateState({ localStream: this.localStream });
    } catch (error) {
      console.error("Failed to get user media:", error);
      throw error;
    }
  }

  private async connectSignaling(callId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // Use the same base URL as the API client but with ws protocol
      const baseUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000/api/v1";
      const wsUrl = baseUrl
        .replace("http://", "ws://")
        .replace("https://", "wss://");

      this.signalingSocket = new WebSocket(
        `${wsUrl}/calls/${callId}/signaling`
      );

      this.signalingSocket.onopen = () => {
        console.log("Signaling WebSocket connected");
        resolve();
      };

      this.signalingSocket.onclose = (event) => {
        console.log("Signaling WebSocket closed:", event.code, event.reason);
        this.signalingSocket = null;
      };

      this.signalingSocket.onerror = (error) => {
        console.error("Signaling WebSocket error:", error);
        reject(error);
      };

      this.signalingSocket.onmessage = (event: MessageEvent) => {
        try {
          const message = JSON.parse(event.data) as SignalingMessage;
          this.handleSignalingMessage(message);
        } catch (error) {
          console.error("Error parsing signaling message:", error);
        }
      };
    });
  }

  private async handleSignalingMessage(
    message: SignalingMessage
  ): Promise<void> {
    const { type, user_id, ...data } = message;

    if (!user_id) {
      console.warn("Received signaling message without user_id");
      return;
    }

    switch (type) {
      case "offer":
        if (data.sdp) {
          await this.handleOffer(user_id, data.sdp);
        }
        break;
      case "answer":
        if (data.sdp) {
          await this.handleAnswer(user_id, data.sdp);
        }
        break;
      case "ice-candidate":
        if (data.candidate) {
          await this.handleIceCandidate(user_id, data.candidate);
        }
        break;
      case "participant_muted":
        if (typeof data.muted === "boolean") {
          this.handleParticipantMuted(user_id, data.muted);
        }
        break;
      case "participant_video":
        if (typeof data.video_enabled === "boolean") {
          this.handleParticipantVideo(user_id, data.video_enabled);
        }
        break;
      default:
        console.log("Unknown signaling message type:", type);
    }
  }

  private async handleOffer(userId: string, sdp: string): Promise<void> {
    const peerConnection = this.getOrCreatePeerConnection(userId);

    await peerConnection.setRemoteDescription(
      new RTCSessionDescription({
        type: "offer",
        sdp,
      })
    );

    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);

    // Get current user ID from token
    const tokenPayload = tokenManager.getTokenPayload();
    const currentUserId = (tokenPayload?.sub as string) || "current_user";

    this.sendSignalingMessage({
      type: "answer",
      user_id: currentUserId,
      sdp: answer.sdp,
    });
  }

  private async handleAnswer(userId: string, sdp: string): Promise<void> {
    const peerConnection = this.peerConnections.get(userId);
    if (peerConnection) {
      await peerConnection.setRemoteDescription(
        new RTCSessionDescription({
          type: "answer",
          sdp,
        })
      );
    }
  }

  private async handleIceCandidate(
    userId: string,
    candidate: RTCIceCandidate
  ): Promise<void> {
    const peerConnection = this.peerConnections.get(userId);
    if (peerConnection) {
      await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    }
  }

  private handleParticipantMuted(userId: string, muted: boolean): void {
    const participants = this.callState.participants.map((p) =>
      p.userId === userId ? { ...p, isMuted: muted } : p
    );
    this.updateState({ participants });
  }

  private handleParticipantVideo(userId: string, videoEnabled: boolean): void {
    const participants = this.callState.participants.map((p) =>
      p.userId === userId ? { ...p, isVideoEnabled: videoEnabled } : p
    );
    this.updateState({ participants });
  }

  private getOrCreatePeerConnection(userId: string): RTCPeerConnection {
    let peerConnection = this.peerConnections.get(userId);

    if (!peerConnection) {
      peerConnection = new RTCPeerConnection(this.config);
      this.peerConnections.set(userId, peerConnection);

      // Add local stream to peer connection
      if (this.localStream) {
        this.localStream.getTracks().forEach((track) => {
          peerConnection!.addTrack(track, this.localStream!);
        });
      }

      // Handle remote stream
      peerConnection.ontrack = (event) => {
        const [remoteStream] = event.streams;
        const participants = this.callState.participants.map((p) =>
          p.userId === userId ? { ...p, stream: remoteStream } : p
        );

        // Add participant if not exists
        if (!participants.find((p) => p.userId === userId)) {
          participants.push({
            userId,
            stream: remoteStream,
            peerConnection,
          });
        }

        this.updateState({ participants });
      };

      // Handle ICE candidates
      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          // Get current user ID from token
          const tokenPayload = tokenManager.getTokenPayload();
          const currentUserId = (tokenPayload?.sub as string) || "current_user";

          this.sendSignalingMessage({
            type: "ice-candidate",
            user_id: currentUserId,
            candidate: event.candidate,
          });
        }
      };

      // Handle connection state changes
      peerConnection.onconnectionstatechange = () => {
        console.log(
          `Peer connection state for ${userId}:`,
          peerConnection!.connectionState
        );
      };
    }

    return peerConnection;
  }

  private sendSignalingMessage(message: SignalingMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private cleanup(): void {
    // Stop local stream
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = undefined;
    }

    // Close peer connections
    this.peerConnections.forEach((pc) => pc.close());
    this.peerConnections.clear();

    // Close WebSocket
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  getCallState(): CallState {
    return this.callState;
  }

  // Handle incoming call notification (would be called from WebSocket chat service)
  handleIncomingCall(
    callId: string,
    callerId: string,
    callType: "audio" | "video"
  ): void {
    console.log("🔔 WebRTC: handleIncomingCall called with:", {
      callId,
      callerId,
      callType,
    });
    this.updateState({
      callId,
      isIncoming: true,
      callType,
      isVideoEnabled: callType === "video",
      participants: [{ userId: callerId }],
    });
    console.log("🔔 WebRTC: State updated, new state:", this.callState);
  }
}

// Create and export singleton instance
export const webrtcService = new WebRTCService();
