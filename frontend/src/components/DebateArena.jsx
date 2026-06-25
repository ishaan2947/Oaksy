import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import CommunitySplit from "./CommunitySplit";

export default function DebateArena({ user, onLogin, onToast }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const reload = useCallback(() => {
    api.debate().then(setData).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  async function vote(sitIndex, pickId) {
    if (!user) {
      onLogin();
      return;
    }
    try {
      const res = await api.vote(pickId);
      setData((d) => {
        const next = structuredClone(d);
        const posts = next.situations[sitIndex].posts;
        const p = posts.find((x) => x.pick_id === pickId);
        if (p) {
          p.votes = res.votes;
          p.you_voted = res.you_voted;
        }
        posts.sort((a, b) => b.votes - a.votes);
        return next;
      });
    } catch (e) {
      onToast?.(e.message);
    }
  }

  if (error) return <div className="card"><p className="muted">{error}</p></div>;
  if (!data) return <div className="spinner">Loading the Debate Arena…</div>;

  return (
    <>
      <div className="eyebrow" style={{ marginBottom: 14 }}>
        <span>The Debate Arena</span>
        <span>· {data.week_label}</span>
      </div>

      <div className="card how-it-works">
        <h4>How the Debate Arena works</h4>
        <ol>
          <li>Make a call on a situation below and <b>write why</b>.</li>
          <li>Your argument shows up here for everyone to read.</li>
          <li><b>Upvote</b> the takes you agree with.</li>
          <li>The best reasoning rises to the top each week.</li>
        </ol>
      </div>

      {data.situations.length === 0 ? (
        <div className="card">
          <p className="muted">
            No debates yet this week. Make a Daily Call <i>with your reasoning</i> —
            or add a take below — and it lands here.
          </p>
        </div>
      ) : (
        data.situations.map((s, i) => (
          <div className="card debate-sit" key={s.situation_id}>
            <div className="eyebrow">
              <span className="sport">{s.sport}</span>
              <span>Most debated</span>
            </div>
            <div className="situation" style={{ fontSize: 19 }}>
              {s.situation_description}
            </div>
            {s.matchup && <div className="matchup">{s.matchup}</div>}

            <CommunitySplit split={s.community_split} options={s.options} />

            <div style={{ marginTop: 14 }}>
              <h4 className="block-label">Best reasoning wins</h4>
              {s.posts.length === 0 && (
                <p className="muted">No arguments yet — be the first to make the case.</p>
              )}
              {s.posts.map((p) => (
                <div className="post" key={p.pick_id}>
                  <button
                    className={`vote ${p.you_voted ? "voted" : ""}`}
                    onClick={() => vote(i, p.pick_id)}
                    title={user ? "Vote for this argument" : "Sign in to vote"}
                  >
                    <span className="up">▲</span>
                    <span className="cnt">{p.votes}</span>
                  </button>
                  <div className="body">
                    <div className="who">
                      {p.author}
                      <span className="pos">picked: {p.choice_label}</span>
                    </div>
                    <div className="arg">{p.reasoning}</div>
                  </div>
                </div>
              ))}

              <ArgueForm
                situation={s}
                user={user}
                onLogin={onLogin}
                onPosted={reload}
                onToast={onToast}
              />
            </div>
          </div>
        ))
      )}
    </>
  );
}

function ArgueForm({ situation, user, onLogin, onPosted, onToast }) {
  const [open, setOpen] = useState(false);
  const [choice, setChoice] = useState(null);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  if (!user) {
    return (
      <button className="btn argue-open" onClick={onLogin}>
        Sign in to add your take
      </button>
    );
  }
  if (!open) {
    return (
      <button className="btn argue-open" onClick={() => setOpen(true)}>
        + Add your take
      </button>
    );
  }

  async function submit() {
    if (!choice) return onToast?.("Pick the side you're arguing for.");
    if (text.trim().length < 1) return onToast?.("Write your argument first.");
    setBusy(true);
    try {
      await api.argue(situation.situation_id, { choice, reasoning: text.trim() });
      setText("");
      setChoice(null);
      setOpen(false);
      onPosted?.();
    } catch (e) {
      onToast?.(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="argue">
      <div className="argue-opts">
        {situation.options.map((o) => (
          <button
            key={o.key}
            className={`argue-chip ${choice === o.key ? "sel" : ""}`}
            onClick={() => setChoice(o.key)}
          >
            <b>{o.key.toUpperCase()}</b> {o.label}
          </button>
        ))}
      </div>
      <textarea
        className="reasoning"
        placeholder="Why is your call the right one? Make the case…"
        value={text}
        maxLength={600}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="argue-actions">
        <button className="btn" onClick={() => setOpen(false)}>
          Cancel
        </button>
        <button className="btn primary" onClick={submit} disabled={busy}>
          {busy ? "…" : "Post argument"}
        </button>
      </div>
      <p className="argue-note">
        Already made this call? We'll keep your pick and just attach your reasoning.
      </p>
    </div>
  );
}
