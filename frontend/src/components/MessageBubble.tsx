import { User, Bot, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import type { ChatMessage } from "../types";
import SourceCard from "./SourceCard";

interface Props {
  message: ChatMessage;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const hasSources = message.sources && message.sources.length > 0;
  const [sourcesOpen, setSourcesOpen] = useState(true);

  return (
    <div className={`flex gap-3 animate-slide-up ${isUser ? "justify-end" : ""}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="shrink-0 mt-1">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600
                         flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Bot className="w-4 h-4 text-white" />
          </div>
        </div>
      )}

      {/* Bubble */}
      <div
        className={`
          max-w-[75%] rounded-2xl px-4 py-3
          ${
            isUser
              ? "bg-indigo-600 text-white rounded-br-md"
              : "glass-light rounded-bl-md"
          }
        `}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        ) : (
          <div className="answer-content text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        )}

        {/* Sources */}
        {hasSources && (
          <div className="mt-3 pt-3 border-t border-slate-700/40">
            <button
              onClick={() => setSourcesOpen(!sourcesOpen)}
              className="flex items-center gap-1.5 text-xs text-slate-400
                        hover:text-indigo-300 transition-colors mb-2"
            >
              {sourcesOpen ? (
                <ChevronDown className="w-3.5 h-3.5" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5" />
              )}
              <span className="font-medium">
                {message.sources!.length} source
                {message.sources!.length > 1 ? "s" : ""} cited
              </span>
            </button>

            {sourcesOpen && (
              <div className="flex flex-wrap gap-1.5 animate-fade-in">
                {message.sources!.map((src, i) => (
                  <SourceCard key={i} source={src} index={i} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p
          className={`text-[10px] mt-2 ${
            isUser ? "text-indigo-200/50" : "text-slate-600"
          }`}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="shrink-0 mt-1">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-slate-600 to-slate-700
                         flex items-center justify-center">
            <User className="w-4 h-4 text-slate-300" />
          </div>
        </div>
      )}
    </div>
  );
}
