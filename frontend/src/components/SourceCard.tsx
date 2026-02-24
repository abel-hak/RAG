import { ExternalLink, FileText } from "lucide-react";
import type { Source } from "../types";

interface Props {
  source: Source;
  index: number;
}

function isUrl(s: string): boolean {
  return (
    s.startsWith("http") ||
    s.includes("github.com/") ||
    s.includes("notion.so/") ||
    s.includes("drive.google.com/")
  );
}

function getUrl(s: string): string {
  if (s.startsWith("http")) return s;
  return "https://" + s;
}

function getLabel(s: string): string {
  const parts = s.split(/[/\\]/);
  return parts[parts.length - 1] ?? s;
}

export default function SourceCard({ source, index }: Props) {
  const s = source.source;
  const url = isUrl(s);
  const label = getLabel(s);
  const page = source.metadata?.["page"];

  return (
    <div
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
                 bg-slate-800/60 border border-slate-700/40
                 hover:border-indigo-500/30 hover:bg-slate-800
                 transition-all text-xs group"
    >
      <span className="flex items-center justify-center w-5 h-5 rounded-full
                       bg-indigo-500/15 text-indigo-400 text-[10px] font-semibold shrink-0">
        {index + 1}
      </span>

      {url ? (
        <a
          href={getUrl(s)}
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-300 hover:text-indigo-300 truncate max-w-[180px] transition-colors"
        >
          {label}
        </a>
      ) : (
        <span className="text-slate-300 truncate max-w-[180px] flex items-center gap-1">
          <FileText className="w-3 h-3 shrink-0" />
          {label}
        </span>
      )}

      {page != null && (
        <span className="text-slate-500">p.{String(page)}</span>
      )}

      {url && (
        <ExternalLink className="w-3 h-3 text-slate-600 group-hover:text-indigo-400 transition-colors shrink-0" />
      )}
    </div>
  );
}
