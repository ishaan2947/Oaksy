// API client for the Oaksy backend (the same FastAPI server the web app uses).
//
// Host resolution order:
//   1. expo.extra.apiBase in app.json (set this for a deployed backend)
//   2. The Expo dev-server host IP + :8000 (so it "just works" on a device in dev)
//   3. http://localhost:8000 (simulators / web)
import Constants from "expo-constants";
import AsyncStorage from "@react-native-async-storage/async-storage";

const TOKEN_KEY = "oaksy_token";
const ANON_KEY = "oaksy_anon";

function resolveBase() {
  const configured = Constants.expoConfig?.extra?.apiBase;
  if (configured) return configured.replace(/\/$/, "");

  // hostUri looks like "192.168.1.50:8081" — reuse the IP, swap to backend port.
  const hostUri =
    Constants.expoConfig?.hostUri ||
    Constants.expoGoConfig?.debuggerHost ||
    "";
  const host = hostUri.split(":")[0];
  if (host && host !== "localhost" && host !== "127.0.0.1") {
    return `http://${host}:8000`;
  }
  return "http://localhost:8000";
}

export const API_BASE = resolveBase();

let _token = null;
let _anon = null;

export async function loadSession() {
  _token = await AsyncStorage.getItem(TOKEN_KEY);
  _anon = await AsyncStorage.getItem(ANON_KEY);
  if (!_anon) {
    _anon = "anon-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    await AsyncStorage.setItem(ANON_KEY, _anon);
  }
  return _token;
}

export function getToken() {
  return _token;
}
export async function setToken(t) {
  _token = t || null;
  if (t) await AsyncStorage.setItem(TOKEN_KEY, t);
  else await AsyncStorage.removeItem(TOKEN_KEY);
}
export function anonId() {
  return _anon;
}

async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  if ((auth || _token) && _token) headers["Authorization"] = `Bearer ${_token}`;

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    throw new Error(
      `Can't reach the backend at ${API_BASE}. Is it running, and on the same network?`
    );
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data.detail === "string") detail = data.detail;
      else if (Array.isArray(data.detail)) detail = data.detail[0]?.msg || detail;
    } catch {}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => request("/api/health"),
  signup: (b) => request("/api/auth/signup", { method: "POST", body: b }),
  login: (b) => request("/api/auth/login", { method: "POST", body: b }),
  me: () => request("/api/auth/me", { auth: true }),

  daily: (sport) => request(`/api/situations/daily?sport=${encodeURIComponent(sport)}`),
  reveal: (id) =>
    request(`/api/situations/${id}/reveal?anon_id=${encodeURIComponent(_anon)}`),
  submitPick: ({ situation_id, choice, reasoning }) =>
    request("/api/picks", {
      method: "POST",
      body: { situation_id, choice, reasoning, anon_id: _token ? null : _anon },
    }),

  myScore: () => request("/api/users/me/score", { auth: true }),
  leaderboard: () => request("/api/users/leaderboard"),

  gmSpin: () => request("/api/gm/spin", { method: "POST" }),
  gmSubmit: ({ spin_id, player_ids }) =>
    request("/api/gm/submit", {
      method: "POST",
      body: { spin_id, player_ids, anon_id: _token ? null : _anon },
    }),
};
