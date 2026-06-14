// Shared stadium-dark palette — mirrors the web app.
export const C = {
  bg: "#0a0a0c",
  bg2: "#121217",
  panel: "#16161c",
  panel2: "#1d1d25",
  line: "#2a2a34",
  ink: "#f4f5f7",
  inkDim: "#9a9aa8",
  inkFaint: "#5f5f70",
  green: "#2ee66a",
  greenDeep: "#14361f",
  red: "#ff4d4d",
  gold: "#ffc23d",
  accent: "#ff5a1f",
  blue: "#3da5ff",
};

export const posColor = (pos) =>
  pos === "G" ? C.accent : pos === "F" ? C.blue : C.gold;
