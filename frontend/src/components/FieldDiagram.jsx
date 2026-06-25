// A lightweight, on-brand scenario visual rendered as inline SVG (no image
// downloads — instant, scales crisply, stays fast). Football field for NFL,
// half-court for NBA.
export default function FieldDiagram({ sport }) {
  return sport === "NBA" ? <Court /> : <Field />;
}

function Field() {
  const yardLines = [70, 127, 184, 241, 298, 355, 412, 469, 526]; // 10..50..10
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
      {/* end zones */}
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
      {/* the ball */}
      <ellipse cx="320" cy="75" rx="11" ry="6.5" fill="#7a4a23" stroke="#e8d5b5" strokeWidth="1.2" />
      <line x1="313" y1="75" x2="327" y2="75" stroke="#e8d5b5" strokeWidth="1" />
    </svg>
  );
}

function Court() {
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
      {/* ball */}
      <circle cx="210" cy="75" r="9" fill="#c0581f" stroke="#e8d5b5" strokeWidth="1" />
    </svg>
  );
}
