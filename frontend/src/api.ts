import type { AskResponse, DocumentInfo, UploadResponse } from "./types";

const BASE = "/api";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail =
      (body as { detail?: string } | null)?.detail ?? res.statusText;
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${BASE}/documents`);
  return handleResponse<DocumentInfo[]>(res);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  return handleResponse<UploadResponse>(res);
}

export async function deleteDocument(filename: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });
  await handleResponse<unknown>(res);
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return handleResponse<AskResponse>(res);
}
