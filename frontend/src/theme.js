// Light/dark theme. The actual <html data-theme> is set by an inline script in
// index.html / landing.html before paint (no flash); this just reads/flips it.
const KEY = "oaksy_theme";

export function getTheme() {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export function setTheme(t) {
  document.documentElement.dataset.theme = t;
  try {
    localStorage.setItem(KEY, t);
  } catch {
    /* ignore */
  }
}

export function toggleTheme() {
  const next = getTheme() === "light" ? "dark" : "light";
  setTheme(next);
  return next;
}
