// "47% went for it, 53% punted" — instant social feel, zero content required.
export default function CommunitySplit({ split, options }) {
  const total = split.total || 0;
  const pct = (n) => (total ? Math.round((n / total) * 100) : 0);
  const segs = options
    .map((o) => ({ key: o.key, label: o.label, n: split[o.key] || 0, p: pct(split[o.key] || 0) }))
    .filter((s) => s.n > 0);

  if (total === 0) {
    return <p className="muted">Be the first to make this call.</p>;
  }

  return (
    <div className="split">
      <div className="split-bar">
        {segs.map((s) => (
          <div
            key={s.key}
            className={`split-seg ${s.key}`}
            style={{ width: `${s.p}%` }}
            title={`${s.label}: ${s.p}%`}
          >
            {s.p >= 12 ? `${s.p}%` : ""}
          </div>
        ))}
      </div>
      <div className="split-legend">
        {options.map((o) => (
          <span key={o.key}>
            <i className={`swatch`} style={{ background: `var(--${swatch(o.key)})` }} />
            {o.label} · {pct(split[o.key] || 0)}%
          </span>
        ))}
      </div>
    </div>
  );
}

function swatch(key) {
  return key === "a" ? "accent" : key === "b" ? "blue" : key === "c" ? "gold" : "purple";
}
