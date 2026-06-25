// A lightweight, on-brand scenario visual rendered as inline SVG (no image
// downloads — instant, scales crisply, stays fast). It shows the actual game
// state: a scoreboard (score / clock / situation) plus the ball (or runners)
// placed where the moment really sat. Football for NFL, half-court for NBA,
// a diamond for MLB (ready for the baseball v2).
export default function FieldDiagram({ sport, state }) {
  const Art = sport === "NBA" ? Court : sport === "MLB" ? Diamond : Field;
  return (
    <div className="scenario">
      {state && <Scoreboard state={state} />}
      <Art state={state} />
    </div>
  );
}

function Scoreboard({ state }) {
  const { your_score, opp_score, clock, tag } = state;
  const hasScore =
    typeof your_score === "number" && typeof opp_score === "number";
  const lead = !hasScore
    ? "tied"
    : your_score > opp_score
    ? "you"
    : your_score < opp_score
    ? "opp"
    : "tied";
  return (
    <div className="scoreboard">
      <div className={`sb-team ${lead === "you" ? "lead" : ""}`}>
        <span className="sb-abbr">YOU</span>
        <span className="sb-pts">{hasScore ? your_score : "–"}</span>
      </div>
      <div className="sb-center">
        {clock && <span className="sb-clock">{clock}</span>}
        {tag && <span className="sb-tag">{tag}</span>}
      </div>
      <div className={`sb-team ${lead === "opp" ? "lead" : ""}`}>
        <span className="sb-pts">{hasScore ? opp_score : "–"}</span>
        <span className="sb-abbr">OPP</span>
      </div>
    </div>
  );
}

function Field({ state }) {
  const yardLines = [70, 127, 184, 241, 298, 355, 412, 469, 526]; // 10..50..10
  const ballOn = state && typeof state.ball_on === "number" ? state.ball_on : null;
  // End zones occupy x 0–70 (your goal) and 570–640 (opp goal); 100 yds = 500px.
  const ballX = ballOn == null ? 320 : 70 + Math.max(0, Math.min(100, ballOn)) * 5;
  const losColor = state?.poss === "them" ? "#5cb3ff" : "#ffc23d";
  return (
    <svg
      className="scenario-art"
      viewBox="0 0 640 150"
      preserveAspectRatio="xMidYMid slice"
      role="img"
      aria-label="Football field"
    >
      <defs>
        <linearGradient id="turf" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#11271a" />
          <stop offset="1" stopColor="#0a1810" />
        </linearGradient>
        <radialGradient id="lights" cx="0.5" cy="0" r="0.9">
          <stop offset="0" stopColor="rgba(255,255,255,0.12)" />
          <stop offset="1" stopColor="rgba(255,255,255,0)" />
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="640" height="150" fill="url(#turf)" />
      <rect x="0" y="0" width="640" height="150" fill="url(#lights)" />
      {/* end zones — yours (orange), opponent's (gold) */}
      <rect x="0" y="0" width="70" height="150" fill="#ff5a1f" opacity="0.16" />
      <rect x="570" y="0" width="70" height="150" fill="#ffc23d" opacity="0.14" />
      <line x1="70" y1="0" x2="70" y2="150" stroke="rgba(255,255,255,0.5)" strokeWidth="2" />
      <line x1="570" y1="0" x2="570" y2="150" stroke="rgba(255,255,255,0.5)" strokeWidth="2" />
      {/* yard lines */}
      {yardLines.map((x) => (
        <line
          key={x}
          x1={x}
          y1="14"
          x2={x}
          y2="136"
          stroke="rgba(255,255,255,0.28)"
          strokeWidth={x === 298 ? 2.5 : 1.5}
        />
      ))}
      {/* hash marks */}
      {yardLines.map((x) =>
        [46, 104].map((y) => (
          <line key={`${x}-${y}`} x1={x - 4} y1={y} x2={x + 4} y2={y} stroke="rgba(255,255,255,0.22)" strokeWidth="1.5" />
        ))
      )}
      {/* line of scrimmage at the ball spot */}
      {ballOn != null && (
        <line x1={ballX} y1="10" x2={ballX} y2="140" stroke={losColor} strokeWidth="2.5" strokeDasharray="6 5" opacity="0.9" />
      )}
      {/* the ball */}
      <ellipse cx={ballX} cy="75" rx="11" ry="6.5" fill="#7a4a23" stroke="#e8d5b5" strokeWidth="1.2" />
      <line x1={ballX - 7} y1="75" x2={ballX + 7} y2="75" stroke="#e8d5b5" strokeWidth="1" />
    </svg>
  );
}

function Court({ state }) {
  const zones = {
    top: [320, 30],
    wing: [205, 52],
    inbound: [150, 122],
    post: [300, 95],
    corner: [120, 30],
  };
  const [bx, by] = zones[state?.zone] || [210, 75];
  return (
    <svg
      className="scenario-art"
      viewBox="0 0 640 150"
      preserveAspectRatio="xMidYMid slice"
      role="img"
      aria-label="Basketball half court"
    >
      <defs>
        <linearGradient id="hardwood" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#241a12" />
          <stop offset="1" stopColor="#17110b" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="640" height="150" fill="url(#hardwood)" />
      {/* key */}
      <rect x="270" y="40" width="100" height="70" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
      <circle cx="320" cy="75" r="26" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
      {/* three-point arc */}
      <path d="M 150 18 A 220 220 0 0 1 150 132" fill="none" stroke="rgba(255,255,255,0.24)" strokeWidth="2" />
      {/* hoop */}
      <line x1="368" y1="55" x2="368" y2="95" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
      <circle cx="356" cy="75" r="8" fill="none" stroke="#ff5a1f" strokeWidth="2.5" />
      {/* ball at the play's spot */}
      <circle cx={bx} cy={by} r="9" fill="#c0581f" stroke="#e8d5b5" strokeWidth="1" />
    </svg>
  );
}

function Diamond({ state }) {
  // bases: [1B, 2B, 3B] occupied; outs: 0–2. Ready for the baseball v2.
  const bases = state?.bases || [0, 0, 0];
  const outs = typeof state?.outs === "number" ? state.outs : null;
  const occ = (i, x, y) => (
    <rect
      x={x - 11}
      y={y - 11}
      width="22"
      height="22"
      transform={`rotate(45 ${x} ${y})`}
      fill={bases[i] ? "#ffc23d" : "none"}
      stroke="rgba(255,255,255,0.55)"
      strokeWidth="2"
    />
  );
  return (
    <svg
      className="scenario-art"
      viewBox="0 0 640 150"
      preserveAspectRatio="xMidYMid slice"
      role="img"
      aria-label="Baseball infield"
    >
      <defs>
        <linearGradient id="dirt" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#1c2a16" />
          <stop offset="1" stopColor="#12190d" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="640" height="150" fill="url(#dirt)" />
      {/* base paths */}
      <polygon
        points="320,128 250,75 320,22 390,75"
        fill="none"
        stroke="rgba(255,255,255,0.28)"
        strokeWidth="2"
      />
      {occ(0, 390, 75)}{/* 1B */}
      {occ(1, 320, 22)}{/* 2B */}
      {occ(2, 250, 75)}{/* 3B */}
      {/* home plate */}
      <rect x="311" y="119" width="18" height="18" transform="rotate(45 320 128)" fill="rgba(255,255,255,0.85)" />
      {/* outs */}
      {outs != null &&
        [0, 1].map((i) => (
          <circle key={i} cx={470 + i * 22} cy={128} r="7" fill={i < outs ? "#ff6b6b" : "none"} stroke="rgba(255,255,255,0.5)" strokeWidth="2" />
        ))}
    </svg>
  );
}
