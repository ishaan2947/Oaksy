import Leaderboard from "./Leaderboard";

// The identity layer — your running record vs real coaches.
export default function CoachScore({ user, score, onLogin }) {
  if (!user) {
    return (
      <div className="card">
        <div className="section-title">Your Coach Score</div>
        <p className="muted">
          Sign in to build a record that spans every Daily Call, GM session, and
          Debate win — the number you brag about.
        </p>
        <button className="btn primary" style={{ marginTop: 14 }} onClick={onLogin}>
          Sign in to track your score
        </button>
        <div style={{ marginTop: 28 }}>
          <div className="section-title">This week's top coaches</div>
          <Leaderboard />
        </div>
      </div>
    );
  }

  if (!score) return <div className="spinner">Loading your score…</div>;

  return (
    <>
      <div className="card">
        <div className="eyebrow">
          <span>Coach Score</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div className="situation" style={{ margin: 0 }}>
            {score.display_name}
          </div>
          <span className="rank-pill">{score.rank_label}</span>
        </div>

        <div className="score-grid">
          <div className="score-tile">
            <div className="n" style={{ color: "var(--green)" }}>
              {score.win_rate}%
            </div>
            <div className="l">Win rate vs coaches</div>
          </div>
          <div className="score-tile">
            <div className="n" style={{ color: "var(--accent)" }}>
              {score.current_streak > 0 ? `🔥 ${score.current_streak}` : "—"}
            </div>
            <div className="l">
              Day streak{score.longest_streak > 0 ? ` · best ${score.longest_streak}` : ""}
            </div>
          </div>
          <div className="score-tile">
            <div className="n" style={{ color: "var(--gold)" }}>
              {score.beat_coach_count}
            </div>
            <div className="l">Times you beat the coach</div>
          </div>
          <div className="score-tile">
            <div className="n">{score.total_calls}</div>
            <div className="l">Calls made</div>
          </div>
          <div className="score-tile">
            <div className="n">{score.debate_wins}</div>
            <div className="l">Debate votes won</div>
          </div>
          <div className="score-tile">
            <div className="n" style={{ color: "var(--blue)" }}>
              {score.gm_teams > 0 ? score.gm_rating : "—"}
            </div>
            <div className="l">GM rating · {score.gm_rank_label}</div>
          </div>
          <div className="score-tile">
            <div className="n">{score.gm_teams}</div>
            <div className="l">82-0 teams built</div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 22 }}>
        <div className="section-title">This week's top coaches</div>
        <Leaderboard highlight={score.display_name} />
      </div>
    </>
  );
}
