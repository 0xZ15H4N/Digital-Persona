import { useState, useEffect } from "react";
import LandingView from "./LandingView.jsx";
import ChatView from "./ChatView.jsx";
import { ToastRack, useToast } from "./Toast.jsx";
import { exitChat } from "./api.js";
import "./styles.css";

export default function App() {
  const [view, setView] = useState("landing");
  const [username, setUsername] = useState("");
  const [vectorId, setVectorId] = useState(null);
  const { toasts, showToast, dismiss } = useToast();

  useEffect(() => {
    const stale = localStorage.getItem("vector_id");
    if (stale) {
      exitChat(stale);
      localStorage.removeItem("vector_id");
    }
  }, []);

  function handleProfileLoaded(user, vid) {
    setUsername(user);
    setVectorId(vid);
    setView("chat");
  }

  function handleNewProfile() {
    setView("landing");
    setUsername("");
    setVectorId(null);
  }

  return (
    <>
      <ToastRack toasts={toasts} onDismiss={dismiss} />
      <div className="shell">
        <header className="header">
          <div className="header-brand">
            <div className="logo">✦</div>
            <div>
              <div className="brand-name">Digital Persona</div>
              <div className="brand-sub">LinkedIn Intelligence</div>
            </div>
          </div>
          <div className={`status-pill${view === "chat" ? " live" : ""}`}>
            <span className="pip" />
            <span>{view === "chat" ? "Profile active" : "Ready"}</span>
          </div>
        </header>

        {view === "landing" && (
          <LandingView onProfileLoaded={handleProfileLoaded} showToast={showToast} />
        )}
        {view === "chat" && (
          <ChatView
            username={username}
            vectorId={vectorId}
            onNewProfile={handleNewProfile}
            showToast={showToast}
          />
        )}
      </div>
    </>
  );
}
