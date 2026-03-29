import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CostIQ — AI Enterprise Cost Intelligence",
  description:
    "Four autonomous AI agents that find cost leakage and plug it — with board-ready math on every dollar saved. Enterprise-grade cost intelligence platform.",
  keywords: ["AI", "cost intelligence", "enterprise", "autonomous agents", "financial optimization"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
