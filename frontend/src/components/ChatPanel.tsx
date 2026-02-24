import {
  useState,
  useRef,
  useEffect,
  useCallback,
  type FormEvent,
  type KeyboardEvent,
} from "react";
import { Send, MessageSquarePlus, Sparkles } from "lucide-react";
import toast from "react-hot-toast";
import type { ChatMessage } from "../types";
import { askQuestion } from "../api";
import MessageBubble from "./MessageBubble";
import ThinkingIndicator from "./ThinkingIndicator";

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, thinking, scrollToBottom]);

  const handleSubmit = useCallback(
    async (e?: FormEvent) => {
      e?.preventDefault();
      const question = input.trim();
      if (!question || thinking) return;

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: question,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setThinking(true);

      // Resize textarea back
      if (inputRef.current) inputRef.current.style.height = "auto";

      try {
        const res = await askQuestion(question);

        const assistantMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        toast.error(
          err instanceof Error ? err.message : "Failed to get answer",
        );

        const errorMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            "Sorry, something went wrong while processing your question. Please try again.",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setThinking(false);
        inputRef.current?.focus();
      }
    },
    [input, thinking],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit],
  );

  const handleClear = useCallback(() => {
    setMessages([]);
    setInput("");
    inputRef.current?.focus();
  }, []);

  const handleTextareaInput = useCallback(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, []);

  return (
    <div className="flex-1 flex flex-col h-screen">
      {/* Top bar */}
      <div className="shrink-0 px-6 py-4 border-b border-slate-800/40 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Ask your documents
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Questions are answered using only your uploaded documents, with source citations.
          </p>
        </div>

        {messages.length > 0 && (
          <button
            onClick={handleClear}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium
                       text-slate-400 hover:text-white
                       bg-slate-800/60 hover:bg-slate-800
                       border border-slate-700/40 hover:border-slate-600
                       rounded-lg transition-all"
          >
            <MessageSquarePlus className="w-3.5 h-3.5" />
            New Chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 && !thinking ? (
          <EmptyState />
        ) : (
          <div className="max-w-3xl mx-auto space-y-5">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {thinking && <ThinkingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="shrink-0 px-6 pb-5 pt-2">
        <form
          onSubmit={handleSubmit}
          className="max-w-3xl mx-auto relative"
        >
          <div
            className="flex items-end gap-2 rounded-2xl glass
                       px-4 py-3 focus-within:border-indigo-500/50
                       transition-all shadow-lg shadow-slate-950/50"
          >
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onInput={handleTextareaInput}
              placeholder="Ask a question about your documents..."
              rows={1}
              disabled={thinking}
              className="flex-1 bg-transparent text-sm text-slate-200
                        placeholder-slate-500 resize-none outline-none
                        max-h-40 leading-relaxed"
            />

            <button
              type="submit"
              disabled={!input.trim() || thinking}
              className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center
                        transition-all duration-200
                        disabled:opacity-30 disabled:cursor-not-allowed
                        bg-indigo-600 hover:bg-indigo-500 active:scale-95
                        shadow-md shadow-indigo-500/20"
            >
              <Send className="w-4 h-4 text-white" />
            </button>
          </div>

          <p className="text-center text-[10px] text-slate-600 mt-2">
            Press Enter to send &middot; Shift+Enter for new line
          </p>
        </form>
      </div>
    </div>
  );
}

function EmptyState() {
  const suggestions = [
    "What are the main topics covered in the documents?",
    "Summarize the key points from my files",
    "What conclusions or recommendations are mentioned?",
  ];

  return (
    <div className="flex-1 flex items-center justify-center min-h-[60vh]">
      <div className="text-center max-w-md animate-fade-in">
        <div
          className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-600/20
                     border border-indigo-500/20 flex items-center justify-center mx-auto mb-5"
        >
          <Sparkles className="w-8 h-8 text-indigo-400" />
        </div>

        <h3 className="text-xl font-semibold text-white mb-2">
          Ready to explore your documents
        </h3>
        <p className="text-sm text-slate-400 mb-6 leading-relaxed">
          Upload PDFs, markdown, or text files, then ask questions.
          Every answer includes citations to the original sources.
        </p>

        <div className="space-y-2">
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">
            Try asking
          </p>
          {suggestions.map((s, i) => (
            <div
              key={i}
              className="px-4 py-2.5 rounded-xl text-left text-sm text-slate-400
                         bg-slate-800/30 border border-slate-800/50
                         hover:border-indigo-500/30 hover:text-slate-300 hover:bg-slate-800/50
                         transition-all cursor-default"
            >
              &ldquo;{s}&rdquo;
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
