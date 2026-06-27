import { useCallback, useState } from "react";
import { api } from "../api";
import FieldDiagram from "./FieldDiagram";

const BEST_KEY = "oaksy_gauntlet_best";

// The Gauntlet — endless sudden-death survival. Random real calls back-to-back;
// keep going as long as you're right, chase your best run. The "one more" loop.
export default function Gauntlet({ onToast }) {
  const [situation, setSituation] = useState(null);
  const [seen, setSeen] = useState([]);
  const [run, setRun] = useState(0);
  const [best, setBest] = useState(() => Number(localStorage.getItem(BEST_KEY) || 0));
  const [phase, setPhase] = useState("intro"); // intro | play | reveal | over
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadNext = useCallback(
    (seenList) => {
      setLoading(true);
      setResult(null);
      api
        .gauntletNext(seenList)
        .then((s) => {
          setSituation(s);
          setPhase("play");
        })
        .catch((e) => onToast?.(e.message))
        .finally(() => setLoading(false));
    },
    [onToast]
  );

  function start() {
    setRun(0);
    setSeen([]);
    loadNext([]);
  }

  async function pick(choice) {
    if (busy || phase !== "play") return;
    setBusy(true);
    try {
      const r = await api.gauntletGrade(situation.id, choice);
      setResult(r);
      setSeen((s) => [...s, situation.id]);
      if (r.correct) {
        setRun((n) => n + 1);
        setPhase("reveal");
      } else {
        if (run > best) {
          setBest(run);
          localStorage.setItem(BEST_KEY, String(run));
        }
        setPhase("over");
      }
    } catch (e) {
      onToast?.(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function share() {
    const text = `I nailed ${best} coach's calls in a row on Oaksy's Gauntlet. Beat it:`;
    const url = window.location.origin;
    try {
      if (navigator.share) await navigator.share({ title: "Oaksy Gauntlet", text, url });
      else {
        await navigator.clipboard.writeText(`${text} ${url}`);
        onToast?.("Copied — go flex.");
      }
    } catch {
      /* cancelled */
    }
  }

  // ---- Intro ----
  if (phase === "intro") {
    return (
      <div className="card gauntlet-intro">
        <div className="eyebrow center" style={{ justifyContent: "center" }}>
          <span className="sport">⚡ Gauntlet</span>
          <span>Endless mode</span>
        </div>
        <h2 className="intro-title" style={{ marginTop: 12 }}>
          How many calls can you nail in a row?
        </h2>
        <p className="intro-sub">
          Real situations, one after another. Get the data's call right and you move
          on. Miss one and the run's over. No timer — just nerve.
        </p>
        {best > 0 && <div className="gauntlet-best-big">Best run: {best} 🔥</div>}
        <button className="btn primary intro-start" onClick={start}>
          Start the run →
        </button>
      </div>
    );
  }

  // ---- Game over ----
  if (phase === "over") {
    return (
      <>
        <div className="card gauntlet-over">
          <div className="run-final">{run}</div>
          <div className="run-final-label">
            {run === 0 ? "Out on the first call." : `calls right in a row`}
          </div>
          <div className="gauntlet-best">Best run: {Math.max(best, run)}</div>
          {result && <MissCard result={result} />}
        </div>
        <div className="reveal-actions">
          <button className="btn primary" onClick={start}>
            Play again →
          </button>
          <button className="btn" onClick={share}>
            Share best run
          </button>
        </div>
      </>
    );
  }

  if (loading || !situation) return <div className="spinner">Loading the gauntlet…</div>;

  // ---- Play / Reveal ----
  return (
    <>
      <div className="gauntlet-hud">
        <div className="hud-run">
          <span className="hud-flame">🔥</span>
          <span className="hud-num">{run}</span>
          <span className="hud-cap">run</span>
        </div>
        <div className="hud-best">best {Math.max(best, run)}</div>
      </div>

      <div className="card">
        <FieldDiagram sport={situation.sport} state={situation.game_state} />
        <div className="eyebrow">
          <span className="sport">{situation.sport}</span>
          <span>Call {run + 1}</span>
        </div>
        <div className="situation">{situation.situation_description}</div>

        {phase === "play" ? (
          <div className="options" style={{ marginTop: 14 }}>
            {situation.options.map((o) => (
              <button
                key={o.key}
                className="option"
                disabled={busy}
                onClick={() => pick(o.key)}
              >
                <span className="key">{o.key.toUpperCase()}</span>
                <span>{o.label}</span>
              </button>
            ))}
          </div>
        ) : (
          <div className="reveal">
            <div className="verdict-strip win" style={{ fontSize: 22 }}>
              ✓ Right call — on to {run + 1}.
            </div>
            <CallOptions situation={situation} result={result} />
            {result?.matchup && <div className="matchup">{result.matchup}</div>}
            <p className="ai-verdict" style={{ marginTop: 12 }}>
              {result?.ai_verdict}
            </p>
          </div>
        )}
      </div>

      {phase === "reveal" && (
        <div className="reveal-actions">
          <button className="btn primary" onClick={() => loadNext(seen)}>
            Next call →
          </button>
        </div>
      )}
    </>
  );
}

// Compact options display for the reveal, with Data / You / Coach marks.
function CallOptions({ situation, result }) {
  return (
    <div className="options" style={{ marginTop: 14 }}>
      {situation.options.map((o) => {
        const isBest = o.key === result.best_call;
        const isYou = o.key === result.your_choice;
        const isCoach = o.key === result.actual_call;
        return (
          <div
            key={o.key}
            className={`option ${isBest ? "best" : "wrong"} ${isCoach ? "coach" : ""}`}
          >
            <span className="key">{o.key.toUpperCase()}</span>
            <span>{o.label}</span>
            <span style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
              {isYou && <span className="badge b-you">You</span>}
              {isCoach && <span className="badge b-coach">Coach</span>}
              {isBest && <span className="badge b-best">Data</span>}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function MissCard({ result }) {
  return (
    <div className="miss-card">
      <div className="miss-line">
        You went <b>{result.your_choice.toUpperCase()}</b> — the data's call was{" "}
        <b className="data">{result.best_call_label}</b>.
      </div>
      {result.matchup && <div className="matchup">{result.matchup}</div>}
      <p className="ai-verdict" style={{ marginTop: 10 }}>
        {result.ai_verdict}
      </p>
    </div>
  );
}
