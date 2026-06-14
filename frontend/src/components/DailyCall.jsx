import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import Timer from "./Timer";
import RevealCard from "./RevealCard";

const SPORTS = ["NFL", "NBA"];

export default function DailyCall({ sport, onSport, coachScore, onPicked, onToast }) {
  const [situation, setSituation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [phase, setPhase] = useState("play"); // play | reveal
  const [reveal, setReveal] = useState(null);
  const [reasoning, setReasoning] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    setPhase("play");
    setReveal(null);
    setReasoning("");
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

  async function expire() {
    if (phase === "reveal") return;
    try {
      const r = await api.reveal(situation.id);
      setReveal(r);
      setPhase("reveal");
    } catch (e) {
      onToast?.(e.message);
    }
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

      <div className="card">
        <div className="eyebrow">
          <span className="sport">{situation.sport}</span>
          <span>The Daily Call</span>
          {situation.week ? <span>· {situation.week}</span> : null}
          {phase === "play" && (
            <Timer seconds={30} running onExpire={expire} />
          )}
        </div>

        <div className="situation">{situation.situation_description}</div>

        {phase === "play" ? (
          <>
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
