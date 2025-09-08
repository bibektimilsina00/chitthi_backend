"use client";

import { useAuth, useAuthActions } from "@/hooks/use-auth";
import Button from "@/components/ui/button";
import Link from "next/link";
import {
  ChatBubbleLeftRightIcon,
  UserGroupIcon,
  PhoneIcon,
  Cog6ToothIcon,
} from "@heroicons/react/24/outline";

export default function DashboardPage() {
  const { user } = useAuth();
  const { logout } = useAuthActions();

  const handleLogout = () => {
    logout();
  };

  const features = [
    {
      name: "Messages",
      description: "Start secure, end-to-end encrypted conversations",
      href: "/chat",
      icon: ChatBubbleLeftRightIcon,
      color: "bg-blue-500",
    },
    {
      name: "Contacts",
      description: "Manage your contacts and connections",
      href: "/contacts",
      icon: UserGroupIcon,
      color: "bg-green-500",
    },
    {
      name: "Calls",
      description: "Make secure voice and video calls",
      href: "/calls",
      icon: PhoneIcon,
      color: "bg-purple-500",
    },
    {
      name: "Settings",
      description: "Configure your account and privacy settings",
      href: "/settings",
      icon: Cog6ToothIcon,
      color: "bg-gray-500",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between items-center">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Chitthi Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.display_name || user?.username}!
              </span>
              <Button variant="outline" onClick={handleLogout}>
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome section */}
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                🎉 Welcome to Chitthi!
              </h2>
              <p className="text-gray-600 mb-6">
                Your secure, end-to-end encrypted messaging platform is ready to
                use.
              </p>

              {/* Quick action */}
              <Link href="/chat">
                <Button className="inline-flex items-center">
                  <ChatBubbleLeftRightIcon className="w-4 h-4 mr-2" />
                  Start Messaging
                </Button>
              </Link>
            </div>
          </div>

          {/* Features grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {features.map((feature) => (
              <Link
                key={feature.name}
                href={feature.href}
                className="group bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center space-x-4">
                  <div className={`${feature.color} rounded-lg p-3`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 group-hover:text-blue-600">
                      {feature.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* User information */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4">Account Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    User ID
                  </label>
                  <p className="text-sm text-gray-900 font-mono">{user?.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Username
                  </label>
                  <p className="text-sm text-gray-900">{user?.username}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Email
                  </label>
                  <p className="text-sm text-gray-900">
                    {user?.email || "Not provided"}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Display Name
                  </label>
                  <p className="text-sm text-gray-900">
                    {user?.display_name || "Not provided"}
                  </p>
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Account Status
                  </label>
                  <p className="text-sm text-gray-900">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user?.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {user?.is_active ? "Active" : "Inactive"}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Account Type
                  </label>
                  <p className="text-sm text-gray-900">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user?.is_superuser
                          ? "bg-purple-100 text-purple-800"
                          : "bg-blue-100 text-blue-800"
                      }`}
                    >
                      {user?.is_superuser ? "Admin" : "User"}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Member Since
                  </label>
                  <p className="text-sm text-gray-900">
                    {user?.created_at
                      ? new Date(user.created_at).toLocaleDateString()
                      : "Unknown"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
