import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SWRConfig } from "swr";
import ErrorBoundary from "@/components/ui/error-boundary";
import { LoadingProvider } from "@/providers/loading-provider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Chitthi - Secure Messaging",
  description: "End-to-end encrypted messaging platform",
  keywords: ["messaging", "chat", "encryption", "secure", "privacy"],
  authors: [{ name: "Chitthi Team" }],
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ErrorBoundary>
          <LoadingProvider>
            <SWRConfig
              value={{
                revalidateOnFocus: false,
                revalidateOnReconnect: true,
                shouldRetryOnError: false,
                dedupingInterval: 60000, // 1 minute
                errorRetryCount: 3,
                errorRetryInterval: 5000, // 5 seconds
              }}
            >
              {children}
            </SWRConfig>
          </LoadingProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
