import { useState } from "react";
import { api } from "../api";

const DONE_KEY = "oaksy_feedback_done";

// A small floating "poll" so testers can leave one-tap signal: would you play
// this daily? Optional comment. Hidden once they've responded.
export default function FeedbackWidget() {
  const [open, setOpen] = useState(false);
  const [rating, setRating] = useState(null);
  const [comment, setComment] = useState("");
  const [state, setState] = useState(
    localStorage.getItem(DONE_KEY) ? "done" : "idle"
  );

  if (state === "done" && !open) return null;

  async function submit() {
    if (!rating) return;
    setState("busy");
    try {
      await api.feedback({ rating, comment: comment.trim() || null });
      localStorage.setItem(DONE_KEY, "1");
      setState("thanks");
      setTimeout(() => setOpen(false), 1800);
    } catch {
      setState("idle");
    }
  }

  if (!open) {
    return (
      <button className="fb-fab" onClick={() => setOpen(true)} title="Give feedback">
        💬 Feedback
      </button>
    );
  }

  return (
    <div className="fb-pop">
      <button className="fb-x" onClick={() => setOpen(false)} aria-label="Close">
        ×
      </button>
      {state === "thanks" ? (
        <div className="fb-thanks">Thanks — that's exactly the signal we need. 🙏</div>
      ) : (
        <>
          <div className="fb-q">Would you play this every day?</div>
          <div className="fb-opts">
            {[
              ["yes", "Yes"],
              ["maybe", "Maybe"],
              ["no", "No"],
            ].map(([val, label]) => (
              <button
                key={val}
                className={`fb-opt ${rating === val ? "sel" : ""}`}
                onClick={() => setRating(val)}
              >
                {label}
              </button>
            ))}
          </div>
          <textarea
            className="fb-comment"
            placeholder="Anything you'd change? (optional)"
            value={comment}
            maxLength={1000}
            onChange={(e) => setComment(e.target.value)}
          />
          <button
            className="btn primary fb-submit"
            disabled={!rating || state === "busy"}
            onClick={submit}
          >
            {state === "busy" ? "…" : "Send feedback"}
          </button>
        </>
      )}
    </div>
  );
}
