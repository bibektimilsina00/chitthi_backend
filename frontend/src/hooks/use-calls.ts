"use client";

import { useState, useEffect, useCallback } from "react";
import { webrtcService, CallState } from "@/lib/webrtc";

export interface UseCallsReturn {
  callState: CallState;
  isCallActive: boolean;
  isIncomingCall: boolean;
  initiateCall: (
    participants: string[],
    type: "audio" | "video"
  ) => Promise<string>;
  acceptCall: (callId: string, type: "audio" | "video") => Promise<void>;
  declineCall: (callId: string) => Promise<void>;
  endCall: () => Promise<void>;
  toggleMute: () => Promise<void>;
  toggleVideo: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

export function useCalls(): UseCallsReturn {
  const [callState, setCallState] = useState<CallState>(
    webrtcService.getCallState()
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Set up WebRTC service state change listener
    webrtcService.setOnStateChange(setCallState);

    return () => {
      // Clean up on unmount
      webrtcService.setOnStateChange(() => {});
    };
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const initiateCall = useCallback(
    async (participants: string[], type: "audio" | "video") => {
      try {
        setError(null);
        const callId = await webrtcService.initiateCall(participants, type);
        return callId;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to initiate call";
        setError(errorMessage);
        throw new Error(errorMessage);
      }
    },
    []
  );

  const acceptCall = useCallback(
    async (callId: string, type: "audio" | "video") => {
      try {
        setError(null);
        await webrtcService.acceptIncomingCall(callId, type);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to accept call";
        setError(errorMessage);
        throw new Error(errorMessage);
      }
    },
    []
  );

  const declineCall = useCallback(async (callId: string) => {
    try {
      setError(null);
      await webrtcService.declineIncomingCall(callId);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to decline call";
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const endCall = useCallback(async () => {
    try {
      setError(null);
      await webrtcService.endCall();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to end call";
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const toggleMute = useCallback(async () => {
    try {
      setError(null);
      await webrtcService.toggleMute();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to toggle mute";
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const toggleVideo = useCallback(async () => {
    try {
      setError(null);
      await webrtcService.toggleVideo();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to toggle video";
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  return {
    callState,
    isCallActive: callState.isActive,
    isIncomingCall: callState.isIncoming,
    initiateCall,
    acceptCall,
    declineCall,
    endCall,
    toggleMute,
    toggleVideo,
    error,
    clearError,
  };
}

// Hook for handling incoming call notifications from WebSocket
export function useIncomingCalls() {
  const [incomingCall, setIncomingCall] = useState<{
    callId: string;
    callerId: string;
    callType: "audio" | "video";
  } | null>(null);

  const handleIncomingCall = useCallback(
    (callId: string, callerId: string, callType: "audio" | "video") => {
      console.log("🎯 useIncomingCalls: handleIncomingCall called with:", {
        callId,
        callerId,
        callType,
      });
      setIncomingCall({ callId, callerId, callType });
      console.log(
        "🎯 useIncomingCalls: Calling webrtcService.handleIncomingCall"
      );
      webrtcService.handleIncomingCall(callId, callerId, callType);
      console.log(
        "🎯 useIncomingCalls: webrtcService.handleIncomingCall completed"
      );
    },
    []
  );

  const clearIncomingCall = useCallback(() => {
    setIncomingCall(null);
  }, []);

  return {
    incomingCall,
    handleIncomingCall,
    clearIncomingCall,
  };
}
