import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SEO Audit Tool",
  description: "Audit any URL for on-page SEO issues.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">
        <header className="border-b border-hairline bg-surface">
          <div className="mx-auto max-w-3xl px-6 py-5">
            <h1 className="text-lg font-semibold tracking-tight text-slate-900">
              SEO Audit Tool
            </h1>
            <p className="mt-0.5 text-sm text-slate-500">
              Check any page for on-page SEO, performance, and accessibility
              issues.
            </p>
          </div>
        </header>

        <main className="mx-auto max-w-3xl px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
