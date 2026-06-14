// The growth engine: a screenshot-worthy result card.
export default function ShareCard({ reveal, options, coachScore, onToast }) {
  const yourLabel =
    options.find((o) => o.key === reveal.your_choice)?.label || null;
  const coachLabel = reveal.actual_call_label;

  const total = reveal.community_split.total || 0;
  const agree = reveal.your_choice
    ? Math.round(((reveal.community_split[reveal.your_choice] || 0) / total) * 100)
    : 0;

  let tone = "neutral";
  let headline = "You let the clock run out.";
  if (reveal.your_choice) {
    if (reveal.you_beat_coach) {
      tone = "win";
      headline = (
        <>
          I <span className="hl-win">out-coached</span> the coach.
        </>
      );
    } else if (reveal.you_were_correct) {
      tone = "win";
      headline = (
        <>
          I made the <span className="hl-win">right call</span>.
        </>
      );
    } else {
      tone = "loss";
      headline = (
        <>
          I got <span className="hl-loss">out-coached</span>.
        </>
      );
    }
  }

  function plainText() {
    const lead =
      tone === "win"
        ? reveal.you_beat_coach
          ? "I out-coached the coach on Oaksy."
          : "I made the right call on Oaksy."
        : tone === "loss"
        ? "The coach got me on Oaksy."
        : "I let the clock run out on Oaksy.";
    const detail = yourLabel
      ? ` I ${low(yourLabel)}. Coach ${low(coachLabel)}. ${agree}% of fans agreed with me.`
      : "";
    const score = coachScore
      ? ` My Coach Score: ${coachScore.win_rate}% (${coachScore.rank_label}).`
      : "";
    return `${lead}${detail}${score} oaksyapp.com`;
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(plainText());
      onToast?.("Result copied — go post it.");
    } catch {
      onToast?.("Copy failed — select and copy manually.");
    }
  }

  async function share() {
    if (navigator.share) {
      try {
        await navigator.share({ text: plainText() });
      } catch {
        /* user cancelled */
      }
    } else {
      copy();
    }
  }

  return (
    <>
      <div className="sharecard">
        <div className={`headline ${tone}`}>{headline}</div>
        {yourLabel && (
          <div className="sub">
            I {low(yourLabel)}. Coach {low(coachLabel)}.{" "}
            <b style={{ color: "var(--ink)" }}>{agree}%</b> of Oaksy fans agreed with me.
          </div>
        )}
        <div className="statline">
          <div className="stat">
            <div className="n">{coachScore ? `${coachScore.win_rate}%` : "—"}</div>
            <div className="l">Coach Score</div>
          </div>
          <div className="stat">
            <div className="n">{coachScore ? coachScore.beat_coach_count : "—"}</div>
            <div className="l">Times beat the coach</div>
          </div>
          <div className="stat">
            <div className="n">{coachScore ? coachScore.rank_label : "Rookie"}</div>
            <div className="l">Rank</div>
          </div>
        </div>
        <div className="watermark">Oaksy<span style={{ color: "var(--accent)" }}>.</span></div>
      </div>
      <div className="share-actions">
        <button className="btn primary" onClick={share}>
          Share result
        </button>
        <button className="btn ghost" onClick={copy}>
          Copy
        </button>
      </div>
    </>
  );
}

function low(s) {
  if (!s) return s;
  return s.charAt(0).toLowerCase() + s.slice(1);
}
