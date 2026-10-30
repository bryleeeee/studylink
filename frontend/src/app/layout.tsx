import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "StudyLink",
  description: "Upload, summarize, and discover student research.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Header />
          <main style={{ maxWidth: 960, margin: "0 auto", padding: "1.5rem" }}>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
