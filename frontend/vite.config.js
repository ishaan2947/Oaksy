import { defineConfig } from "vite";
import { resolve } from "path";
import react from "@vitejs/plugin-react";

// Dev server proxies /api to the FastAPI backend so the frontend can call
// relative URLs (no CORS juggling in development).
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        // The app (index.html) and the marketing/waitlist page (landing.html).
        main: resolve(__dirname, "index.html"),
        landing: resolve(__dirname, "landing.html"),
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
