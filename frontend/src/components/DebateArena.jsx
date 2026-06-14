import { useEffect, useState } from "react";
import { api } from "../api";
import CommunitySplit from "./CommunitySplit";

export default function DebateArena({ user, onLogin, onToast }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .debate()
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

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

  if (data.situations.length === 0) {
    return (
      <div className="card">
        <div className="section-title">The Debate Arena</div>
        <p className="muted">
          No debates yet this week. Make a Daily Call <i>with your reasoning</i> and
          it can land in the bracket.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="eyebrow" style={{ marginBottom: 14 }}>
        <span>The Debate Arena</span>
        <span>· {data.week_label}</span>
      </div>

      {data.situations.map((s, i) => (
        <div className="card debate-sit" key={s.situation_id}>
          <div className="eyebrow">
            <span className="sport">{s.sport}</span>
            <span>Most debated</span>
          </div>
          <div className="situation" style={{ fontSize: 19 }}>
            {s.situation_description}
          </div>

          <CommunitySplit split={s.community_split} options={s.options} />

          <div style={{ marginTop: 14 }}>
            <h4
              style={{
                fontSize: 12,
                textTransform: "uppercase",
                letterSpacing: "0.14em",
                color: "var(--ink-faint)",
                margin: "0 0 4px",
              }}
            >
              Best reasoning wins
            </h4>
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
          </div>
        </div>
      ))}
    </>
  );
}
