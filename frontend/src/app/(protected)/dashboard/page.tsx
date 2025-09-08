"use client";

import { useAuth, useAuthActions } from "@/hooks/use-auth";
import Button from "@/components/ui/button";

export default function DashboardPage() {
  const { user } = useAuth();
  const { logout } = useAuthActions();

  const handleLogout = () => {
    logout();
  };

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
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                🎉 Welcome to Chitthi!
              </h2>
              <p className="text-gray-600 mb-6">
                Your authentication system is working perfectly.
              </p>
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="text-lg font-semibold mb-4">
                  User Information:
                </h3>
                <div className="text-left space-y-2">
                  <p>
                    <strong>ID:</strong> {user?.id}
                  </p>
                  <p>
                    <strong>Username:</strong> {user?.username}
                  </p>
                  <p>
                    <strong>Email:</strong> {user?.email || "Not provided"}
                  </p>
                  <p>
                    <strong>Display Name:</strong>{" "}
                    {user?.display_name || "Not provided"}
                  </p>
                  <p>
                    <strong>Account Status:</strong>{" "}
                    {user?.is_active ? "Active" : "Inactive"}
                  </p>
                  <p>
                    <strong>Account Type:</strong>{" "}
                    {user?.is_superuser ? "Admin" : "User"}
                  </p>
                  <p>
                    <strong>Created:</strong>{" "}
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
