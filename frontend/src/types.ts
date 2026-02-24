export interface DocumentInfo {
  name: string;
  path: string;
  size: number;
  modified_ts: number;
}

export interface Source {
  source: string;
  metadata: Record<string, unknown> | null;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface UploadResponse {
  message: string;
  documents_indexed: number;
  chunks_added: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: Date;
}
