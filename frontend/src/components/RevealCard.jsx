import CommunitySplit from "./CommunitySplit";
import ShareCard from "./ShareCard";

// Shown after the pick (or timeout). Flips the card from question to verdict.
export default function RevealCard({ options, reveal, coachScore, onToast }) {
  let tone = "neutral";
  let line = "Time's up — here's how it played out.";
  if (reveal.your_choice) {
    if (reveal.you_beat_coach) {
      tone = "win";
      line = "You out-coached the coach.";
    } else if (reveal.you_were_correct) {
      tone = "win";
      line = "Right call.";
    } else {
      tone = "loss";
      line = "The coach got this one.";
    }
  }

  return (
    <div className="reveal">
      <div className={`verdict-strip ${tone}`}>{line}</div>

      <div className="options" style={{ marginTop: 14 }}>
        {options.map((o) => {
          const isBest = o.key === reveal.best_call;
          const isCoach = o.key === reveal.actual_call;
          const isYou = o.key === reveal.your_choice;
          const cls = [
            "option",
            isBest ? "best" : "wrong",
            isCoach ? "coach" : "",
          ].join(" ");
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

      <div className="block">
        <h4>What happened</h4>
        <p>{reveal.outcome}</p>
      </div>

      <div className="block">
        <h4>The verdict</h4>
        <p className="ai-verdict">{reveal.ai_verdict}</p>
      </div>

      <div className="block">
        <h4>The community split</h4>
        <CommunitySplit split={reveal.community_split} options={options} />
      </div>

      <ShareCard
        reveal={reveal}
        options={options}
        coachScore={coachScore}
        onToast={onToast}
      />
    </div>
  );
}
