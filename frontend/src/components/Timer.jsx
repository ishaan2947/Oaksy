import { useEffect, useRef, useState } from "react";

// A 30-second countdown ring that pulses red in the final stretch.
export default function Timer({ seconds = 30, onExpire, running }) {
  const [left, setLeft] = useState(seconds);
  const expired = useRef(false);

  useEffect(() => {
    if (!running) return;
    const start = Date.now();
    const tick = setInterval(() => {
      const remaining = Math.max(0, seconds - (Date.now() - start) / 1000);
      setLeft(remaining);
      if (remaining <= 0 && !expired.current) {
        expired.current = true;
        clearInterval(tick);
        onExpire?.();
      }
    }, 100);
    return () => clearInterval(tick);
  }, [running, seconds, onExpire]);

  const pct = (left / seconds) * 100;
  const danger = left <= 10;

  return (
    <div className={`timer ${danger ? "danger" : ""}`}>
      <div className="ring" style={{ "--pct": pct }}>
        <span className="num">{Math.ceil(left)}</span>
      </div>
    </div>
  );
}
