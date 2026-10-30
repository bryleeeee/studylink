"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type DocumentListItem } from "@/lib/api";
import { DocumentCard } from "@/components/DocumentCard";

export default function BrowsePage() {
  const [docs, setDocs] = useState<DocumentListItem[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load(q?: string) {
    setLoading(true);
    setError(null);
    try {
      setDocs(await api.browseDocuments({ q }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1 style={{ margin: 0 }}>Browse research</h1>
        <Link href="/upload" style={{ fontWeight: 600 }}>
          + Upload
        </Link>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          load(query || undefined);
        }}
        style={{ marginBottom: "1.5rem" }}
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title (semantic search lands in Phase 2)"
          style={{ width: "100%", padding: "0.6rem", borderRadius: 6, border: "1px solid #ccc" }}
        />
      </form>

      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {!loading && !error && docs.length === 0 && <p>No documents yet.</p>}
      {docs.map((doc) => (
        <DocumentCard key={doc.id} doc={doc} />
      ))}
    </div>
  );
}
