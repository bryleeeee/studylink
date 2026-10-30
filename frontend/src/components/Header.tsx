"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export function Header() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();

  function handleLogout() {
    logout();
    router.push("/");
  }

  return (
    <header
      style={{
        padding: "1rem",
        borderBottom: "1px solid #e5e5e5",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <Link href="/" style={{ fontWeight: 600, fontSize: "1.1rem", textDecoration: "none" }}>
        StudyLink
      </Link>

      <nav style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        {loading ? null : user ? (
          <>
            <span style={{ color: "#666", fontSize: "0.9rem" }}>{user.email}</span>
            <button
              onClick={handleLogout}
              style={{ background: "none", border: "none", cursor: "pointer", font: "inherit", color: "inherit" }}
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <Link href="/login">Log in</Link>
            <Link href="/register">Register</Link>
          </>
        )}
      </nav>
    </header>
  );
}
