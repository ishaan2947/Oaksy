import { useEffect } from "react";

// An immersive ambient layer: a cursor-following spotlight, slow-drifting
// sports line-art that parallaxes on scroll, and a click ripple. All
// compositor-friendly (transform/opacity), rAF-throttled, and fully disabled
// under prefers-reduced-motion. Pointer effects only attach to fine pointers.
export default function Ambient() {
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const fine = window.matchMedia("(pointer: fine)").matches;
    const root = document.documentElement;
    let raf = 0;
    let mx = window.innerWidth / 2;
    let my = window.innerHeight / 2;
    let sy = 0;

    const apply = () => {
      root.style.setProperty("--mx", `${mx}px`);
      root.style.setProperty("--my", `${my}px`);
      root.style.setProperty("--scrolly", `${sy}`);
      raf = 0;
    };
    const schedule = () => {
      if (!raf) raf = requestAnimationFrame(apply);
    };
    const onMove = (e) => {
      mx = e.clientX;
      my = e.clientY;
      schedule();
    };
    const onScroll = () => {
      sy = window.scrollY;
      schedule();
    };
    const onDown = (e) => {
      const r = document.createElement("span");
      r.className = "click-ripple";
      r.style.left = `${e.clientX}px`;
      r.style.top = `${e.clientY}px`;
      document.body.appendChild(r);
      r.addEventListener("animationend", () => r.remove());
    };

    if (fine) window.addEventListener("pointermove", onMove, { passive: true });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("pointerdown", onDown, { passive: true });
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("pointerdown", onDown);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      <div className="ambient" aria-hidden="true">
        {/* Football */}
        <svg className="orb o1" viewBox="0 0 100 60">
          <ellipse cx="50" cy="30" rx="46" ry="26" fill="none" stroke="currentColor" strokeWidth="2" />
          <line x1="34" y1="30" x2="66" y2="30" stroke="currentColor" strokeWidth="2" />
          <line x1="40" y1="25" x2="40" y2="35" stroke="currentColor" strokeWidth="2" />
          <line x1="48" y1="24" x2="48" y2="36" stroke="currentColor" strokeWidth="2" />
          <line x1="56" y1="24" x2="56" y2="36" stroke="currentColor" strokeWidth="2" />
        </svg>
        {/* Basketball */}
        <svg className="orb o2" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" strokeWidth="2" />
          <path d="M4 50 H96 M50 4 V96 M16 16 Q50 50 16 84 M84 16 Q50 50 84 84" fill="none" stroke="currentColor" strokeWidth="2" />
        </svg>
        {/* Baseball */}
        <svg className="orb o3" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" strokeWidth="2" />
          <path d="M22 14 Q40 50 22 86 M78 14 Q60 50 78 86" fill="none" stroke="currentColor" strokeWidth="2" />
        </svg>
        {/* Whistle-ish ring / hoop */}
        <svg className="orb o4" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="44" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="6 10" />
        </svg>
      </div>
      <div className="spotlight" aria-hidden="true" />
    </>
  );
}
