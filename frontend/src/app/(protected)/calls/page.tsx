"use client";

import { useState } from "react";
import { PhoneIcon, VideoCameraIcon } from "@heroicons/react/24/outline";
import { VideoCall } from "@/components/calls/video-call";
import { useCalls } from "@/hooks/use-calls";

// Import development auth token
import "@/lib/dev-auth";

export default function CallsPage() {
  const [showVideoCall, setShowVideoCall] = useState(false);
  const [participants, setParticipants] = useState("");

  const {
    callState,
    isCallActive,
    isIncomingCall,
    initiateCall,
    error: callError,
    clearError: clearCallError,
  } = useCalls();

  const handleInitiateCall = async (callType: "audio" | "video") => {
    try {
      clearCallError();
      const participantList = participants
        .split(",")
        .map((p) => p.trim())
        .filter((p) => p.length > 0);

      if (participantList.length === 0) {
        alert("Please enter at least one participant");
        return;
      }

      await initiateCall(participantList, callType);
      setShowVideoCall(true);
    } catch (error) {
      console.error(`Failed to initiate ${callType} call:`, error);
    }
  };

  const handleCloseCall = () => {
    setShowVideoCall(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
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

      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <PhoneIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Calls</h1>
            <p className="text-gray-600">
              Make secure voice and video calls with end-to-end encryption.
            </p>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Participants (User IDs, comma-separated)
              </label>
              <textarea
                value={participants}
                onChange={(e) => setParticipants(e.target.value)}
                placeholder="Enter user IDs: user1, user2, user3..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter the user IDs of people you want to call
              </p>
            </div>

            <div className="flex justify-center space-x-4">
              <button
                onClick={() => handleInitiateCall("audio")}
                disabled={!participants.trim()}
                className="flex items-center px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PhoneIcon className="w-5 h-5 mr-2" />
                Start Voice Call
              </button>

              <button
                onClick={() => handleInitiateCall("video")}
                disabled={!participants.trim()}
                className="flex items-center px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <VideoCameraIcon className="w-5 h-5 mr-2" />
                Start Video Call
              </button>
            </div>
          </div>

          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Demo Instructions
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <ul className="list-disc list-inside space-y-1">
                    <li>
                      Enter participant user IDs (you can use test IDs for demo)
                    </li>
                    <li>
                      Click either &ldquo;Start Voice Call&rdquo; or
                      &ldquo;Start Video Call&rdquo;
                    </li>
                    <li>
                      The call interface will open with local video/audio
                      controls
                    </li>
                    <li>
                      For testing, you can use IDs like: test-user-1,
                      test-user-2
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
