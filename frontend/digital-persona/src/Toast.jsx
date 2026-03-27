import { useState, useCallback, useRef } from "react";

const TOAST_DUR = 4500;
const TOAST_ICONS = { success: "✓", error: "✕", info: "ℹ" };

function ToastItem({ toast, onDismiss }) {
  return (
    <div
      className={`toast ${toast.type}`}
      style={{ "--toast-dur": TOAST_DUR + "ms" }}
      onClick={() => onDismiss(toast.id)}
    >
      <div className="toast-icon">{TOAST_ICONS[toast.type] || "ℹ"}</div>
      <div>
        <div className="toast-title">{toast.title}</div>
        {toast.msg && <div className="toast-msg">{toast.msg}</div>}
      </div>
    </div>
  );
}

export function ToastRack({ toasts, onDismiss }) {
  return (
    <div className="toast-rack">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

export function useToast() {
  const [toasts, setToasts] = useState([]);
  const timers = useRef({});

  const dismiss = useCallback((id) => {
    clearTimeout(timers.current[id]);
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((type, title, msg) => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, type, title, msg }]);
    timers.current[id] = setTimeout(() => dismiss(id), TOAST_DUR);
  }, [dismiss]);

  return { toasts, showToast, dismiss };
}
