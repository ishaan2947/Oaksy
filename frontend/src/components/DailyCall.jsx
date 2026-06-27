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

const SPORT_TEASER = {
  NFL: "A real coaching decision from an NFL game.",
  NBA: "A real end-game decision from an NBA game.",
  MLB: "A real managerial decision from an MLB game.",
};

export default function DailyCall({
  sport,
  onSport,
  coachScore,
  onPicked,
  onToast,
  challenge,
  onExitChallenge,
}) {
  const [situation, setSituation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // intro → play → reveal. Intro lets the user start the 30s clock on their
  // terms instead of being dropped straight into a countdown.
  const [phase, setPhase] = useState("intro");
  const [reveal, setReveal] = useState(null);
  const [reasoning, setReasoning] = useState("");
  const [selected, setSelected] = useState(null); // option chosen, not yet locked in
  const [confidence, setConfidence] = useState(2); // 1 lean · 2 confident · 3 lock it
  const [pickedConfidence, setPickedConfidence] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [timeUp, setTimeUp] = useState(false);

  const load = useCallback(() => {
    setError(null);
    setPhase("intro");
    setReveal(null);
    setReasoning("");
    setSelected(null);
    setConfidence(2);
    setPickedConfidence(null);
    setTimeUp(false);
    if (challenge) {
      // Challenge mode: play the exact situation the friend was challenged on.
      setSituation(challenge.situation);
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .daily(sport)
      .then((s) => setSituation(s))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sport, challenge]);

  useEffect(() => {
    load();
  }, [load]);

  function begin() {
    setTimeUp(false);
    setPhase("play");
  }

  async function pick(choice) {
    if (submitting || phase === "reveal") return;
    setSubmitting(true);
    try {
      const r = await api.submitPick({
        situation_id: situation.id,
        choice,
        reasoning: reasoning.trim() || null,
        confidence,
      });
      setReveal(r);
      setPickedConfidence(confidence);
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

  async function challengeFriend() {
    try {
      const { id } = await api.createChallenge({
        kind: "daily",
        situation_id: situation.id,
        choice: reveal.your_choice,
        confidence: pickedConfidence || undefined,
        challenger_name: coachScore?.display_name || "A challenger",
      });
      const url = `${window.location.origin}${window.location.pathname}?c=${id}`;
      const text = "Can you out-coach me on today's Oaksy call?";
      if (navigator.share) {
        await navigator.share({ title: "Oaksy", text, url });
      } else {
        await navigator.clipboard.writeText(url);
        onToast?.("Challenge link copied — send it to a friend.");
      }
    } catch (e) {
      if (e?.name !== "AbortError") onToast?.(e.message || "Couldn't create challenge");
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

  const opt = (k) => situation?.options.find((o) => o.key === k)?.label || k?.toUpperCase();

  return (
    <>
      {challenge ? (
        <div className="challenge-banner">
          <span className="cb-tag">⚔️ Challenge</span>
          <span>
            <b>{challenge.challenger_name}</b> challenged you — they went with{" "}
            <b>{opt(challenge.challenger_choice)}</b>. Can you do better?
          </span>
          <button className="linkbtn" onClick={onExitChallenge}>
            Play today's instead
          </button>
        </div>
      ) : (
        SPORTS.length > 1 && (
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
        )
      )}

      <div className="card">
        <FieldDiagram sport={situation.sport} state={situation.game_state} />
        <div className="eyebrow">
          <span className="sport">{situation.sport}</span>
          <span>The Daily Call</span>
          {phase === "play" && <Timer seconds={30} running onExpire={expire} />}
        </div>

        {phase === "intro" ? (
          <div className="intro">
            <h2 className="intro-title">
              {challenge ? `Beat ${challenge.challenger_name}'s call.` : "Make the call before the coach did."}
            </h2>
            <p className="intro-sub">
              {SPORT_TEASER[situation.sport] || "A real coaching decision."} You'll
              get the situation and 30 seconds on the clock — then see the real call,
              what the data said, and how the crowd voted.
            </p>
            <button className="btn primary intro-start" onClick={begin}>
              {challenge ? "Take the challenge →" : "Start today's call →"}
            </button>
            <p className="intro-foot">No account needed. ~30 seconds.</p>
          </div>
        ) : (
          <>
            <div className="situation">{situation.situation_description}</div>

            <div className="frame-note">
              Real game, real outcome. The “right call” is set by{" "}
              <b>win-probability models across thousands of similar situations</b> —
              not opinion. We hide the teams until after you pick, so you decide on
              the merits.
            </div>

            {phase === "play" ? (
              <>
                {timeUp && (
                  <div className="no-rush">
                    No rush — take the time you need. Your call still counts.
                  </div>
                )}
                <div className="conf">
                  <span className="conf-label">How sure are you?</span>
                  <div className="conf-chips">
                    {[
                      [1, "Lean", "×1"],
                      [2, "Confident", "×2"],
                      [3, "Lock it", "×3"],
                    ].map(([v, label, mult]) => (
                      <button
                        key={v}
                        type="button"
                        className={`conf-chip ${confidence === v ? "sel" : ""}`}
                        onClick={() => setConfidence(v)}
                        disabled={submitting}
                      >
                        {label} <b>{mult}</b>
                      </button>
                    ))}
                  </div>
                </div>
                <div className="options">
                  {situation.options.map((o) => (
                    <button
                      key={o.key}
                      className={`option ${selected === o.key ? "sel" : ""}`}
                      disabled={submitting}
                      onClick={() => setSelected(o.key)}
                    >
                      <span className="key">{o.key.toUpperCase()}</span>
                      <span>{o.label}</span>
                      {selected === o.key && <span className="opt-check">✓</span>}
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
                <button
                  className="btn primary lock-in"
                  disabled={!selected || submitting}
                  onClick={() => pick(selected)}
                >
                  {submitting
                    ? "Locking in…"
                    : selected
                    ? "Lock in my call →"
                    : "Pick an option above"}
                </button>
              </>
            ) : (
              <RevealCard
                options={situation.options}
                reveal={reveal}
                coachScore={coachScore}
                confidence={pickedConfidence}
                onToast={onToast}
              />
            )}
          </>
        )}
      </div>

      {phase === "reveal" && challenge && reveal && (
        <HeadToHead reveal={reveal} challenge={challenge} optLabel={opt} />
      )}

      {phase === "reveal" && (
        <div className="reveal-actions">
          {!challenge && reveal?.your_choice && (
            <button className="btn primary" onClick={challengeFriend}>
              ⚔️ Challenge a friend
            </button>
          )}
          {challenge ? (
            <button className="btn" onClick={onExitChallenge}>
              Play today's call →
            </button>
          ) : (
            <button className="btn" onClick={load}>
              Next call →
            </button>
          )}
        </div>
      )}
    </>
  );
}

function HeadToHead({ reveal, challenge, optLabel }) {
  const themCorrect = challenge.challenger_choice === reveal.best_call;
  const youCorrect = !!reveal.you_were_correct;
  const result =
    youCorrect === themCorrect
      ? "Dead even — you both made the same verdict."
      : youCorrect
      ? "You win this one. 🏆"
      : `${challenge.challenger_name} takes it.`;
  return (
    <div className="card h2h">
      <h4 className="block-label">Head to head</h4>
      <div className="h2h-rows">
        <div className={`h2h-row ${youCorrect ? "win" : ""}`}>
          <span className="h2h-who">You</span>
          <span className="h2h-pick">{optLabel(reveal.your_choice)}</span>
          <span className="h2h-mark">{youCorrect ? "✓ data's call" : "✗ missed"}</span>
        </div>
        <div className={`h2h-row ${themCorrect ? "win" : ""}`}>
          <span className="h2h-who">{challenge.challenger_name}</span>
          <span className="h2h-pick">{optLabel(challenge.challenger_choice)}</span>
          <span className="h2h-mark">{themCorrect ? "✓ data's call" : "✗ missed"}</span>
        </div>
      </div>
      <div className="h2h-result">{result}</div>
    </div>
  );
}
