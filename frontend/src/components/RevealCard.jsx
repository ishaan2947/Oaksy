import CommunitySplit from "./CommunitySplit";
import ShareCard from "./ShareCard";

// Shown after the pick (or timeout). Flips the card from question to verdict.
// Order is deliberate: lead with the *data* (win probability per call), say how
// clear-cut it was, then show what actually happened — kept separate, with a
// "process, not result" note — so the grade never reads as hindsight or opinion.
export default function RevealCard({ options, reveal, coachScore, confidence, onToast }) {
  const odds = reveal.win_probabilities;
  const hasOdds = odds && options.every((o) => typeof odds[o.key] === "number");

  // How clear-cut was the call? Gap between the best option and the next best.
  let clarity = null;
  let yourGap = null;
  if (hasOdds) {
    const sorted = options.map((o) => odds[o.key]).sort((a, b) => b - a);
    const gap = sorted[0] - (sorted[1] ?? sorted[0]);
    clarity =
      gap >= 12
        ? { cls: "strong", label: "No-brainer", note: "The model is emphatic here." }
        : gap >= 5
        ? { cls: "edge", label: "Clear edge", note: "The data leans one way." }
        : { cls: "coinflip", label: "Coin flip", note: "Even the analysts split on this one." };
    if (reveal.your_choice && typeof odds[reveal.your_choice] === "number") {
      yourGap = odds[reveal.best_call] - odds[reveal.your_choice];
    }
  }

  let tone = "neutral";
  let line = "Time's up — here's how it played out.";
  if (reveal.your_choice) {
    if (reveal.you_beat_coach) {
      tone = "win";
      line = "You out-coached the coach.";
    } else if (reveal.you_were_correct) {
      tone = "win";
      line = "Right call.";
    } else if (yourGap != null && yourGap <= 4) {
      tone = "neutral";
      line = "Defensible — it's basically a coin flip.";
    } else {
      tone = "loss";
      line = "The coach got this one.";
    }
  }

  const streak = coachScore?.current_streak;

  // "How you stacked up" — share of the crowd that found the data's call.
  // Pure social proof from the community split; shown once enough have played.
  const split = reveal.community_split || {};
  const total = split.total || 0;
  const rightPct =
    total > 0 ? Math.round(((split[reveal.best_call] || 0) / total) * 100) : null;
  const showStacked = total >= 4 && rightPct != null && reveal.your_choice;

  // Immediate Sharp Score feedback for the call you just locked in.
  let sharp = null;
  if (confidence && reveal.your_choice && typeof reveal.you_were_correct === "boolean") {
    const pts = reveal.you_were_correct ? confidence : -confidence;
    const word = { 1: "leaned", 2: "were confident", 3: "locked it in" }[confidence];
    sharp = {
      pts,
      good: pts > 0,
      text: `You ${word} and ${reveal.you_were_correct ? "nailed it" : "missed"}.`,
    };
  }

  return (
    <div className="reveal">
      {reveal.matchup && <div className="matchup">{reveal.matchup}</div>}
      <div className={`verdict-strip ${tone}`}>{line}</div>
      {sharp && (
        <div className={`sharp-delta ${sharp.good ? "good" : "bad"}`}>
          <b>{sharp.pts > 0 ? `+${sharp.pts}` : sharp.pts} Sharp</b>
          <span>{sharp.text}</span>
        </div>
      )}

      {hasOdds ? (
        <div className="block">
          <div className="odds-head">
            <h4>What the numbers say</h4>
            {clarity && <span className={`clarity ${clarity.cls}`}>{clarity.label}</span>}
          </div>
          <p className="odds-sub">
            Win probability for each call — from{" "}
            <b>thousands of similar situations</b> that already played out, figured
            before anyone knew how this game ended. {clarity?.note}
          </p>
          <div className="odds">
            {options.map((o) => {
              const wp = odds[o.key];
              const isBest = o.key === reveal.best_call;
              const isCoach = o.key === reveal.actual_call;
              const isYou = o.key === reveal.your_choice;
              return (
                <div
                  key={o.key}
                  className={`odds-row ${isBest ? "best" : ""} ${isCoach ? "coach" : ""}`}
                >
                  <span className="key">{o.key.toUpperCase()}</span>
                  <div className="odds-main">
                    <div className="odds-label">
                      <span>{o.label}</span>
                      <span className="odds-badges">
                        {isYou && <span className="badge b-you">You</span>}
                        {isCoach && <span className="badge b-coach">Coach</span>}
                        {isBest && <span className="badge b-best">Data pick</span>}
                      </span>
                    </div>
                    <div className="odds-bar">
                      <div
                        className={`odds-fill ${isBest ? "best" : ""}`}
                        style={{ width: `${wp}%` }}
                      />
                    </div>
                  </div>
                  <span className="odds-pct">{wp}%</span>
                </div>
              );
            })}
          </div>
          <details className="grade-explainer">
            <summary>How is this graded?</summary>
            <p>
              These percentages are real base rates — the share of games that were
              won from this exact kind of spot, pooled across thousands of seasons
              of play-by-play. It's the same win-probability math behind ESPN's live
              graph and the famous NFL "4th-down bot." We can't replay <i>this</i>{" "}
              game with the other call — but we don't need to. The decision is
              judged against everything that's already happened, not a guess about
              one alternate ending.
            </p>
          </details>
        </div>
      ) : (
        <div className="options" style={{ marginTop: 14 }}>
          {options.map((o) => {
            const isBest = o.key === reveal.best_call;
            const isCoach = o.key === reveal.actual_call;
            const isYou = o.key === reveal.your_choice;
            const cls = ["option", isBest ? "best" : "wrong", isCoach ? "coach" : ""].join(" ");
            return (
              <div key={o.key} className={cls}>
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
      )}

      <div className="block">
        <h4>What actually happened</h4>
        <p>{reveal.outcome}</p>
        <div className="process-note">
          <b>Process, not result.</b> The grade comes from the model above — not from
          how this one play ended. A great call can still lose, and a bad call can
          still get lucky. You're scored on the decision, not the dice.
        </div>
      </div>

      <div className="block">
        <h4>The verdict</h4>
        <p className="ai-verdict">{reveal.ai_verdict}</p>
      </div>

      <div className="block">
        <h4>The community split</h4>
        <CommunitySplit split={reveal.community_split} options={options} />
        {showStacked && (
          <div className="stacked">
            <span className="stacked-pct">{rightPct}%</span>
            <span className="stacked-txt">
              of coaches found the data's call.{" "}
              {reveal.you_were_correct
                ? "You're one of them."
                : "You missed it — you're in good company."}
            </span>
          </div>
        )}
      </div>

      {streak > 0 && (
        <div className="streak-nudge">
          🔥 {streak}-day streak — a fresh call drops every morning. Keep it alive.
        </div>
      )}

      <ShareCard
        reveal={reveal}
        options={options}
        coachScore={coachScore}
        onToast={onToast}
      />
    </div>
  );
}
