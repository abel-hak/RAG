import { useCallback, useState } from "react";
import { Menu } from "lucide-react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [, setRefreshKey] = useState(0);

  const handleDocumentsChange = useCallback(() => {
    setRefreshKey((k) => k + 1);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      {/* Mobile hamburger */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="fixed top-4 left-4 z-30 lg:hidden p-2 rounded-lg
                   glass hover:bg-slate-800 text-slate-300
                   hover:text-white transition-colors"
        aria-label="Open sidebar"
      >
        <Menu className="w-5 h-5" />
      </button>

      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onDocumentsChange={handleDocumentsChange}
      />
      <ChatPanel />
    </div>
  );
}
