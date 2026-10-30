import Link from "next/link";
import type { DocumentListItem } from "@/lib/api";

export function DocumentCard({ doc }: { doc: DocumentListItem }) {
  return (
    <Link
      href={`/documents/${doc.id}`}
      style={{
        display: "block",
        padding: "1rem",
        border: "1px solid #e5e5e5",
        borderRadius: 8,
        marginBottom: "0.75rem",
        textDecoration: "none",
      }}
    >
      <h3 style={{ margin: "0 0 0.25rem" }}>{doc.title}</h3>
      {doc.authors && doc.authors.length > 0 && (
        <p style={{ margin: "0 0 0.5rem", color: "#666", fontSize: "0.9rem" }}>
          {doc.authors.join(", ")}
        </p>
      )}
      {doc.summary_status === "done" && doc.summary ? (
        <p style={{ margin: 0, color: "#333" }}>{doc.summary}</p>
      ) : (
        <p style={{ margin: 0, color: "#999", fontStyle: "italic" }}>
          {doc.summary_status === "pending" ? "Summary generating…" : "Summary unavailable"}
        </p>
      )}
    </Link>
  );
}
