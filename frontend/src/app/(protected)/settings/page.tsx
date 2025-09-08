"use client";

import { Cog6ToothIcon } from "@heroicons/react/24/outline";
import PlaceholderPage from "@/components/placeholder-page";

export default function SettingsPage() {
  return (
    <PlaceholderPage
      title="Settings"
      description="Configure your account, privacy settings, and security preferences."
      icon={<Cog6ToothIcon className="w-12 h-12 text-gray-400" />}
    />
  );
}
