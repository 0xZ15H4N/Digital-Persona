import { useState, useRef, useEffect } from "react";
import { sendChat, exitChat } from "./api.js";

const CHIPS = [
  "What are their top skills?",
  "Summarize their experience",
  "What industries have they worked in?",
  "Career progression?",
];

function Message({ msg, onRetry }) {
  if (msg.type === "typing") {
    return (
      <div className="msg-row bot">
        <div className="msg-avatar">✦</div>
        <div className="msg-body">
          <div className="bubble typing-bubble">
            <div className="dot" />
            <div className="dot" />
            <div className="dot" />
          </div>
        </div>
      </div>
    );
  }

  const isBot = msg.role === "bot";
  const isErr = msg.isErr;

  return (
    <div className={`msg-row ${msg.role}${isErr ? " err" : ""}`}>
      <div className="msg-avatar">{isBot ? "✦" : "You"}</div>
      <div className="msg-body">
        <div className="bubble">{isErr ? "⚠ " + msg.text : msg.text}</div>
        <div className="ts">{msg.time}</div>
        {isErr && (
          <button className="retry-btn" onClick={() => onRetry(msg.retryText)}>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
            </svg>
            Retry
          </button>
        )}
      </div>
    </div>
  );
}

export default function ChatView({ username, vectorId, onNewProfile, showToast }) {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chipsVisible, setChipsVisible] = useState(true);
  const messagesRef = useRef(null);
  const textareaRef = useRef(null);

  const initials = username.slice(0, 2).toUpperCase();

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTo({ top: messagesRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  function getTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  async function handleSend(text) {
    const trimmed = (text || query).trim();
    if (!trimmed || isLoading) return;

    setQuery("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "";
    }
    setChipsVisible(false);
    setIsLoading(true);

    const userMsg = { id: Date.now().toString(), role: "user", text: trimmed, time: getTime() };
    const typingId = "typing_" + Date.now();
    const typingMsg = { id: typingId, type: "typing" };

    setMessages((prev) => [...prev, userMsg, typingMsg]);

    try {
      const data = await sendChat(trimmed);
      if (!data.response) throw new Error("The AI returned an empty response. Please try again.");

      setMessages((prev) =>
        prev
          .filter((m) => m.id !== typingId)
          .concat({ id: Date.now().toString(), role: "bot", text: data.response, time: getTime() })
      );
    } catch (err) {
      setMessages((prev) =>
        prev
          .filter((m) => m.id !== typingId)
          .concat({
            id: Date.now().toString(),
            role: "bot",
            isErr: true,
            text: err.message,
            retryText: trimmed,
            time: getTime(),
          })
      );
      showToast("error", "Message Failed", err.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleRetry(retryText) {
    setMessages((prev) => prev.filter((m) => m.retryText !== retryText || !m.isErr));
    handleSend(retryText);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleTextareaChange(e) {
    setQuery(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  }

  async function handleNewProfile() {
    try {
      await exitChat(vectorId);
    } catch (_) {}
    localStorage.removeItem("vector_id");
    onNewProfile();
  }

  const showEmpty = messages.length === 0;

  return (
    <div className="view chat-view">
      <div className="profile-bar">
        <div className="profile-left">
          <div className="avatar">{initials}</div>
          <div>
            <div className="profile-name">{username}</div>
            <div className="profile-handle">linkedin.com/in/{username}</div>
          </div>
        </div>
        <button className="btn-outline" onClick={handleNewProfile}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
          </svg>
          New Profile
        </button>
      </div>

      <div className="messages" ref={messagesRef}>
        {showEmpty ? (
          <div className="empty">
            <div className="empty-glyph">💡</div>
            <div className="empty-title">Profile ready</div>
            <div className="empty-body">
              Ask anything about this person — skills, experience, career trajectory, and more.
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <Message key={msg.id} msg={msg} onRetry={handleRetry} />
          ))
        )}
      </div>

      {chipsVisible && (
        <div className="chips">
          {CHIPS.map((chip) => (
            <button
              key={chip}
              className="chip"
              disabled={isLoading}
              onClick={() => handleSend(chip)}
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      <div className="composer">
        <div className="compose-field">
          <textarea
            ref={textareaRef}
            placeholder="Ask anything about this profile…"
            rows={1}
            value={query}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
          />
        </div>
        <button
          className="send"
          disabled={!query.trim() || isLoading}
          onClick={() => handleSend()}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  );
}
