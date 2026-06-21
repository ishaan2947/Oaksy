import { useEffect, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { C } from "../theme";

export default function ScoreScreen({ user, score, onLogin }) {
  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      {!user ? (
        <View style={styles.card}>
          <Text style={styles.title}>Your Coach Score</Text>
          <Text style={styles.muted}>
            Sign in to build a record that spans every Daily Call, GM session, and
            debate win — the number you brag about.
          </Text>
          <Pressable style={styles.primary} onPress={onLogin}>
            <Text style={styles.primaryText}>Sign in to track your score</Text>
          </Pressable>
        </View>
      ) : !score ? (
        <Text style={styles.muted}>Loading your score…</Text>
      ) : (
        <View style={styles.card}>
          <View style={styles.titleRow}>
            <Text style={styles.title}>{score.display_name}</Text>
            <Text style={styles.rank}>{score.rank_label}</Text>
          </View>
          <View style={styles.grid}>
            <Tile n={`${score.win_rate}%`} l="Win rate vs coaches" color={C.green} />
            <Tile
              n={score.current_streak > 0 ? `🔥 ${score.current_streak}` : "—"}
              l={`Day streak${score.longest_streak > 0 ? ` · best ${score.longest_streak}` : ""}`}
              color={C.accent}
            />
            <Tile n={score.beat_coach_count} l="Beat the coach" color={C.gold} />
            <Tile n={score.total_calls} l="Calls made" />
            <Tile n={score.debate_wins} l="Debate votes won" />
            <Tile
              n={score.gm_teams > 0 ? score.gm_rating : "—"}
              l={`GM rating · ${score.gm_rank_label}`}
              color={C.blue}
            />
            <Tile n={score.gm_teams} l="82-0 teams built" />
          </View>
        </View>
      )}

      <Text style={styles.sectionTitle}>This week's top coaches</Text>
      <Leaderboard highlight={score?.display_name} />
    </ScrollView>
  );
}

function Tile({ n, l, color = C.ink }) {
  return (
    <View style={styles.tile}>
      <Text style={[styles.tileN, { color }]}>{n}</Text>
      <Text style={styles.tileL}>{l}</Text>
    </View>
  );
}

function Leaderboard({ highlight }) {
  const [rows, setRows] = useState(null);
  useEffect(() => {
    api.leaderboard().then(setRows).catch(() => setRows([]));
  }, []);

  if (!rows) return <Text style={styles.muted}>Loading…</Text>;
  if (!rows.length) return <Text style={styles.muted}>No ranked coaches yet — make some calls.</Text>;

  return (
    <View>
      {rows.map((r, i) => (
        <View
          key={`${r.display_name}-${i}`}
          style={[styles.lbRow, r.display_name === highlight && { borderColor: C.gold }]}
        >
          <Text style={[styles.lbRank, i < 3 && { color: C.gold }]}>{i + 1}</Text>
          <Text style={styles.lbName}>{r.display_name}</Text>
          <Text style={styles.lbRate}>{r.win_rate}%</Text>
          <Text style={styles.lbCalls}>{r.total_calls} calls</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 16, paddingBottom: 30 },
  card: { backgroundColor: C.panel, borderColor: C.line, borderWidth: 1, borderRadius: 16, padding: 18 },
  titleRow: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 4 },
  title: { color: C.ink, fontSize: 22, fontWeight: "900", letterSpacing: -0.5 },
  rank: {
    backgroundColor: C.gold, color: "#2a1d00", fontWeight: "800", fontSize: 13,
    borderRadius: 999, paddingHorizontal: 12, paddingVertical: 4, overflow: "hidden",
  },
  muted: { color: C.inkDim, fontSize: 14, lineHeight: 21 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 10, marginTop: 14 },
  tile: {
    width: "47.5%", backgroundColor: C.bg2, borderColor: C.line, borderWidth: 1,
    borderRadius: 12, padding: 14,
  },
  tileN: { fontSize: 30, fontWeight: "900", letterSpacing: -1 },
  tileL: { color: C.inkFaint, fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 0.8, marginTop: 2 },
  primary: { backgroundColor: C.accent, borderRadius: 12, paddingVertical: 13, alignItems: "center", marginTop: 14 },
  primaryText: { color: "#1a0c04", fontWeight: "800", fontSize: 15 },
  sectionTitle: { color: C.ink, fontSize: 18, fontWeight: "900", letterSpacing: -0.5, marginTop: 24, marginBottom: 8 },
  lbRow: {
    flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: C.panel,
    borderColor: C.line, borderWidth: 1, borderRadius: 11, padding: 13, marginTop: 8,
  },
  lbRank: { color: C.inkFaint, fontWeight: "900", width: 24, fontSize: 15 },
  lbName: { color: C.ink, fontWeight: "700", flex: 1 },
  lbRate: { color: C.green, fontWeight: "900" },
  lbCalls: { color: C.inkFaint, fontSize: 13 },
});
