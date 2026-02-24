import { useState } from "react";
import { FileText, FileType, HardDrive, Clock, Trash2, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import type { DocumentInfo } from "../types";
import { deleteDocument } from "../api";

interface Props {
  documents: DocumentInfo[];
  loading: boolean;
  onDeleted: () => void;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i]!;
}

function timeAgo(ts: number): string {
  const seconds = Math.floor((Date.now() - ts * 1000) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function fileIcon(name: string) {
  const ext = name.split(".").pop()?.toLowerCase();
  if (ext === "pdf") return <FileType className="w-4 h-4 text-rose-400" />;
  if (ext === "md" || ext === "markdown")
    return <FileText className="w-4 h-4 text-sky-400" />;
  return <FileText className="w-4 h-4 text-slate-400" />;
}

export default function DocumentList({ documents, loading, onDeleted }: Props) {
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleDelete = async (name: string) => {
    setDeleting(name);
    try {
      await deleteDocument(name);
      toast.success(`"${name}" deleted`);
      onDeleted();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="px-4 py-6 space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-14 rounded-lg bg-slate-800/50 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="px-4 py-8 text-center">
        <HardDrive className="w-10 h-10 text-slate-700 mx-auto mb-3" />
        <p className="text-sm text-slate-500">No documents yet</p>
        <p className="text-xs text-slate-600 mt-1">
          Upload your first file above
        </p>
      </div>
    );
  }

  return (
    <div className="px-4 py-2 space-y-1.5 max-h-[calc(100vh-380px)] overflow-y-auto">
      {documents.map((doc) => (
        <div
          key={doc.path}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg
                     bg-slate-800/30 hover:bg-slate-800/60 transition-colors
                     border border-transparent hover:border-slate-700/50 group"
        >
          <div className="shrink-0">{fileIcon(doc.name)}</div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-slate-200 truncate">
              {doc.name}
            </p>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs text-slate-500">
                {formatBytes(doc.size)}
              </span>
              <span className="text-slate-700">&#183;</span>
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {timeAgo(doc.modified_ts)}
              </span>
            </div>
          </div>

          <button
            onClick={() => handleDelete(doc.name)}
            disabled={deleting === doc.name}
            className="shrink-0 p-1.5 rounded-md
                       opacity-0 group-hover:opacity-100
                       text-slate-500 hover:text-rose-400
                       hover:bg-rose-500/10
                       transition-all disabled:opacity-50"
            title={`Delete ${doc.name}`}
          >
            {deleting === doc.name ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Trash2 className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      ))}
    </div>
  );
}
