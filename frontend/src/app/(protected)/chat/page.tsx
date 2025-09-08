"use client";

import { ChatInterface } from "@/components/chat/chat-interface";
import { useAuth, useAuthActions } from "@/hooks/use-auth";
import Button from "@/components/ui/button";

export default function ChatPage() {
  const { user } = useAuth();
  const { logout } = useAuthActions();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Top navigation bar */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-full px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between items-center">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Chitthi</h1>
              <span className="ml-2 text-sm text-gray-500">
                Secure Messaging
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user?.display_name || user?.username}
              </span>
              <Button variant="outline" onClick={handleLogout}>
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat interface */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}
