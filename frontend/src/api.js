// Thin API client. The dev server proxies /api to the FastAPI backend.

const TOKEN_KEY = "oaksy_token";
const ANON_KEY = "oaksy_anon";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(t) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}

export function anonId() {
  let id = localStorage.getItem(ANON_KEY);
  if (!id) {
    id =
      crypto.randomUUID?.() ||
      "anon-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem(ANON_KEY, id);
  }
  return id;
}

async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  const token = getToken();
  if ((auth || token) && token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data.detail === "string") detail = data.detail;
      else if (Array.isArray(data.detail)) detail = data.detail[0]?.msg || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => request("/api/health"),

  // Auth
  signup: (payload) => request("/api/auth/signup", { method: "POST", body: payload }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: payload }),
  authConfig: () => request("/api/auth/config"),
  google: (credential) =>
    request("/api/auth/google", { method: "POST", body: { credential } }),
  me: () => request("/api/auth/me", { auth: true }),

  // Daily Call
  daily: (sport) => request(`/api/situations/daily?sport=${encodeURIComponent(sport)}`),
  reveal: (id) =>
    request(`/api/situations/${id}/reveal?anon_id=${encodeURIComponent(anonId())}`),
  submitPick: ({ situation_id, choice, reasoning, confidence }) =>
    request("/api/picks", {
      method: "POST",
      body: {
        situation_id,
        choice,
        reasoning,
        confidence,
        anon_id: getToken() ? null : anonId(),
      },
    }),

  // Live scores
  scores: (sport) => request(`/api/scores?sport=${encodeURIComponent(sport)}`),

  // Challenge a friend
  createChallenge: (body) => request("/api/challenges", { method: "POST", body }),
  getChallenge: (id) => request(`/api/challenges/${encodeURIComponent(id)}`),

  // Coach Score + leaderboard
  myScore: () => request("/api/users/me/score", { auth: true }),
  leaderboard: () => request("/api/users/leaderboard"),

  // Debate Arena
  debate: () => request("/api/debate/current"),
  vote: (pickId) =>
    request(`/api/debate/posts/${pickId}/vote`, { method: "POST", auth: true }),
  argue: (situationId, { choice, reasoning }) =>
    request(`/api/debate/${situationId}/argue`, {
      method: "POST",
      auth: true,
      body: { choice, reasoning },
    }),

  // Feedback poll
  feedback: ({ rating, comment }) =>
    request("/api/feedback", {
      method: "POST",
      body: { rating, comment, source: "app", anon_id: getToken() ? null : anonId() },
    }),

  // 82-0 GM Mode
  gmSpin: () => request("/api/gm/spin", { method: "POST" }),
  gmSubmit: ({ spin_id, player_ids }) =>
    request("/api/gm/submit", {
      method: "POST",
      body: { spin_id, player_ids, anon_id: getToken() ? null : anonId() },
    }),
};
