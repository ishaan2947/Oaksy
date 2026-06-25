import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth";

// Load Google Identity Services once, on demand.
function loadGsi() {
  return new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) return resolve();
    let s = document.getElementById("gsi-script");
    if (s) {
      s.addEventListener("load", () => resolve());
      s.addEventListener("error", reject);
      return;
    }
    s = document.createElement("script");
    s.src = "https://accounts.google.com/gsi/client";
    s.async = true;
    s.defer = true;
    s.id = "gsi-script";
    s.onload = () => resolve();
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

export default function AuthModal({ onClose }) {
  const { login, signup, loginWithGoogle } = useAuth();
  const [mode, setMode] = useState("signup");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [clientId, setClientId] = useState(null);
  const googleBtnRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    api
      .authConfig()
      .then((cfg) => !cancelled && setClientId(cfg.google_client_id || null))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!clientId || !googleBtnRef.current) return;
    let cancelled = false;
    loadGsi()
      .then(() => {
        if (cancelled || !window.google?.accounts?.id) return;
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: async (resp) => {
            try {
              await loginWithGoogle(resp.credential);
              onClose();
            } catch (e) {
              setErr(e.message);
            }
          },
        });
        googleBtnRef.current.innerHTML = "";
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: "outline",
          size: "large",
          text: "continue_with",
          shape: "pill",
          width: 300,
        });
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [clientId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function submit(e) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      if (mode === "signup") await signup(email, name, password);
      else await login(email, password);
      onClose();
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="overlay" onClick={onClose}>
      <div className="card modal" onClick={(e) => e.stopPropagation()}>
        <h3>{mode === "signup" ? "Claim your Coach Score" : "Welcome back"}</h3>
        <div className="sub">
          {mode === "signup"
            ? "Track your record vs real coaches and join the debate."
            : "Sign in to keep building your record."}
        </div>

        {clientId && (
          <>
            <div className="gbtn-wrap">
              <div ref={googleBtnRef} className="gbtn" />
            </div>
            <div className="or-divider">
              <span>or use email</span>
            </div>
          </>
        )}

        <form onSubmit={submit}>
          {mode === "signup" && (
            <div className="field">
              <label>Coach name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="What should the leaderboard call you?"
                required
                maxLength={40}
              />
            </div>
          )}
          <div className="field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@email.com"
              required
            />
          </div>
          <div className="field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={mode === "signup" ? "At least 8 characters" : "••••••••"}
              required
              minLength={8}
            />
          </div>
          <div className="modal-err">{err}</div>
          <button className="btn primary" style={{ width: "100%" }} disabled={busy}>
            {busy ? "…" : mode === "signup" ? "Create account" : "Sign in"}
          </button>
        </form>

        <div className="modal-switch">
          {mode === "signup" ? "Already have an account?" : "New to Oaksy?"}{" "}
          <button
            className="linkbtn"
            onClick={() => {
              setErr("");
              setMode(mode === "signup" ? "login" : "signup");
            }}
          >
            {mode === "signup" ? "Sign in" : "Create one"}
          </button>
        </div>
      </div>
    </div>
  );
}
