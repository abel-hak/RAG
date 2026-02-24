import { useCallback, useEffect, useState } from "react";
import {
  BookOpen,
  FolderOpen,
  RefreshCw,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import { fetchDocuments, healthCheck } from "../api";
import type { DocumentInfo } from "../types";
import UploadZone from "./UploadZone";
import DocumentList from "./DocumentList";

interface Props {
  open: boolean;
  onClose: () => void;
  onDocumentsChange: () => void;
}

export default function Sidebar({ open, onClose, onDocumentsChange }: Props) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [online, setOnline] = useState(true);

  const loadDocs = useCallback(async () => {
    setLoading(true);
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
      setOnline(true);
    } catch {
      setOnline(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocs();
    const interval = setInterval(async () => {
      setOnline(await healthCheck());
    }, 30_000);
    return () => clearInterval(interval);
  }, [loadDocs]);

  const handleUploaded = useCallback(() => {
    loadDocs();
    onDocumentsChange();
  }, [loadDocs, onDocumentsChange]);

  const handleDeleted = useCallback(() => {
    loadDocs();
    onDocumentsChange();
  }, [loadDocs, onDocumentsChange]);

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed lg:relative z-50 lg:z-auto
          w-80 shrink-0 h-screen flex flex-col
          border-r border-slate-800/60 bg-slate-950/95 lg:bg-slate-950/80
          transition-transform duration-300 ease-in-out
          ${open ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
      >
        {/* Header */}
        <div className="px-5 pt-5 pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600
                             flex items-center justify-center shadow-lg shadow-indigo-500/25">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold tracking-tight text-white">
                  DocuMind
                </h1>
                <p className="text-[11px] text-slate-500 -mt-0.5">
                  AI Document Intelligence
                </p>
              </div>
            </div>

            {/* Mobile close */}
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-800 text-slate-400
                         hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Status */}
          <div className="flex items-center gap-2 mt-4 px-1">
            {online ? (
              <div className="flex items-center gap-1.5 text-emerald-400">
                <Wifi className="w-3.5 h-3.5" />
                <span className="text-[11px] font-medium">API Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-rose-400">
                <WifiOff className="w-3.5 h-3.5" />
                <span className="text-[11px] font-medium">API Offline</span>
              </div>
            )}
          </div>
        </div>

        {/* Upload */}
        <div className="px-1">
          <UploadZone onUploaded={handleUploaded} />
        </div>

        {/* Docs header */}
        <div className="flex items-center justify-between px-5 pt-4 pb-1">
          <div className="flex items-center gap-2">
            <FolderOpen className="w-4 h-4 text-slate-500" />
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Documents
            </h2>
            {documents.length > 0 && (
              <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded-full">
                {documents.length}
              </span>
            )}
          </div>
          <button
            onClick={loadDocs}
            disabled={loading}
            className="p-1.5 rounded-md hover:bg-slate-800 text-slate-500
                       hover:text-slate-300 transition-colors disabled:opacity-40"
            title="Refresh"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>

        {/* Document list */}
        <div className="flex-1 overflow-hidden">
          <DocumentList documents={documents} loading={loading} onDeleted={handleDeleted} />
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-800/40">
          <p className="text-[10px] text-slate-600 text-center">
            Built with FastAPI &middot; React &middot; ChromaDB
          </p>
        </div>
      </aside>
    </>
  );
}
