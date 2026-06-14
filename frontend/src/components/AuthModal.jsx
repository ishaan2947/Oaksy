import { useState } from "react";
import { useAuth } from "../auth";

export default function AuthModal({ onClose }) {
  const { login, signup } = useAuth();
  const [mode, setMode] = useState("signup");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

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
