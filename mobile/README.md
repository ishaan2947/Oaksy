# Oaksy Mobile (React Native / Expo)

The native iOS + Android app for Oaksy. It shares the **same FastAPI backend** as
the web app — the Daily Call loop, GM Mode, Coach Score, and auth all hit the
same `/api` endpoints.

Built with **Expo** so you can run it on a real phone (Expo Go) or a simulator
with no native build tooling.

## What's here
- **Daily Call** — sport toggle, 30-second timer, tap your call, animated reveal
  with the verdict, community split, and native share sheet.
- **GM Mode** — spin a pool of legends, build a five under the cap (live cap meter
  + guard/center requirements), Claude verdict, share.
- **Coach Score** — your record vs real coaches + GM rating + the weekly leaderboard.
- **Auth** — email/password (JWT), persisted with AsyncStorage.
- Custom bottom-tab navigation, stadium-dark theme matching the web app.

## Run it

```bash
cd mobile
npm install
npx expo install --fix     # aligns native module versions to your Expo SDK
npx expo start             # press i (iOS), a (Android), or scan the QR in Expo Go
```

### Pointing the app at your backend

The app needs to reach the FastAPI backend (default port **8000**). It resolves
the host automatically in this order (`src/api.js`):

1. **`expo.extra.apiBase` in `app.json`** — set this for a deployed backend, e.g.
   `"apiBase": "https://api.oaksy.app"`.
2. **Auto-detected dev host** — on a phone running Expo Go, it reuses the Expo
   packager's LAN IP and swaps to `:8000`, so a backend started with
   `uvicorn app.main:app --host 0.0.0.0 --port 8000` is reachable with no config.
3. **`http://localhost:8000`** — for the iOS simulator / Expo web.

> Start the backend with `--host 0.0.0.0` (not `127.0.0.1`) so your phone can
> reach it over the LAN, and make sure the phone and computer are on the same
> Wi-Fi. CORS doesn't apply to the native app (it's a browser-only concept), so
> no backend changes are needed for iOS/Android.

## Notes
- Per the product spec, mobile follows the web app — this shares the web's
  backend and feature set. The Debate Arena is the one web feature not yet ported
  to mobile (next up); everything else is here.
- The codebase was scaffolded and statically checked; run it through Expo Go /
  a simulator for the first live pass.
