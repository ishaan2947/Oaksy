import { useEffect, useState } from "react";
import { api } from "../api";

export default function GMMode({ onSubmitted, onToast, coachScore, challenge, onExitChallenge }) {
  const [spin, setSpin] = useState(challenge?.spin || null);
  const [selected, setSelected] = useState([]); // ordered list of player ids
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  // Challenge mode: build from the exact spin pool the friend was challenged on.
  useEffect(() => {
    if (challenge?.spin) {
      setSpin(challenge.spin);
      setSelected([]);
      setResult(null);
    }
  }, [challenge]);

  async function challengeFriend() {
    if (!spin || !result) return;
    try {
      const { id } = await api.createChallenge({
        kind: "gm",
        spin_id: spin.spin_id,
        player_ids: result.team.map((p) => p.id),
        score: result.score,
        challenger_name: coachScore?.display_name || "A challenger",
      });
      const url = `${window.location.origin}${window.location.pathname}?c=${id}`;
      const text = `My 82-0 team scored ${result.score}/100. Same player pool — can you beat it?`;
      if (navigator.share) await navigator.share({ title: "Oaksy 82-0", text, url });
      else {
        await navigator.clipboard.writeText(url);
        onToast?.("Challenge link copied — send it to a friend.");
      }
    } catch (e) {
      if (e?.name !== "AbortError") onToast?.(e.message || "Couldn't create challenge");
    }
  }

  async function doSpin() {
    setBusy(true);
    setResult(null);
    setSelected([]);
    try {
      const s = await api.gmSpin();
      setSpin(s);
    } catch (e) {
      onToast?.(e.message);
    } finally {
      setBusy(false);
    }
  }

  function toggle(id) {
    setSelected((sel) => {
      if (sel.includes(id)) return sel.filter((x) => x !== id);
      if (sel.length >= spin.roster_size) return sel;
      return [...sel, id];
    });
  }

  const pool = spin?.pool || [];
  const team = selected.map((id) => pool.find((p) => p.id === id)).filter(Boolean);
  const cost = team.reduce((sum, p) => sum + p.cost, 0);
  const positions = new Set(team.map((p) => p.pos));
  const hasG = positions.has("G");
  const hasC = positions.has("C");
  const cap = spin?.cap || 0;
  const overCap = cost > cap;
  const full = spin && selected.length === spin.roster_size;
  const legal = full && !overCap && hasG && hasC;

  async function lockIn() {
    if (!legal || busy) return;
    setBusy(true);
    try {
      const r = await api.gmSubmit({ spin_id: spin.spin_id, player_ids: selected });
      setResult(r);
      onSubmitted?.();
    } catch (e) {
      onToast?.(e.message);
    } finally {
      setBusy(false);
    }
  }

  // ---- Result screen ----
  if (result) {
    return (
      <GMResult
        result={result}
        onAgain={doSpin}
        onToast={onToast}
        challenge={challenge}
        onChallenge={challengeFriend}
        onExitChallenge={onExitChallenge}
      />
    );
  }

  // ---- Intro (no spin yet) ----
  if (!spin) {
    return (
      <div className="card">
        <div className="gm-intro">
          <div className="eyebrow center" style={{ justifyContent: "center" }}>
            <span className="sport">NBA</span>
            <span>82-0 GM Mode</span>
          </div>
          <div className="big">Build a team that goes 82-0.</div>
          <p className="muted" style={{ maxWidth: 460, margin: "0 auto" }}>
            Spin the wheel for a pool of legends from any era. Assemble a starting
            five under the salary cap, then let Claude rate whether it could really
            go undefeated.
          </p>
          <button
            className="btn primary"
            style={{ marginTop: 18, padding: "13px 26px", fontSize: 16 }}
            onClick={doSpin}
            disabled={busy}
          >
            {busy ? "Spinning…" : "🎲 Spin the wheel"}
          </button>
        </div>
      </div>
    );
  }

  // ---- Build screen ----
  return (
    <div className="card">
      {challenge && (
        <div className="challenge-banner" style={{ marginBottom: 14 }}>
          <span className="cb-tag">⚔️ Challenge</span>
          <span>
            <b>{challenge.challenger_name}</b> scored{" "}
            <b>{challenge.challenger_score}/100</b> from this exact pool. Beat it.
          </span>
          <button className="linkbtn" onClick={onExitChallenge}>
            Free play instead
          </button>
        </div>
      )}
      <div className="eyebrow">
        <span className="sport">NBA</span>
        <span>82-0 GM Mode</span>
      </div>

      <div className="gm-rules">
        <div className="meter-wrap">
          <div className="cap-meter">
            <div
              className={`cap-fill ${overCap ? "over" : ""}`}
              style={{ width: `${Math.min(100, (cost / cap) * 100)}%` }}
            />
          </div>
          <div className="cap-label">
            Cap: <b style={{ color: overCap ? "var(--red-text)" : undefined }}>{cost}</b> / {cap} ·{" "}
            {selected.length}/{spin.roster_size} starters
          </div>
        </div>
        <div className="req-chips">
          <span className={`req ${hasG ? "met" : ""}`}>Guard {hasG ? "✓" : "✗"}</span>
          <span className={`req ${hasC ? "met" : ""}`}>Center {hasC ? "✓" : "✗"}</span>
        </div>
      </div>

      <div className="pool-grid">
        {pool.map((p) => {
          const idx = selected.indexOf(p.id);
          const isSel = idx >= 0;
          const disabled = !isSel && full;
          return (
            <button
              key={p.id}
              className={`pcard ${isSel ? "sel" : ""}`}
              disabled={disabled}
              onClick={() => toggle(p.id)}
            >
              {isSel && <span className="pick-num">{idx + 1}</span>}
              <div className="row1">
                <span className={`pos ${p.pos}`}>{p.pos}</span>
                <span className="pname">{p.name}</span>
                <span className="cost">{p.cost} pts</span>
              </div>
              <div className="pmeta">{p.era}</div>
              <div className="ptag">{p.tag}</div>
            </button>
          );
        })}
      </div>

      <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
        <button className="btn primary" style={{ flex: 1 }} disabled={!legal || busy} onClick={lockIn}>
          {busy
            ? "Asking Claude…"
            : legal
            ? "Lock in roster →"
            : overCap
            ? "Over the cap"
            : !full
            ? `Pick ${spin.roster_size - selected.length} more`
            : !hasG
            ? "Need a guard"
            : "Need a center"}
        </button>
        <button className="btn ghost" disabled={busy} onClick={doSpin}>
          Re-spin
        </button>
      </div>
    </div>
  );
}

function GMResult({ result, onAgain, onToast, challenge, onChallenge, onExitChallenge }) {
  const grade =
    result.score >= 90 ? "win" : result.score >= 70 ? "neutral" : "loss";
  const themScore = challenge?.challenger_score;
  const h2hLine =
    themScore == null
      ? null
      : result.score > themScore
      ? `You win — ${result.score} to ${themScore}. 🏆`
      : result.score < themScore
      ? `${challenge.challenger_name} wins — ${themScore} to ${result.score}.`
      : `Dead tie at ${result.score}.`;

  async function share() {
    const text = `${result.share_line} oaksyapp.com`;
    try {
      if (navigator.share) await navigator.share({ text });
      else {
        await navigator.clipboard.writeText(text);
        onToast?.("Team copied — go post it.");
      }
    } catch {
      /* cancelled */
    }
  }

  return (
    <>
      <div className="card reveal">
        <div className="eyebrow">
          <span className="sport">NBA</span>
          <span>Claude's verdict</span>
        </div>
        <div className={`gm-score verdict-strip ${grade}`} style={{ margin: "8px 0" }}>
          {result.score}
          <small>/100</small>
        </div>
        <p className="ai-verdict" style={{ marginTop: 6 }}>
          {result.verdict}
        </p>

        <div className="gm-team-list">
          {result.team.map((p) => (
            <span className="gm-chip" key={p.id}>
              <span className={`pos ${p.pos}`}>{p.pos}</span>
              {p.name}
            </span>
          ))}
        </div>
        <div className="cap-label" style={{ marginTop: 10 }}>
          Team cost: <b>{result.total_cost}</b> / {result.cap}
        </div>

        {h2hLine && (
          <div className="h2h" style={{ marginTop: 14 }}>
            <h4 className="block-label">Head to head</h4>
            <div className="h2h-rows">
              <div className={`h2h-row ${result.score >= themScore ? "win" : ""}`}>
                <span className="h2h-who">You</span>
                <span className="h2h-mark">{result.score}/100</span>
              </div>
              <div className={`h2h-row ${themScore > result.score ? "win" : ""}`}>
                <span className="h2h-who">{challenge.challenger_name}</span>
                <span className="h2h-mark">{themScore}/100</span>
              </div>
            </div>
            <div className="h2h-result">{h2hLine}</div>
          </div>
        )}
      </div>

      <div className="sharecard" style={{ marginTop: 18 }}>
        <div className={`headline ${grade}`}>
          {result.score >= 90 ? (
            <>
              An <span className="hl-win">82-0</span> juggernaut.
            </>
          ) : result.score >= 70 ? (
            "A serious contender."
          ) : (
            <>
              Won't go <span className="hl-loss">undefeated</span>.
            </>
          )}
        </div>
        <div className="sub">{result.share_line}</div>
        <div className="watermark">
          Oaksy<span style={{ color: "var(--accent)" }}>.</span>
        </div>
      </div>

      <div className="share-actions">
        <button className="btn primary" onClick={onChallenge}>
          ⚔️ Challenge a friend
        </button>
        <button className="btn ghost" onClick={share}>
          Share team
        </button>
        {challenge ? (
          <button className="btn ghost" onClick={onExitChallenge}>
            Free play →
          </button>
        ) : (
          <button className="btn ghost" onClick={onAgain}>
            🎲 Spin again
          </button>
        )}
      </div>
    </>
  );
}
