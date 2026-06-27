import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { useAuth } from "./auth";
import { getTheme, toggleTheme } from "./theme";
import DailyCall from "./components/DailyCall";
import DebateArena from "./components/DebateArena";
import GMMode from "./components/GMMode";
import CoachScore from "./components/CoachScore";
import Leaderboard from "./components/Leaderboard";
import LiveScores from "./components/LiveScores";
import Gauntlet from "./components/Gauntlet";
import Survey from "./components/Survey";
import Ambient from "./components/Ambient";
import AuthModal from "./components/AuthModal";
import FeedbackWidget from "./components/FeedbackWidget";

const TABS = [
  { id: "daily", label: "Daily Call" },
  { id: "gauntlet", label: "⚡ Gauntlet" },
  { id: "scores", label: "Scores" },
  { id: "debate", label: "Debate" },
  { id: "gm", label: "GM Mode" },
  { id: "score", label: "Coach Score" },
  { id: "survey", label: "📣 Survey", cls: "tab-survey" }, // temporary — remove after the user study
];

export default function App() {
  const { user, ready, logout } = useAuth();
  const [tab, setTab] = useState("daily");
  const [sport, setSport] = useState("NFL");
  const [showAuth, setShowAuth] = useState(false);
  const [score, setScore] = useState(null);
  const [toast, setToast] = useState(null);
  const [theme, setThemeState] = useState(getTheme());
  const [challenge, setChallenge] = useState(null);

  // Someone opened a challenge link (?c=ID): load it and jump to the right tab.
  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("c");
    if (!id) return;
    api
      .getChallenge(id)
      .then((ch) => {
        setChallenge(ch);
        setTab(ch.kind === "gm" ? "gm" : "daily");
      })
      .catch(() => {})
      .finally(() => {
        // Clean the URL so a refresh doesn't replay the challenge.
        window.history.replaceState({}, "", window.location.pathname);
      });
  }, []);

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
      <Ambient />
      <header className="topbar">
        <div className="brand">
          <h1>
            Oaksy<span className="dot">.</span>
          </h1>
          <span className="tag">Out-coach the coach</span>
        </div>
        <div className="topbar-right">
          <button
            className="theme-toggle"
            onClick={() => setThemeState(toggleTheme())}
            title="Toggle light / dark"
            aria-label="Toggle light or dark theme"
          >
            {theme === "light" ? "🌙" : "☀️"}
          </button>
          {user ? (
            <>
              <div
                className="scorechip"
                onClick={() => setTab("score")}
                style={{ cursor: "pointer" }}
              >
                {score ? (
                  <>
                    {score.current_streak > 0 && (
                      <span title={`${score.current_streak}-day streak`}>
                        🔥{score.current_streak}
                      </span>
                    )}
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

      <div className="shell">
        <main className="main-col">
          <nav className="tabs">
            {TABS.map((t) => (
              <button
                key={t.id}
                className={`tab ${t.cls || ""} ${tab === t.id ? "active" : ""}`}
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
              challenge={challenge?.kind === "daily" ? challenge : null}
              onExitChallenge={() => setChallenge(null)}
            />
          )}
          {tab === "gauntlet" && <Gauntlet onToast={showToast} />}
          {tab === "scores" && <LiveScores />}
          {tab === "survey" && <Survey onToast={showToast} />}
          {tab === "debate" && (
            <DebateArena
              user={user}
              onLogin={() => setShowAuth(true)}
              onToast={showToast}
            />
          )}
          {tab === "gm" && (
            <GMMode
              onSubmitted={refreshScore}
              onToast={showToast}
              coachScore={score}
              challenge={challenge?.kind === "gm" ? challenge : null}
              onExitChallenge={() => setChallenge(null)}
            />
          )}
          {tab === "score" && (
            <CoachScore user={user} score={score} onLogin={() => setShowAuth(true)} />
          )}
        </main>

        <aside className="rail">
          <Rail onPlay={() => setTab("daily")} />
        </aside>
      </div>

      <footer className="footer">
        Oaksy<span style={{ color: "var(--accent)" }}>.</span> — the arena where fans
        out-coach the coach, and settle it with data.
        {" · "}
        <a href="/landing.html" style={{ color: "var(--gold-text)" }}>
          Get launch updates
        </a>
      </footer>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
      <FeedbackWidget />
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

function Rail() {
  return (
    <>
      <div className="rail-card">
        <h4 className="rail-title">How Oaksy works</h4>
        <ol className="how">
          <li>
            <b>Make the call.</b> One real game decision. 30 seconds. 3 choices.
          </li>
          <li>
            <b>See the verdict.</b> What the coach did, the outcome, the data-backed take.
          </li>
          <li>
            <b>Build your score.</b> Out-coach real coaches and climb the board.
          </li>
        </ol>
      </div>
      <div className="rail-card">
        <h4 className="rail-title">Top coaches this week</h4>
        <Leaderboard />
      </div>
    </>
  );
}
