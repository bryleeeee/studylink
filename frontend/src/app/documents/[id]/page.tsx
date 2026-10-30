"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type DocumentDetail } from "@/lib/api";

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getDocument(params.id)
      .then(setDoc)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load document"));
  }, [params.id]);

  if (error) return <p style={{ color: "crimson" }}>{error}</p>;
  if (!doc) return <p>Loading…</p>;

  return (
    <article>
      <h1>{doc.title}</h1>
      {doc.authors && doc.authors.length > 0 && <p style={{ color: "#666" }}>{doc.authors.join(", ")}</p>}
      {doc.field && (
        <span
          style={{
            display: "inline-block",
            padding: "0.15rem 0.6rem",
            background: "#eee",
            borderRadius: 999,
            fontSize: "0.85rem",
            marginBottom: "1rem",
          }}
        >
          {doc.field}
        </span>
      )}

      <section style={{ margin: "1.5rem 0" }}>
        <h2 style={{ fontSize: "1rem", textTransform: "uppercase", color: "#888" }}>Summary</h2>
        {doc.summary_status === "done" && doc.summary ? (
          <p>{doc.summary}</p>
        ) : (
          <p style={{ color: "#999", fontStyle: "italic" }}>
            {doc.summary_status === "pending" ? "Summary is being generated." : "Summary unavailable."}
          </p>
        )}
      </section>

      <section>
        <h2 style={{ fontSize: "1rem", textTransform: "uppercase", color: "#888" }}>Related research</h2>
        <p style={{ color: "#999", fontStyle: "italic" }}>Semantic related-research suggestions arrive in Phase 2.</p>
      </section>
    </article>
  );
}
