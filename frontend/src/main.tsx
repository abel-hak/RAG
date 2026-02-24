import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Toaster } from "react-hot-toast";
import App from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Toaster
      position="top-right"
      toastOptions={{
        style: {
          background: "#1e293b",
          color: "#e2e8f0",
          border: "1px solid rgba(51, 65, 85, 0.5)",
          borderRadius: "12px",
          fontSize: "0.875rem",
        },
        success: { iconTheme: { primary: "#34d399", secondary: "#1e293b" } },
        error: { iconTheme: { primary: "#f87171", secondary: "#1e293b" } },
      }}
    />
    <App />
  </StrictMode>,
);
