import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Auditly — Audit any website's SEO in seconds",
  description: "Enter a URL and get a clear, actionable SEO report across 20+ checks.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-canvas font-sans text-ink antialiased">
        {children}
      </body>
    </html>
  );
}
