import { Bot } from "lucide-react";

export default function ThinkingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="shrink-0 mt-1">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600
                       flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Bot className="w-4 h-4 text-white" />
        </div>
      </div>

      <div className="glass-light rounded-2xl rounded-bl-md px-5 py-4">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0ms]" />
          <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:150ms]" />
          <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:300ms]" />
        </div>
        <p className="text-xs text-slate-500 mt-2">Searching documents & generating answer...</p>
      </div>
    </div>
  );
}
