"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function UploadPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [title, setTitle] = useState("");
  const [authors, setAuthors] = useState("");
  const [field, setField] = useState("");
  const [visibility, setVisibility] = useState<"public" | "private">("private");
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [loading, user, router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Choose a PDF to upload.");
      return;
    }
    setSubmitting(true);
    setError(null);

    const formData = new FormData();
    formData.append("title", title);
    if (authors) formData.append("authors", authors);
    if (field) formData.append("field", field);
    formData.append("visibility", visibility);
    formData.append("file", file);

    try {
      const doc = await api.uploadDocument(formData);
      router.push(`/documents/${doc.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading || !user) {
    return <p>Loading…</p>;
  }

  return (
    <div>
      <h1>Upload research</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxWidth: 480 }}>
        <label>
          Title
          <input
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </label>
        <label>
          Authors (comma-separated)
          <input value={authors} onChange={(e) => setAuthors(e.target.value)} style={{ width: "100%", padding: "0.5rem" }} />
        </label>
        <label>
          Field
          <input value={field} onChange={(e) => setField(e.target.value)} style={{ width: "100%", padding: "0.5rem" }} />
        </label>
        <label>
          Visibility
          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value as "public" | "private")}
            style={{ width: "100%", padding: "0.5rem" }}
          >
            <option value="private">Private</option>
            <option value="public">Public</option>
          </select>
        </label>
        <label>
          PDF file
          <input
            required
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>

        {error && <p style={{ color: "crimson" }}>{error}</p>}

        <button type="submit" disabled={submitting} style={{ padding: "0.6rem", fontWeight: 600 }}>
          {submitting ? "Uploading…" : "Upload"}
        </button>
      </form>
    </div>
  );
}
