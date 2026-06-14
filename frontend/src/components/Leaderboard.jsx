import { useEffect, useState } from "react";
import { api } from "../api";

export default function Leaderboard({ highlight }) {
  const [rows, setRows] = useState(null);

  useEffect(() => {
    api.leaderboard().then(setRows).catch(() => setRows([]));
  }, []);

  if (!rows) return <div className="spinner">Loading leaderboard…</div>;
  if (rows.length === 0)
    return <p className="muted">No ranked coaches yet — make some calls.</p>;

  return (
    <div>
      {rows.map((r, i) => (
        <div
          className="lb-row"
          key={`${r.display_name}-${i}`}
          style={
            r.display_name === highlight
              ? { borderColor: "var(--gold)" }
              : undefined
          }
        >
          <span className={`lb-rank ${i < 3 ? "top" : ""}`}>{i + 1}</span>
          <span className="lb-name">{r.display_name}</span>
          <span className="lb-rate" style={{ color: "var(--green)" }}>
            {r.win_rate}%
          </span>
          <span className="lb-calls">{r.total_calls} calls</span>
        </div>
      ))}
    </div>
  );
}
