import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function Landing() {
  const [email, setEmail] = useState("");
  const [state, setState] = useState("idle"); // idle | busy | done | error
  const [count, setCount] = useState(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetch("/api/waitlist/count")
      .then((r) => r.json())
      .then((d) => setCount(d.count))
      .catch(() => {});
  }, []);

  async function submit(e) {
    e.preventDefault();
    setState("busy");
    setMsg("");
    try {
      const r = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), source: "landing" }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Something went wrong");
      setCount(data.count);
      setState("done");
      setMsg(data.already ? "You're already on the list — see you at launch." : "You're in. We'll be in touch.");
    } catch (err) {
      setState("error");
      setMsg(String(err.message || err));
    }
  }

  return (
    <div className="lp">
      <header className="lp-nav">
        <span className="lp-brand">
          Oaksy<span style={{ color: "var(--accent)" }}>.</span>
        </span>
        <a className="btn ghost" href="/">
          Play now →
        </a>
      </header>

      <section className="lp-hero">
        <div className="lp-kicker">No betting. Just bragging rights.</div>
        <h1 className="lp-h1">
          Out-coach the coach.
          <br />
          <span className="lp-h1-accent">Settle it with data.</span>
        </h1>
        <p className="lp-sub">
          Every day, one real game decision drops — go for it, punt, kick? You pick
          in 30 seconds, then see what the coach actually did, the real outcome, and
          whether the data backed the call. The verdict isn't opinion: it's from{" "}
          <b style={{ color: "var(--ink)" }}>
            win-probability models across thousands of similar games
          </b>
          .
        </p>

        <form className="lp-form" onSubmit={submit}>
          <input
            type="email"
            required
            placeholder="you@email.com"
            value={email}
            disabled={state === "busy" || state === "done"}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button className="btn primary" disabled={state === "busy" || state === "done"}>
            {state === "busy" ? "…" : state === "done" ? "✓ On the list" : "Get launch updates"}
          </button>
        </form>
        {msg ? (
          <div className={`lp-msg ${state === "error" ? "err" : "ok"}`}>{msg}</div>
        ) : (
          <div className="lp-msg muted">
            {count != null && count > 0
              ? `Join ${count.toLocaleString()} fan${count === 1 ? "" : "s"} on the list.`
              : "Be the first fan on the list."}
          </div>
        )}
      </section>

      <WorkedExample />

      <section className="lp-steps">
        <Step n="1" title="Make the call">
          One real game decision. 30 seconds. Go for it, punt, or kick?
        </Step>
        <Step n="2" title="See the verdict">
          What the coach did, the outcome, and the data-backed AI take.
        </Step>
        <Step n="3" title="Build your score">
          Out-coach real coaches, keep your streak alive, climb the board.
        </Step>
      </section>

      <section className="lp-modes">
        <h2 className="lp-h2">Four ways to prove you know ball.</h2>
        <div className="lp-mode-grid">
          <Mode emoji="🏈" name="The Daily Call" desc="The 60-second habit. One real decision, every day." />
          <Mode emoji="⚔️" name="Debate Arena" desc="The week's hottest calls, bracketed. Best argument wins." />
          <Mode emoji="🏀" name="82-0 GM Mode" desc="Build an all-era team under the cap. Claude rates it." />
          <Mode emoji="🏆" name="Coach Score" desc="Your record vs real coaches. The number you brag about." />
        </div>
      </section>

      <section className="lp-cta">
        <h2 className="lp-h2">Think you know better than the coach?</h2>
        <p className="lp-sub" style={{ margin: "0 auto 22px" }}>Prove it. Your first call is waiting.</p>
        <a className="btn primary lp-cta-btn" href="/">
          Play the Daily Call →
        </a>
      </section>

      <footer className="lp-footer">
        Oaksy<span style={{ color: "var(--accent)" }}>.</span> — the arena where fans
        out-coach the coach, and settle it with data.
      </footer>
    </div>
  );
}

function WorkedExample() {
  return (
    <section className="lp-example">
      <div className="lp-example-tag">Here's a real one</div>
      <div className="we-card">
        <div className="we-q">
          Divisional Round. You just took the lead with 13 seconds left, kicking off
          to Patrick Mahomes — who has all three timeouts. How do you kick it?
        </div>
        <div className="we-opt">
          <span className="we-key">A</span> Kick it deep, normal kickoff
          <span className="we-badge coach">Coach did this</span>
        </div>
        <div className="we-opt best">
          <span className="we-key">B</span> Squib / pooch kick to bleed the clock
          <span className="we-badge data">Data says</span>
        </div>
        <div className="we-reveal">
          <b>What happened:</b> Buffalo kicked it deep. Mahomes reached field-goal
          range in 13 seconds, tied it, and Kansas City won in overtime.
          <div className="we-verdict">
            The models screamed squib: every second you bleed is a second the league's
            most dangerous closer can't use. Kicking deep handed him a clean catch with
            the clock stopped — the worst-case setup.
          </div>
        </div>
      </div>
      <div className="lp-example-foot">
        That's one day. There's a fresh call every morning — plus a Debate Arena and an
        82-0 GM Mode inside.
      </div>
    </section>
  );
}

const Step = ({ n, title, children }) => (
  <div className="lp-step">
    <div className="lp-step-n">{n}</div>
    <div className="lp-step-title">{title}</div>
    <div className="lp-step-body">{children}</div>
  </div>
);

const Mode = ({ emoji, name, desc }) => (
  <div className="lp-mode">
    <div className="lp-mode-emoji">{emoji}</div>
    <div className="lp-mode-name">{name}</div>
    <div className="lp-mode-desc">{desc}</div>
  </div>
);

createRoot(document.getElementById("landing")).render(
  <StrictMode>
    <Landing />
  </StrictMode>
);
