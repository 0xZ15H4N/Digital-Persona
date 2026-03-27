import { useState, useRef } from "react";
import { fetchLinkedInProfile, createChunks, createDB, loadVectorDB } from "./api.js";

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export default function LandingView({ onProfileLoaded, showToast }) {
  const [username, setUsername] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasErr, setHasErr] = useState(false);
  const [errMsg, setErrMsg] = useState("");
  const [steps, setSteps] = useState([]);
  const [showSteps, setShowSteps] = useState(false);

  const inputRef = useRef(null);

  function showErr(msg) {
    setHasErr(true);
    setErrMsg(msg);
    inputRef.current?.focus();
  }

  function clearErr() {
    setHasErr(false);
    setErrMsg("");
  }

  function addStep(text, state) {
    const id = Date.now().toString() + Math.random();
    setSteps((prev) => [...prev, { id, text, state, in: false }]);
    setTimeout(() => {
      setSteps((prev) =>
        prev.map((s) => (s.id === id ? { ...s, in: true } : s))
      );
    }, 20);
    return id;
  }

  function updateStep(id, text, state) {
    setSteps((prev) =>
      prev.map((s) => (s.id === id ? { ...s, text, state, in: true } : s))
    );
  }

  function markStepsError(msg) {
    setSteps((prev) =>
      prev.map((s) =>
        s.state === "loading" ? { ...s, state: "error", text: msg, in: true } : s
      )
    );
  }

  async function handleAnalyze() {
    const userID = username.trim();
    if (!userID) { showErr("Please enter a LinkedIn username."); return; }
    if (userID.length < 3) { showErr("Username must be at least 3 characters."); return; }
    if (isLoading) return;

    setIsLoading(true);
    clearErr();
    setShowSteps(true);
    setSteps([]);

    const step1 = addStep("Fetching LinkedIn profile…", "loading");

    try {
      const profileData = await fetchLinkedInProfile(userID);
      const documents = await createChunks(profileData);
      const dbResult = await createDB(documents.chunks);

      const vectorId = dbResult.vector_id;
      localStorage.setItem("vector_id", vectorId);

      updateStep(step1, "Profile data retrieved", "done");
      const step2 = addStep("Building AI context…", "loading");

      await delay(1000);

      const vdResult = await loadVectorDB(vectorId);

      if (vdResult.status === "Failed" || vdResult.status_code === 500) {
        throw new Error("AI context could not be loaded. Please try again.");
      }

      updateStep(step2, "AI context ready", "done");
      await delay(400);

      showToast("success", "Profile Loaded", `"${userID}" is ready to chat.`);
      onProfileLoaded(userID, vectorId);
    } catch (err) {
      markStepsError(err.message);
      showToast("error", "Analysis Failed", err.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleAnalyze();
  }

  function renderStepIcon(state) {
    if (state === "loading") return <div className="spin" />;
    if (state === "done") return "✓";
    return "✕";
  }

  return (
    <div className="view landing-view">
      <div className="hero">
        <div className="hero-eyebrow">
          <span className="hero-eyebrow-dot" />
          AI-Powered Profile Analysis
        </div>
        <h1 className="hero-title">
          Chat with any<br />
          <span className="grad">LinkedIn profile</span>
        </h1>
        <p className="hero-body">
          Enter a LinkedIn username to analyze their public profile. Then ask
          anything — career path, skills, experience, and hidden insights.
        </p>
      </div>

      <div className="card">
        <div className="field-label">LinkedIn Username</div>

        <div className="search-row">
          <div className={`input-wrap${hasErr ? " err" : ""}`}>
            <span className="input-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
                <rect x="2" y="9" width="4" height="12" />
                <circle cx="4" cy="4" r="2" />
              </svg>
            </span>
            <input
              ref={inputRef}
              type="text"
              placeholder="e.g. john-doe-123"
              autoComplete="off"
              spellCheck="false"
              maxLength={100}
              value={username}
              onChange={(e) => { setUsername(e.target.value); clearErr(); }}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
          </div>
          <button className="btn-cta" onClick={handleAnalyze} disabled={isLoading}>
            {!isLoading && (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
            )}
            {isLoading ? "Analyzing…" : "Analyze"}
          </button>
        </div>

        <div className={`err-hint${hasErr ? " show" : ""}`}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{errMsg}</span>
        </div>

        <div className="status-area">
          {showSteps && steps.length > 0 && (
            <div className="steps show">
              {steps.map((step) => (
                <div key={step.id} className={`step ${step.state}${step.in ? " in" : ""}`}>
                  <div className="step-dot">{renderStepIcon(step.state)}</div>
                  <span>{step.text}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="pills">
          <div className="pill"><span className="pill-icon">🔍</span><span>Deep analysis</span></div>
          <div className="pill"><span className="pill-icon">💬</span><span>Conversational AI</span></div>
          <div className="pill"><span className="pill-icon">⚡</span><span>Instant insights</span></div>
        </div>
      </div>
    </div>
  );
}
