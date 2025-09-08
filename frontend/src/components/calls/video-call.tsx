"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  PhoneIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  SpeakerWaveIcon,
  XMarkIcon,
  PhoneXMarkIcon,
  VideoCameraSlashIcon,
} from "@heroicons/react/24/outline";
import { MicrophoneIcon as MicrophoneIconSolid } from "@heroicons/react/24/solid";
import { webrtcService, CallState, CallParticipant } from "@/lib/webrtc";

interface VideoCallProps {
  callId?: string | undefined;
  onClose: () => void;
}

export function VideoCall({ callId, onClose }: VideoCallProps) {
  const [callState, setCallState] = useState<CallState>(
    webrtcService.getCallState()
  );
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRefs = useRef<Map<string, HTMLVideoElement>>(new Map());

  useEffect(() => {
    // Set up state change listener
    webrtcService.setOnStateChange(setCallState);

    // Set up local video stream
    if (callState.localStream && localVideoRef.current) {
      localVideoRef.current.srcObject = callState.localStream;
    }

    return () => {
      // Cleanup when component unmounts
      if (!callState.isActive) {
        webrtcService.endCall();
      }
    };
  }, [callState.localStream, callState.isActive]);

  // Update remote video streams
  useEffect(() => {
    callState.participants.forEach((participant) => {
      if (participant.stream) {
        const videoElement = remoteVideoRefs.current.get(participant.userId);
        if (videoElement) {
          videoElement.srcObject = participant.stream;
        }
      }
    });
  }, [callState.participants]);

  const handleAcceptCall = async () => {
    if (callId && callState.isIncoming) {
      try {
        await webrtcService.acceptIncomingCall(callId, callState.callType);
      } catch (error) {
        console.error("Failed to accept call:", error);
      }
    }
  };

  const handleDeclineCall = async () => {
    if (callId && callState.isIncoming) {
      try {
        await webrtcService.declineIncomingCall(callId);
        onClose();
      } catch (error) {
        console.error("Failed to decline call:", error);
        onClose();
      }
    }
  };

  const handleEndCall = async () => {
    try {
      await webrtcService.endCall();
      onClose();
    } catch (error) {
      console.error("Failed to end call:", error);
      onClose();
    }
  };

  const handleToggleMute = async () => {
    try {
      await webrtcService.toggleMute();
    } catch (error) {
      console.error("Failed to toggle mute:", error);
    }
  };

  const handleToggleVideo = async () => {
    try {
      await webrtcService.toggleVideo();
    } catch (error) {
      console.error("Failed to toggle video:", error);
    }
  };

  const setRemoteVideoRef = (
    userId: string,
    element: HTMLVideoElement | null
  ) => {
    if (element) {
      remoteVideoRefs.current.set(userId, element);
    } else {
      remoteVideoRefs.current.delete(userId);
    }
  };

  // Incoming call screen
  if (callState.isIncoming) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center">
          <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-6">
            {callState.callType === "video" ? (
              <VideoCameraIcon className="w-12 h-12 text-white" />
            ) : (
              <PhoneIcon className="w-12 h-12 text-white" />
            )}
          </div>

          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Incoming {callState.callType} call
          </h2>

          <p className="text-gray-600 mb-8">
            {callState.participants[0]?.userId || "Unknown caller"}
          </p>

          <div className="flex justify-center space-x-4">
            <button
              onClick={handleDeclineCall}
              className="flex items-center justify-center w-16 h-16 bg-red-500 hover:bg-red-600 text-white rounded-full transition-colors"
              title="Decline call"
            >
              <PhoneXMarkIcon className="w-8 h-8" />
            </button>

            <button
              onClick={handleAcceptCall}
              className="flex items-center justify-center w-16 h-16 bg-green-500 hover:bg-green-600 text-white rounded-full transition-colors"
              title="Accept call"
            >
              <PhoneIcon className="w-8 h-8" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Active call screen
  return (
    <div className="fixed inset-0 bg-gray-900 flex flex-col z-50">
      {/* Header */}
      <div className="bg-gray-800 p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
            {callState.callType === "video" ? (
              <VideoCameraIcon className="w-4 h-4 text-white" />
            ) : (
              <PhoneIcon className="w-4 h-4 text-white" />
            )}
          </div>
          <div>
            <h2 className="text-white font-medium">
              {callState.callType === "video" ? "Video Call" : "Voice Call"}
            </h2>
            <p className="text-gray-400 text-sm">
              {callState.participants.length + 1} participants
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-full transition-colors"
          title="Minimize"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Video Grid */}
      <div className="flex-1 p-4">
        {callState.callType === "video" ? (
          <div className="h-full grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {/* Local video */}
            <div className="relative bg-gray-800 rounded-lg overflow-hidden">
              <video
                ref={localVideoRef}
                autoPlay
                muted
                playsInline
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                You {callState.isMuted && "(muted)"}
              </div>
              {!callState.isVideoEnabled && (
                <div className="absolute inset-0 bg-gray-700 flex items-center justify-center">
                  <VideoCameraSlashIcon className="w-12 h-12 text-gray-400" />
                </div>
              )}
            </div>

            {/* Remote videos */}
            {callState.participants.map((participant) => (
              <RemoteVideo
                key={participant.userId}
                participant={participant}
                onVideoRef={(element) =>
                  setRemoteVideoRef(participant.userId, element)
                }
              />
            ))}
          </div>
        ) : (
          /* Audio call interface */
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-4xl">
                {/* Local user */}
                <div className="flex flex-col items-center">
                  <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center mb-4">
                    <span className="text-white text-2xl font-semibold">
                      You
                    </span>
                  </div>
                  <p className="text-white font-medium">You</p>
                  {callState.isMuted && (
                    <p className="text-red-400 text-sm">(muted)</p>
                  )}
                </div>

                {/* Remote participants */}
                {callState.participants.map((participant) => (
                  <div
                    key={participant.userId}
                    className="flex flex-col items-center"
                  >
                    <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center mb-4">
                      <span className="text-white text-xl font-semibold">
                        {participant.userId.slice(0, 2).toUpperCase()}
                      </span>
                    </div>
                    <p className="text-white font-medium">
                      {participant.userId}
                    </p>
                    {participant.isMuted && (
                      <p className="text-red-400 text-sm">(muted)</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="bg-gray-800 p-6">
        <div className="flex items-center justify-center space-x-4">
          {/* Mute button */}
          <button
            onClick={handleToggleMute}
            className={`flex items-center justify-center w-12 h-12 rounded-full transition-colors ${
              callState.isMuted
                ? "bg-red-500 hover:bg-red-600 text-white"
                : "bg-gray-600 hover:bg-gray-700 text-white"
            }`}
            title={callState.isMuted ? "Unmute" : "Mute"}
          >
            {callState.isMuted ? (
              <MicrophoneIconSolid className="w-6 h-6" />
            ) : (
              <MicrophoneIcon className="w-6 h-6" />
            )}
          </button>

          {/* Video toggle button (only for video calls) */}
          {callState.callType === "video" && (
            <button
              onClick={handleToggleVideo}
              className={`flex items-center justify-center w-12 h-12 rounded-full transition-colors ${
                !callState.isVideoEnabled
                  ? "bg-red-500 hover:bg-red-600 text-white"
                  : "bg-gray-600 hover:bg-gray-700 text-white"
              }`}
              title={
                callState.isVideoEnabled ? "Turn off video" : "Turn on video"
              }
            >
              {callState.isVideoEnabled ? (
                <VideoCameraIcon className="w-6 h-6" />
              ) : (
                <VideoCameraSlashIcon className="w-6 h-6" />
              )}
            </button>
          )}

          {/* Speaker button */}
          <button
            className="flex items-center justify-center w-12 h-12 bg-gray-600 hover:bg-gray-700 text-white rounded-full transition-colors"
            title="Speaker"
          >
            <SpeakerWaveIcon className="w-6 h-6" />
          </button>

          {/* End call button */}
          <button
            onClick={handleEndCall}
            className="flex items-center justify-center w-12 h-12 bg-red-500 hover:bg-red-600 text-white rounded-full transition-colors"
            title="End call"
          >
            <PhoneXMarkIcon className="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  );
}

interface RemoteVideoProps {
  participant: CallParticipant;
  onVideoRef: (element: HTMLVideoElement | null) => void;
}

function RemoteVideo({ participant, onVideoRef }: RemoteVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      onVideoRef(videoRef.current);
      if (participant.stream) {
        videoRef.current.srcObject = participant.stream;
      }
    }

    return () => {
      onVideoRef(null);
    };
  }, [participant.stream, onVideoRef]);

  return (
    <div className="relative bg-gray-800 rounded-lg overflow-hidden">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full h-full object-cover"
      />
      <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
        {participant.userId.slice(0, 20)}
        {participant.isMuted && " (muted)"}
      </div>
      {!participant.isVideoEnabled && (
        <div className="absolute inset-0 bg-gray-700 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center mb-2 mx-auto">
              <span className="text-white text-lg font-semibold">
                {participant.userId.slice(0, 2).toUpperCase()}
              </span>
            </div>
            <p className="text-gray-300 text-sm">{participant.userId}</p>
          </div>
        </div>
      )}
    </div>
  );
}
