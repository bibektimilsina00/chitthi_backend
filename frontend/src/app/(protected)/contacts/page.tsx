"use client";

import { UserGroupIcon } from "@heroicons/react/24/outline";
import PlaceholderPage from "@/components/placeholder-page";

export default function ContactsPage() {
  return (
    <PlaceholderPage
      title="Contacts"
      description="Manage your contacts and discover new connections securely."
      icon={<UserGroupIcon className="w-12 h-12 text-gray-400" />}
    />
  );
}
