import type { Metadata } from "next";
import type { ReactNode } from "react";
import { NavHeader } from "@/components/nav-header";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sanchai (सञ्चै) — Clinical Health Ledger",
  description: "Zero-hallucination bilingual Nepali clinical intake and longitudinal health ledger."
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <NavHeader />
        {children}
      </body>
    </html>
  );
}