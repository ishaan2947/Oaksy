import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import Timer from "./Timer";
import RevealCard from "./RevealCard";
import FieldDiagram from "./FieldDiagram";

// All three sports. We keep NBA to genuinely clean, binary coaching calls (foul
// up 3, pull the rebounder, 2-for-1) — the kind anyone can judge — not play
// design or rotations. MLB has the cleanest decision points of all (bunt, IBB,
// infield in, closer usage), per the Reddit feedback.
const SPORTS = ["NFL", "NBA", "MLB"];

export default function DailyCall({ sport, onSport, coachScore, onPicked, onToast }) {
  const [situation, setSituation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [phase, setPhase] = useState("play"); // play | reveal
  const [reveal, setReveal] = useState(null);
  const [reasoning, setReasoning] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [timeUp, setTimeUp] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    setPhase("play");
    setReveal(null);
    setReasoning("");
    setTimeUp(false);
    api
      .daily(sport)
      .then((s) => setSituation(s))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sport]);

  useEffect(() => {
    load();
  }, [load]);

  async function pick(choice) {
    if (submitting || phase === "reveal") return;
    setSubmitting(true);
    try {
      const r = await api.submitPick({
        situation_id: situation.id,
        choice,
        reasoning: reasoning.trim() || null,
      });
      setReveal(r);
      setPhase("reveal");
      onPicked?.();
    } catch (e) {
      onToast?.(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  // The 30-second clock is a pace-setter, not a guillotine. When it runs out we
  // don't reveal the answer or lock the user out — their call still counts.
  // (Reddit feedback: "I can't do anything in 30 seconds.")
  function expire() {
    if (phase === "reveal") return;
    setTimeUp(true);
  }

  if (loading) return <div className="spinner">Loading today's call…</div>;
  if (error)
    return (
      <div className="card">
        <p className="muted">Couldn't load the Daily Call: {error}</p>
        <button className="btn" onClick={load} style={{ marginTop: 12 }}>
          Retry
        </button>
      </div>
    );

  return (
    <>
      {SPORTS.length > 1 && (
        <div className="tabs" style={{ marginBottom: 16 }}>
          {SPORTS.map((s) => (
            <button
              key={s}
              className={`tab ${s === sport ? "active" : ""}`}
              onClick={() => onSport(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="card">
        <FieldDiagram sport={situation.sport} state={situation.game_state} />
        <div className="eyebrow">
          <span className="sport">{situation.sport}</span>
          <span>The Daily Call</span>
          {situation.week ? <span>· {situation.week}</span> : null}
          {phase === "play" && (
            <Timer seconds={30} running onExpire={expire} />
          )}
        </div>

        <div className="situation">{situation.situation_description}</div>

        <div className="frame-note">
          Real game, real outcome. The “right call” is set by{" "}
          <b>win-probability models across thousands of similar situations</b> — not
          opinion.
        </div>

        {phase === "play" ? (
          <>
            {timeUp && (
              <div className="no-rush">
                No rush — take the time you need. Your call still counts.
              </div>
            )}
            <div className="options">
              {situation.options.map((o) => (
                <button
                  key={o.key}
                  className="option"
                  disabled={submitting}
                  onClick={() => pick(o.key)}
                >
                  <span className="key">{o.key.toUpperCase()}</span>
                  <span>{o.label}</span>
                </button>
              ))}
            </div>
            <textarea
              className="reasoning"
              placeholder="Make your case (optional) — strong arguments win the Debate Arena."
              value={reasoning}
              maxLength={600}
              onChange={(e) => setReasoning(e.target.value)}
            />
          </>
        ) : (
          <RevealCard
            options={situation.options}
            reveal={reveal}
            coachScore={coachScore}
            onToast={onToast}
          />
        )}
      </div>

      {phase === "reveal" && (
        <div className="center" style={{ marginTop: 18 }}>
          <button className="btn" onClick={load}>
            Next call →
          </button>
        </div>
      )}
    </>
  );
}
