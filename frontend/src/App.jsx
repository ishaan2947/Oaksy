import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { useAuth } from "./auth";
import DailyCall from "./components/DailyCall";
import DebateArena from "./components/DebateArena";
import CoachScore from "./components/CoachScore";
import AuthModal from "./components/AuthModal";

const TABS = [
  { id: "daily", label: "Daily Call" },
  { id: "debate", label: "Debate Arena" },
  { id: "score", label: "Coach Score" },
];

export default function App() {
  const { user, ready, logout } = useAuth();
  const [tab, setTab] = useState("daily");
  const [sport, setSport] = useState("NFL");
  const [showAuth, setShowAuth] = useState(false);
  const [score, setScore] = useState(null);
  const [toast, setToast] = useState(null);

  const refreshScore = useCallback(() => {
    if (!user) {
      setScore(null);
      return;
    }
    api.myScore().then(setScore).catch(() => {});
  }, [user]);

  useEffect(() => {
    refreshScore();
  }, [refreshScore]);

  const showToast = useCallback((msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2600);
  }, []);

  if (!ready) return <div className="spinner" style={{ marginTop: 120 }}>Oaksy…</div>;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <h1>
            Oaksy<span className="dot">.</span>
          </h1>
          <span className="tag">Out-coach the coach</span>
        </div>
        <div className="topbar-right">
          {user ? (
            <>
              <div
                className="scorechip"
                onClick={() => setTab("score")}
                style={{ cursor: "pointer" }}
              >
                {score ? (
                  <>
                    <span>Coach Score</span>
                    <b>{score.win_rate}%</b>
                  </>
                ) : (
                  <span>{user.display_name}</span>
                )}
              </div>
              <button className="btn ghost" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <button className="btn primary" onClick={() => setShowAuth(true)}>
              Sign in
            </button>
          )}
        </div>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "daily" && (
        <DailyCall
          sport={sport}
          onSport={setSport}
          coachScore={score}
          onPicked={refreshScore}
          onToast={showToast}
        />
      )}
      {tab === "debate" && (
        <DebateArena
          user={user}
          onLogin={() => setShowAuth(true)}
          onToast={showToast}
        />
      )}
      {tab === "score" && (
        <CoachScore user={user} score={score} onLogin={() => setShowAuth(true)} />
      )}

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
