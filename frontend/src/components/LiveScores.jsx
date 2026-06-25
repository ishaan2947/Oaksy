import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

const SPORTS = ["MLB", "NFL", "NBA"];

// Live & recent scores — a "what's happening now" surface. Today's games are
// tomorrow's Daily Calls. Auto-refreshes while the tab is open.
export default function LiveScores() {
  const [sport, setSport] = useState("MLB");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(
    (showSpinner) => {
      if (showSpinner) setData(null);
      setError(null);
      api
        .scores(sport)
        .then(setData)
        .catch((e) => setError(e.message));
    },
    [sport]
  );

  useEffect(() => {
    load(true);
    const t = setInterval(() => load(false), 30000); // refresh every 30s
    return () => clearInterval(t);
  }, [load]);

  const games = data?.games || [];
  const live = games.filter((g) => g.state === "in").length;

  return (
    <>
      <div className="tabs" style={{ marginBottom: 16 }}>
        {SPORTS.map((s) => (
          <button
            key={s}
            className={`tab ${s === sport ? "active" : ""}`}
            onClick={() => setSport(s)}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="card">
        <div className="eyebrow" style={{ marginBottom: 4 }}>
          <span className="sport">{sport}</span>
          <span>Scoreboard</span>
          {live > 0 && <span className="live-pill">● {live} live</span>}
        </div>
        <p className="scores-tie">
          Today's games are tomorrow's calls — spot a gutsy decision live and it
          might be the next Daily Call.
        </p>

        {error && <p className="muted">{error}</p>}
        {!data && !error && <div className="spinner">Loading the scoreboard…</div>}
        {data && games.length === 0 && (
          <p className="muted">
            {data.note || `No ${sport} games on the board right now.`}
          </p>
        )}

        <div className="games">
          {games.map((g) => (
            <Game key={g.id} g={g} />
          ))}
        </div>
      </div>
    </>
  );
}

function Game({ g }) {
  const isLive = g.state === "in";
  const isFinal = g.state === "post";
  return (
    <div className={`game ${isLive ? "live" : ""}`}>
      <div className="game-status">
        {isLive && <span className="dot" />}
        <span className={isLive ? "gs-live" : "gs"}>{g.detail}</span>
      </div>
      <div className="game-rows">
        <TeamRow t={g.away} dim={isFinal && !g.away.winner} />
        <TeamRow t={g.home} dim={isFinal && !g.home.winner} />
      </div>
      {isLive && g.note && <div className="game-note">{g.note}</div>}
    </div>
  );
}

function TeamRow({ t, dim }) {
  return (
    <div className={`team-row ${dim ? "dim" : ""}`}>
      <span className="t-abbr">{t.abbr}</span>
      <span className="t-name">{t.name}</span>
      <span className="t-score">{t.score ?? "–"}</span>
    </div>
  );
}
