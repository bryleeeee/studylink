const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface DocumentListItem {
  id: string;
  title: string;
  authors: string[] | null;
  field: string | null;
  summary: string | null;
  summary_status: "pending" | "done" | "failed";
  created_at: string;
}

export interface DocumentDetail extends DocumentListItem {
  author_id: string;
  keywords: string[] | null;
  visibility: "public" | "private";
}

export interface CurrentUser {
  id: string;
  email: string;
  is_researcher_verified: boolean;
  is_admin: boolean;
}

const TOKEN_KEY = "access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (!(options.body instanceof FormData) && options.body) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail.detail ?? `Request failed: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  register: (email: string, password: string, display_name?: string) =>
    request<{ access_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),

  getMe: () => request<CurrentUser>("/auth/me"),

  browseDocuments: (params: { q?: string; field?: string } = {}) => {
    const search = new URLSearchParams();
    if (params.q) search.set("q", params.q);
    if (params.field) search.set("field", params.field);
    const query = search.toString();
    return request<DocumentListItem[]>(`/documents${query ? `?${query}` : ""}`);
  },

  getDocument: (id: string) => request<DocumentDetail>(`/documents/${id}`),

  uploadDocument: (formData: FormData) =>
    request<DocumentDetail>("/documents", { method: "POST", body: formData }),
};
