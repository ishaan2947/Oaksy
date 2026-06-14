import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Share,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { api } from "../api";
import { C, posColor } from "../theme";

export default function GMScreen({ onSubmitted, onToast }) {
  const [spin, setSpin] = useState(null);
  const [selected, setSelected] = useState([]);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  async function doSpin() {
    setBusy(true);
    setResult(null);
    setSelected([]);
    try {
      setSpin(await api.gmSpin());
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
  const cost = team.reduce((s, p) => s + p.cost, 0);
  const positions = new Set(team.map((p) => p.pos));
  const hasG = positions.has("G");
  const hasC = positions.has("C");
  const cap = spin?.cap || 0;
  const over = cost > cap;
  const full = spin && selected.length === spin.roster_size;
  const legal = full && !over && hasG && hasC;

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

  // ---- Result ----
  if (result) {
    const grade = result.score >= 90 ? C.green : result.score >= 70 ? C.ink : C.red;
    return (
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.card}>
          <Text style={styles.eyebrow}>
            <Text style={styles.sportTag}>NBA</Text>  CLAUDE'S VERDICT
          </Text>
          <Text style={[styles.score, { color: grade }]}>
            {result.score}
            <Text style={styles.scoreOf}> /100</Text>
          </Text>
          <View style={styles.aiBox}>
            <Text style={styles.body}>{result.verdict}</Text>
          </View>
          <View style={styles.chips}>
            {result.team.map((p) => (
              <View key={p.id} style={styles.chip}>
                <PosBadge pos={p.pos} />
                <Text style={styles.chipName}>{p.name}</Text>
              </View>
            ))}
          </View>
          <Text style={styles.capLabel}>
            Team cost: <Text style={{ color: C.ink }}>{result.total_cost}</Text> / {result.cap}
          </Text>
        </View>
        <View style={styles.rowBtns}>
          <Pressable
            style={styles.primary}
            onPress={() => Share.share({ message: `${result.share_line} oaksyapp.com` })}
          >
            <Text style={styles.primaryText}>Share team</Text>
          </Pressable>
          <Pressable style={styles.ghost} onPress={doSpin}>
            <Text style={{ color: C.ink, fontWeight: "700" }}>🎲 Spin again</Text>
          </Pressable>
        </View>
      </ScrollView>
    );
  }

  // ---- Intro ----
  if (!spin) {
    return (
      <ScrollView contentContainerStyle={[styles.scroll, { paddingTop: 40 }]}>
        <Text style={styles.bigTitle}>Build a team that goes 82-0.</Text>
        <Text style={styles.intro}>
          Spin for a pool of legends from any era. Assemble a starting five under
          the cap, then let Claude rate whether it goes undefeated.
        </Text>
        <Pressable style={styles.primary} onPress={doSpin} disabled={busy}>
          {busy ? (
            <ActivityIndicator color="#1a0c04" />
          ) : (
            <Text style={styles.primaryText}>🎲 Spin the wheel</Text>
          )}
        </Pressable>
      </ScrollView>
    );
  }

  // ---- Build ----
  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <View style={styles.capRow}>
        <View style={{ flex: 1 }}>
          <View style={styles.capMeter}>
            <View
              style={{
                width: `${Math.min(100, (cost / cap) * 100)}%`,
                height: "100%",
                backgroundColor: over ? C.red : C.green,
              }}
            />
          </View>
          <Text style={styles.capLabel}>
            Cap: <Text style={{ color: over ? C.red : C.ink }}>{cost}</Text> / {cap} ·{" "}
            {selected.length}/{spin.roster_size}
          </Text>
        </View>
        <View style={styles.reqs}>
          <Text style={[styles.req, hasG && styles.reqMet]}>G {hasG ? "✓" : "✗"}</Text>
          <Text style={[styles.req, hasC && styles.reqMet]}>C {hasC ? "✓" : "✗"}</Text>
        </View>
      </View>

      {pool.map((p) => {
        const idx = selected.indexOf(p.id);
        const sel = idx >= 0;
        const disabled = !sel && full;
        return (
          <Pressable
            key={p.id}
            style={[styles.pcard, sel && styles.pcardSel, disabled && { opacity: 0.4 }]}
            disabled={disabled}
            onPress={() => toggle(p.id)}
          >
            <PosBadge pos={p.pos} />
            <View style={{ flex: 1 }}>
              <Text style={styles.pname}>{p.name}</Text>
              <Text style={styles.pmeta}>{p.era} · {p.tag}</Text>
            </View>
            <Text style={styles.pcost}>{p.cost} pts</Text>
            {sel && (
              <View style={styles.pickNum}>
                <Text style={styles.pickNumText}>{idx + 1}</Text>
              </View>
            )}
          </Pressable>
        );
      })}

      <View style={styles.rowBtns}>
        <Pressable style={[styles.primary, !legal && { opacity: 0.5 }]} disabled={!legal || busy} onPress={lockIn}>
          {busy ? (
            <ActivityIndicator color="#1a0c04" />
          ) : (
            <Text style={styles.primaryText}>
              {legal
                ? "Lock in roster →"
                : over
                ? "Over the cap"
                : !full
                ? `Pick ${spin.roster_size - selected.length} more`
                : !hasG
                ? "Need a guard"
                : "Need a center"}
            </Text>
          )}
        </Pressable>
        <Pressable style={styles.ghost} disabled={busy} onPress={doSpin}>
          <Text style={{ color: C.ink, fontWeight: "700" }}>Re-spin</Text>
        </Pressable>
      </View>
    </ScrollView>
  );
}

const PosBadge = ({ pos }) => (
  <View style={[styles.pos, { backgroundColor: posColor(pos) }]}>
    <Text style={styles.posText}>{pos}</Text>
  </View>
);

const styles = StyleSheet.create({
  scroll: { padding: 16, paddingBottom: 30 },
  bigTitle: { color: C.ink, fontSize: 28, fontWeight: "900", letterSpacing: -1, textAlign: "center" },
  intro: { color: C.inkDim, fontSize: 15, lineHeight: 22, textAlign: "center", marginTop: 10, marginBottom: 22 },
  card: { backgroundColor: C.panel, borderColor: C.line, borderWidth: 1, borderRadius: 16, padding: 18 },
  eyebrow: { color: C.inkFaint, fontSize: 11, fontWeight: "700", letterSpacing: 1, marginBottom: 6 },
  sportTag: { color: C.inkDim },
  score: { fontSize: 66, fontWeight: "900", letterSpacing: -3 },
  scoreOf: { fontSize: 22, color: C.inkFaint, fontWeight: "800" },
  aiBox: {
    backgroundColor: C.panel2, borderColor: C.line, borderWidth: 1, borderLeftColor: C.gold,
    borderLeftWidth: 3, borderRadius: 10, padding: 14, marginTop: 6,
  },
  body: { color: C.ink, fontSize: 15, lineHeight: 22 },
  chips: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 14 },
  chip: {
    flexDirection: "row", alignItems: "center", gap: 7, backgroundColor: C.panel2,
    borderColor: C.line, borderWidth: 1, borderRadius: 999, paddingVertical: 5, paddingHorizontal: 10, paddingLeft: 5,
  },
  chipName: { color: C.ink, fontSize: 13, fontWeight: "700" },
  capLabel: { color: C.inkDim, fontSize: 13, marginTop: 10 },
  capRow: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 14 },
  capMeter: { height: 12, borderRadius: 7, backgroundColor: C.bg, borderColor: C.line, borderWidth: 1, overflow: "hidden" },
  reqs: { flexDirection: "row", gap: 8 },
  req: {
    color: C.inkDim, fontWeight: "800", fontSize: 12, borderWidth: 1, borderColor: C.line,
    borderRadius: 999, paddingHorizontal: 10, paddingVertical: 5, overflow: "hidden",
  },
  reqMet: { color: C.green, borderColor: C.green },
  pcard: {
    flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: C.panel,
    borderColor: C.line, borderWidth: 1, borderRadius: 12, padding: 12, marginBottom: 9,
  },
  pcardSel: { borderColor: C.gold, backgroundColor: "#1d1a12" },
  pos: { width: 24, height: 24, borderRadius: 6, alignItems: "center", justifyContent: "center" },
  posText: { fontWeight: "800", fontSize: 11, color: "#0a0a0c" },
  pname: { color: C.ink, fontSize: 15, fontWeight: "800" },
  pmeta: { color: C.inkFaint, fontSize: 12, marginTop: 1 },
  pcost: { color: C.inkDim, fontWeight: "700", fontSize: 13 },
  pickNum: { width: 22, height: 22, borderRadius: 11, backgroundColor: C.gold, alignItems: "center", justifyContent: "center" },
  pickNumText: { color: "#2a1d00", fontWeight: "900", fontSize: 12 },
  rowBtns: { flexDirection: "row", gap: 10, marginTop: 18 },
  primary: { flex: 1, backgroundColor: C.accent, borderRadius: 12, paddingVertical: 13, alignItems: "center" },
  primaryText: { color: "#1a0c04", fontWeight: "800", fontSize: 15 },
  ghost: { borderWidth: 1, borderColor: C.line, borderRadius: 12, paddingVertical: 13, paddingHorizontal: 16, alignItems: "center", justifyContent: "center" },
});
