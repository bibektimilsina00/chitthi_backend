"use client";

import { PhoneIcon } from "@heroicons/react/24/outline";
import PlaceholderPage from "@/components/placeholder-page";

export default function CallsPage() {
  return (
    <PlaceholderPage
      title="Calls"
      description="Make secure voice and video calls with end-to-end encryption."
      icon={<PhoneIcon className="w-12 h-12 text-gray-400" />}
    />
  );
}
