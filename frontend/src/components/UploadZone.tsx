import { useCallback, useState, type DragEvent, type ChangeEvent } from "react";
import { Upload, FileUp, Loader2, CheckCircle2 } from "lucide-react";
import toast from "react-hot-toast";
import { uploadDocument } from "../api";

interface Props {
  onUploaded: () => void;
}

const ACCEPTED = [".pdf", ".md", ".markdown", ".txt", ".rst"];

export default function UploadZone({ onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const handleFile = useCallback(
    async (file: File) => {
      const ext = "." + file.name.split(".").pop()?.toLowerCase();
      if (!ACCEPTED.includes(ext)) {
        toast.error(`Unsupported file type: ${ext}`);
        return;
      }

      setUploading(true);
      setLastResult(null);
      try {
        const res = await uploadDocument(file);
        setLastResult(
          `${res.documents_indexed} doc(s), ${res.chunks_added} chunks indexed`,
        );
        toast.success(`"${file.name}" uploaded and indexed`);
        onUploaded();
      } catch (err) {
        toast.error(
          err instanceof Error ? err.message : "Upload failed",
        );
      } finally {
        setUploading(false);
      }
    },
    [onUploaded],
  );

  const onDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const onFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
      e.target.value = "";
    },
    [handleFile],
  );

  return (
    <div className="px-4 pb-2">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`
          relative rounded-xl border-2 border-dashed p-6
          transition-all duration-200 cursor-pointer group
          ${
            dragging
              ? "border-indigo-400 bg-indigo-500/10 scale-[1.02]"
              : "border-slate-700 hover:border-slate-500 hover:bg-slate-800/40"
          }
          ${uploading ? "pointer-events-none opacity-60" : ""}
        `}
      >
        <input
          type="file"
          accept={ACCEPTED.join(",")}
          onChange={onFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />

        <div className="flex flex-col items-center gap-2 text-center">
          {uploading ? (
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          ) : lastResult ? (
            <CheckCircle2 className="w-8 h-8 text-emerald-400" />
          ) : dragging ? (
            <FileUp className="w-8 h-8 text-indigo-400 animate-bounce" />
          ) : (
            <Upload className="w-8 h-8 text-slate-500 group-hover:text-slate-300 transition-colors" />
          )}

          <div>
            <p className="text-sm font-medium text-slate-300">
              {uploading
                ? "Uploading & indexing..."
                : dragging
                  ? "Drop your file here"
                  : "Drag & drop or click to upload"}
            </p>
            <p className="text-xs text-slate-500 mt-1">
              PDF, Markdown, TXT, RST
            </p>
          </div>

          {lastResult && !uploading && (
            <p className="text-xs text-emerald-400/80 mt-1 animate-fade-in">
              {lastResult}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
