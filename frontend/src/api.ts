import type { Bot, ChatSession, FAQ, KnowledgeDocument } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? `${window.location.origin}/api`;

function token() {
  return localStorage.getItem("glowdom_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const savedToken = token();
  if (savedToken) headers.set("Authorization", `Bearer ${savedToken}`);
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) throw new Error((await response.json()).detail ?? "Request failed");
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = {
  listBots: () => request<Bot[]>("/bots"),
  getBot: (slug: string) => request<Bot>(`/bots/${slug}`),
  updateBot: (slug: string, payload: Partial<Bot>) => request<Bot>(`/bots/${slug}`, { method: "PATCH", body: JSON.stringify(payload) }),
  login: (email: string, password: string) => request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  chat: (slug: string, message: string, sessionId: string | null) =>
    request<{ session_id: string; answer: string }>(`/bots/${slug}/chat`, {
      method: "POST",
      body: JSON.stringify({ message, session_id: sessionId }),
    }),
  listFaqs: (slug: string) => request<FAQ[]>(`/bots/${slug}/faqs`),
  createFaq: (slug: string, question: string, answer: string) =>
    request<FAQ>(`/bots/${slug}/faqs`, { method: "POST", body: JSON.stringify({ question, answer }) }),
  updateFaq: (slug: string, id: string, payload: Partial<FAQ>) =>
    request<FAQ>(`/bots/${slug}/faqs/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteFaq: (slug: string, id: string) => request<void>(`/bots/${slug}/faqs/${id}`, { method: "DELETE" }),
  listDocuments: (slug: string) => request<KnowledgeDocument[]>(`/bots/${slug}/knowledge/documents`),
  pasteKnowledge: (slug: string, title: string, text: string, change_note: string) =>
    request<KnowledgeDocument>(`/bots/${slug}/knowledge/paste`, { method: "POST", body: JSON.stringify({ title, text, change_note }) }),
  addDocumentVersion: (slug: string, documentId: string, title: string, text: string, change_note: string) =>
    request<KnowledgeDocument>(`/bots/${slug}/knowledge/documents/${documentId}/versions/paste`, { method: "POST", body: JSON.stringify({ title, text, change_note }) }),
  uploadKnowledge: (slug: string, file: File, changeNote: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("change_note", changeNote);
    return request<KnowledgeDocument>(`/bots/${slug}/knowledge/upload`, { method: "POST", body: form });
  },
  chatHistory: (slug: string) => request<ChatSession[]>(`/admin/bots/${slug}/chat-history`),
};
