import { useState } from "react";
import { api } from "../api";

// Temporary user-study survey. Remove this component + its tab when the study
// wraps. Answers post to /api/survey; read results at /api/survey/summary.
const SCALES = [
  { id: "use_regularly", label: "How likely are you to use Oaksy regularly?", low: "Never", high: "Every day" },
  { id: "fun", label: "How fun is it right now?", low: "Boring", high: "Addicting" },
  { id: "clarity", label: "How clear is what the app actually does?", low: "Confusing", high: "Crystal clear" },
  { id: "recommend", label: "How likely are you to tell a friend about it?", low: "No way", high: "Definitely" },
];

const TEXTS = [
  { id: "best", label: "What's the best thing about it?", ph: "What clicked for you…" },
  { id: "worst", label: "What's confusing, annoying, or just bad?", ph: "Be brutal — it helps most…" },
  { id: "bugs", label: "Anything broken, buggy, or glitchy? (what + where)", ph: "Tell me what broke so I can fix it…" },
  { id: "missing", label: "What would make you use it every single day?", ph: "The one thing that's missing…" },
];

const MODES = ["Daily Call", "Gauntlet", "GM Mode", "Debate", "Scores"];

export default function Survey({ onToast }) {
  const [answers, setAnswers] = useState({});
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  const set = (id, val) => setAnswers((a) => ({ ...a, [id]: val }));

  async function submit() {
    const hasAny =
      SCALES.some((s) => answers[s.id]) ||
      TEXTS.some((t) => (answers[t.id] || "").trim()) ||
      answers.fav_mode;
    if (!hasAny) return onToast?.("Answer at least one question first.");
    setBusy(true);
    try {
      await api.submitSurvey(answers);
      setDone(true);
    } catch (e) {
      onToast?.(e.message);
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <div className="card survey-done">
        <div className="survey-check">🙏</div>
        <h2>Thank you — seriously.</h2>
        <p className="muted">
          This is exactly the kind of feedback that shapes what gets built next.
          You're the reason Oaksy gets better.
        </p>
      </div>
    );
  }

  return (
    <div className="card survey">
      <div className="survey-head">
        <span className="survey-badge">User study</span>
        <h2>Help shape Oaksy</h2>
        <p className="muted">
          ~1 minute, totally anonymous. Answer what you want — every bit helps.
        </p>
      </div>

      {SCALES.map((s) => (
        <div className="survey-q" key={s.id}>
          <div className="survey-label">{s.label}</div>
          <div className="scale">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                className={`scale-dot ${answers[s.id] === n ? "sel" : ""}`}
                onClick={() => set(s.id, n)}
              >
                {n}
              </button>
            ))}
          </div>
          <div className="scale-ends">
            <span>{s.low}</span>
            <span>{s.high}</span>
          </div>
        </div>
      ))}

      <div className="survey-q">
        <div className="survey-label">Which mode did you like most?</div>
        <div className="survey-modes">
          {MODES.map((m) => (
            <button
              key={m}
              className={`mode-chip ${answers.fav_mode === m ? "sel" : ""}`}
              onClick={() => set("fav_mode", m)}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {TEXTS.map((t) => (
        <div className="survey-q" key={t.id}>
          <div className="survey-label">{t.label}</div>
          <textarea
            className="reasoning"
            placeholder={t.ph}
            maxLength={1000}
            value={answers[t.id] || ""}
            onChange={(e) => set(t.id, e.target.value)}
          />
        </div>
      ))}

      <button
        className="btn primary"
        style={{ width: "100%", marginTop: 8 }}
        disabled={busy}
        onClick={submit}
      >
        {busy ? "Sending…" : "Submit feedback"}
      </button>
    </div>
  );
}
