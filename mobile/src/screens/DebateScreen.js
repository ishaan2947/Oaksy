import { useEffect, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { C } from "../theme";

export default function DebateScreen({ user, onLogin, onToast }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.debate().then(setData).catch((e) => setError(e.message));
  }, []);

  async function vote(sitIndex, pickId) {
    if (!user) return onLogin();
    try {
      const res = await api.vote(pickId);
      setData((d) => {
        const next = JSON.parse(JSON.stringify(d));
        const posts = next.situations[sitIndex].posts;
        const p = posts.find((x) => x.pick_id === pickId);
        if (p) {
          p.votes = res.votes;
          p.you_voted = res.you_voted;
        }
        posts.sort((a, b) => b.votes - a.votes);
        return next;
      });
    } catch (e) {
      onToast?.(e.message);
    }
  }

  if (error)
    return (
      <View style={styles.center}>
        <Text style={{ color: C.inkDim }}>{error}</Text>
      </View>
    );
  if (!data)
    return (
      <View style={styles.center}>
        <Text style={{ color: C.inkFaint, fontWeight: "700" }}>Loading the Debate Arena…</Text>
      </View>
    );

  if (!data.situations.length)
    return (
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.card}>
          <Text style={styles.h}>The Debate Arena</Text>
          <Text style={styles.muted}>
            No debates yet this week. Make a Daily Call with your reasoning and it
            can land in the bracket.
          </Text>
        </View>
      </ScrollView>
    );

  const color = (k) => (k === "a" ? C.accent : k === "b" ? C.blue : C.gold);

  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Text style={styles.eyebrow}>THE DEBATE ARENA · {data.week_label}</Text>

      {data.situations.map((s, i) => {
        const total = s.community_split.total || 0;
        return (
          <View key={s.situation_id} style={styles.card}>
            <Text style={styles.eyebrow}>
              <Text style={styles.sportTag}>{s.sport}</Text>  MOST DEBATED
            </Text>
            <Text style={styles.situation}>{s.situation_description}</Text>

            {total > 0 && (
              <View style={styles.splitBar}>
                {s.options.map((o) => {
                  const pct = Math.round(((s.community_split[o.key] || 0) / total) * 100);
                  if (!pct) return null;
                  return (
                    <View
                      key={o.key}
                      style={{ width: `${pct}%`, backgroundColor: color(o.key), justifyContent: "center" }}
                    >
                      <Text style={styles.splitPct}>{pct >= 12 ? `${pct}%` : ""}</Text>
                    </View>
                  );
                })}
              </View>
            )}

            <Text style={styles.subhead}>Best reasoning wins</Text>
            {s.posts.length === 0 && (
              <Text style={styles.muted}>No arguments yet — be the first.</Text>
            )}
            {s.posts.map((p) => (
              <View key={p.pick_id} style={styles.post}>
                <Pressable
                  style={[styles.voteBtn, p.you_voted && styles.voted]}
                  onPress={() => vote(i, p.pick_id)}
                >
                  <Text style={[styles.voteUp, p.you_voted && { color: C.gold }]}>▲</Text>
                  <Text style={[styles.voteCnt, p.you_voted && { color: C.gold }]}>{p.votes}</Text>
                </Pressable>
                <View style={{ flex: 1 }}>
                  <Text style={styles.who}>
                    {p.author} <Text style={styles.pos}>· {p.choice_label}</Text>
                  </Text>
                  <Text style={styles.arg}>{p.reasoning}</Text>
                </View>
              </View>
            ))}
          </View>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 16, paddingBottom: 30 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", padding: 20 },
  card: { backgroundColor: C.panel, borderColor: C.line, borderWidth: 1, borderRadius: 16, padding: 18, marginBottom: 16 },
  eyebrow: { color: C.inkFaint, fontSize: 11, fontWeight: "700", letterSpacing: 1, marginBottom: 8 },
  sportTag: { color: C.inkDim },
  h: { color: C.ink, fontSize: 19, fontWeight: "900", letterSpacing: -0.5, marginBottom: 6 },
  situation: { color: C.ink, fontSize: 18, fontWeight: "800", lineHeight: 24, marginBottom: 12 },
  muted: { color: C.inkDim, fontSize: 14, lineHeight: 21 },
  splitBar: { flexDirection: "row", height: 30, borderRadius: 9, overflow: "hidden", borderWidth: 1, borderColor: C.line, marginBottom: 6 },
  splitPct: { textAlign: "center", color: "#0a0a0c", fontWeight: "800", fontSize: 11 },
  subhead: { color: C.inkFaint, fontSize: 11, fontWeight: "700", letterSpacing: 1.4, textTransform: "uppercase", marginTop: 12, marginBottom: 4 },
  post: { flexDirection: "row", gap: 12, backgroundColor: C.bg2, borderColor: C.line, borderWidth: 1, borderRadius: 12, padding: 12, marginTop: 9 },
  voteBtn: {
    alignItems: "center", justifyContent: "center", backgroundColor: C.bg, borderColor: C.line,
    borderWidth: 1, borderRadius: 10, paddingVertical: 8, paddingHorizontal: 12, minWidth: 50,
  },
  voted: { borderColor: C.gold },
  voteUp: { color: C.inkDim, fontSize: 12 },
  voteCnt: { color: C.inkDim, fontWeight: "800", fontSize: 16 },
  who: { color: C.ink, fontWeight: "800", fontSize: 14 },
  pos: { color: C.inkFaint, fontWeight: "600" },
  arg: { color: C.ink, fontSize: 14, lineHeight: 20, marginTop: 3 },
});
