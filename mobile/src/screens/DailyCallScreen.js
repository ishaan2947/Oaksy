import { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Share,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { api } from "../api";
import { C } from "../theme";

const SPORTS = ["NFL", "NBA"];

export default function DailyCallScreen({ coachScore, onPicked, onToast }) {
  const [sport, setSport] = useState("NFL");
  const [situation, setSituation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [phase, setPhase] = useState("play");
  const [reveal, setReveal] = useState(null);
  const [reasoning, setReasoning] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [left, setLeft] = useState(30);
  const expired = useRef(false);

  const load = useCallback(() => {
    setLoading(true);
    setPhase("play");
    setReveal(null);
    setReasoning("");
    setLeft(30);
    expired.current = false;
    api
      .daily(sport)
      .then(setSituation)
      .catch((e) => onToast?.(e.message))
      .finally(() => setLoading(false));
  }, [sport, onToast]);

  useEffect(() => {
    load();
  }, [load]);

  // Countdown timer (only while playing).
  useEffect(() => {
    if (loading || phase !== "play") return;
    const start = Date.now();
    const t = setInterval(() => {
      const rem = Math.max(0, 30 - (Date.now() - start) / 1000);
      setLeft(rem);
      if (rem <= 0 && !expired.current) {
        expired.current = true;
        clearInterval(t);
        expire();
      }
    }, 100);
    return () => clearInterval(t);
  }, [loading, phase, situation]);

  async function pick(choice) {
    if (submitting || phase === "reveal") return;
    setSubmitting(true);
    try {
      const r = await api.submitPick({
        situation_id: situation.id,
        choice,
        reasoning: reasoning.trim() || null,
      });
      setReveal(r);
      setPhase("reveal");
      onPicked?.();
    } catch (e) {
      onToast?.(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function expire() {
    try {
      const r = await api.reveal(situation.id);
      setReveal(r);
      setPhase("reveal");
    } catch (e) {
      onToast?.(e.message);
    }
  }

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={C.accent} />
      </View>
    );
  }
  if (!situation) {
    return (
      <View style={styles.loading}>
        <Text style={{ color: C.inkDim }}>No call available.</Text>
        <Pressable style={styles.retry} onPress={load}>
          <Text style={{ color: C.ink, fontWeight: "700" }}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  const danger = left <= 10;

  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <View style={styles.toggle}>
        {SPORTS.map((s) => (
          <Pressable
            key={s}
            style={[styles.toggleItem, s === sport && styles.toggleActive]}
            onPress={() => setSport(s)}
          >
            <Text style={[styles.toggleText, s === sport && { color: "#0a0a0c" }]}>{s}</Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.card}>
        <View style={styles.eyebrowRow}>
          <Text style={styles.eyebrow}>
            <Text style={styles.sportTag}>{situation.sport}</Text>  THE DAILY CALL
          </Text>
          {phase === "play" && (
            <View style={[styles.timer, danger && { borderColor: C.red }]}>
              <Text style={[styles.timerNum, danger && { color: C.red }]}>
                {Math.ceil(left)}
              </Text>
            </View>
          )}
        </View>

        <Text style={styles.situation}>{situation.situation_description}</Text>

        {phase === "play" ? (
          <>
            {situation.options.map((o) => (
              <Pressable
                key={o.key}
                style={styles.option}
                disabled={submitting}
                onPress={() => pick(o.key)}
              >
                <View style={styles.optKey}>
                  <Text style={styles.optKeyText}>{o.key.toUpperCase()}</Text>
                </View>
                <Text style={styles.optLabel}>{o.label}</Text>
              </Pressable>
            ))}
            <TextInput
              style={styles.reasoning}
              placeholder="Make your case (optional)"
              placeholderTextColor={C.inkFaint}
              value={reasoning}
              onChangeText={setReasoning}
              multiline
              maxLength={600}
            />
          </>
        ) : (
          <Reveal options={situation.options} reveal={reveal} coachScore={coachScore} onToast={onToast} />
        )}
      </View>

      {phase === "reveal" && (
        <Pressable style={styles.next} onPress={load}>
          <Text style={{ color: C.ink, fontWeight: "700" }}>Next call →</Text>
        </Pressable>
      )}
    </ScrollView>
  );
}

function Reveal({ options, reveal, coachScore, onToast }) {
  let tone = C.ink;
  let line = "Time's up — here's how it played out.";
  if (reveal.your_choice) {
    if (reveal.you_beat_coach) {
      tone = C.green;
      line = "You out-coached the coach.";
    } else if (reveal.you_were_correct) {
      tone = C.green;
      line = "Right call.";
    } else {
      tone = C.red;
      line = "The coach got this one.";
    }
  }

  async function share() {
    const yourLabel = options.find((o) => o.key === reveal.your_choice)?.label;
    const total = reveal.community_split.total || 1;
    const agree = reveal.your_choice
      ? Math.round(((reveal.community_split[reveal.your_choice] || 0) / total) * 100)
      : 0;
    const lead = reveal.you_beat_coach
      ? "I out-coached the coach on Oaksy."
      : reveal.you_were_correct
      ? "I made the right call on Oaksy."
      : "The coach got me on Oaksy.";
    const detail = yourLabel
      ? ` I ${yourLabel.toLowerCase()}. ${agree}% of fans agreed.`
      : "";
    const sc = coachScore ? ` Coach Score: ${coachScore.win_rate}%.` : "";
    try {
      await Share.share({ message: `${lead}${detail}${sc} oaksyapp.com` });
    } catch (e) {
      onToast?.("Share failed.");
    }
  }

  return (
    <View>
      <Text style={[styles.verdictLine, { color: tone }]}>{line}</Text>

      {options.map((o) => {
        const isBest = o.key === reveal.best_call;
        const isCoach = o.key === reveal.actual_call;
        const isYou = o.key === reveal.your_choice;
        return (
          <View
            key={o.key}
            style={[
              styles.option,
              isBest && { borderColor: C.green, backgroundColor: C.greenDeep },
              !isBest && { opacity: 0.6 },
            ]}
          >
            <View style={styles.optKey}>
              <Text style={styles.optKeyText}>{o.key.toUpperCase()}</Text>
            </View>
            <Text style={styles.optLabel}>{o.label}</Text>
            <View style={styles.badges}>
              {isYou && <Badge text="You" bg={C.gold} fg="#2a1d00" />}
              {isCoach && <Badge text="Coach" bg={C.blue} fg="#04203a" />}
              {isBest && <Badge text="Data" bg={C.green} fg="#06210f" />}
            </View>
          </View>
        );
      })}

      <Section title="What happened">
        <Text style={styles.body}>{reveal.outcome}</Text>
      </Section>
      <Section title="The verdict">
        <View style={styles.aiBox}>
          <Text style={styles.body}>{reveal.ai_verdict}</Text>
        </View>
      </Section>
      <Section title="The community split">
        <Split split={reveal.community_split} options={options} />
      </Section>

      <Pressable style={styles.share} onPress={share}>
        <Text style={styles.shareText}>Share result</Text>
      </Pressable>
    </View>
  );
}

function Split({ split, options }) {
  const total = split.total || 0;
  if (!total) return <Text style={{ color: C.inkDim }}>Be the first to call it.</Text>;
  const color = (k) => (k === "a" ? C.accent : k === "b" ? C.blue : C.gold);
  return (
    <View>
      <View style={styles.splitBar}>
        {options.map((o) => {
          const pct = Math.round(((split[o.key] || 0) / total) * 100);
          if (!pct) return null;
          return (
            <View key={o.key} style={{ width: `${pct}%`, backgroundColor: color(o.key), justifyContent: "center" }}>
              <Text style={styles.splitPct}>{pct >= 12 ? `${pct}%` : ""}</Text>
            </View>
          );
        })}
      </View>
      {options.map((o) => (
        <Text key={o.key} style={styles.legend}>
          <Text style={{ color: color(o.key), fontWeight: "900" }}>● </Text>
          {o.label} · {Math.round(((split[o.key] || 0) / total) * 100)}%
        </Text>
      ))}
    </View>
  );
}

const Badge = ({ text, bg, fg }) => (
  <Text style={[styles.badge, { backgroundColor: bg, color: fg }]}>{text}</Text>
);
const Section = ({ title, children }) => (
  <View style={{ marginTop: 18 }}>
    <Text style={styles.h4}>{title}</Text>
    {children}
  </View>
);

const styles = StyleSheet.create({
  scroll: { padding: 16, paddingBottom: 30 },
  loading: { flex: 1, alignItems: "center", justifyContent: "center", gap: 12 },
  retry: { borderWidth: 1, borderColor: C.line, borderRadius: 10, paddingHorizontal: 16, paddingVertical: 9 },
  toggle: { flexDirection: "row", gap: 8, marginBottom: 14 },
  toggleItem: {
    flex: 1, alignItems: "center", paddingVertical: 11, borderRadius: 12,
    borderWidth: 1, borderColor: C.line,
  },
  toggleActive: { backgroundColor: C.ink, borderColor: C.ink },
  toggleText: { color: C.inkDim, fontWeight: "800" },
  card: {
    backgroundColor: C.panel, borderColor: C.line, borderWidth: 1, borderRadius: 16,
    padding: 18, borderTopColor: C.accent, borderTopWidth: 3,
  },
  eyebrowRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 12 },
  eyebrow: { color: C.inkFaint, fontSize: 11, fontWeight: "700", letterSpacing: 1 },
  sportTag: { color: C.inkDim },
  timer: {
    width: 40, height: 40, borderRadius: 20, borderWidth: 2, borderColor: C.accent,
    alignItems: "center", justifyContent: "center",
  },
  timerNum: { color: C.ink, fontWeight: "800", fontSize: 15 },
  situation: { color: C.ink, fontSize: 21, fontWeight: "800", lineHeight: 28, marginBottom: 16 },
  option: {
    flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: C.panel2,
    borderColor: C.line, borderWidth: 1, borderRadius: 12, padding: 15, marginBottom: 10,
  },
  optKey: {
    width: 26, height: 26, borderRadius: 7, backgroundColor: C.bg, borderColor: C.line,
    borderWidth: 1, alignItems: "center", justifyContent: "center",
  },
  optKeyText: { color: C.inkDim, fontWeight: "700", fontSize: 12 },
  optLabel: { color: C.ink, fontSize: 15, fontWeight: "600", flexShrink: 1 },
  badges: { flexDirection: "row", gap: 5, marginLeft: "auto" },
  badge: {
    fontSize: 10, fontWeight: "800", overflow: "hidden", borderRadius: 6,
    paddingHorizontal: 7, paddingVertical: 3,
  },
  reasoning: {
    backgroundColor: C.bg, borderColor: C.line, borderWidth: 1, borderRadius: 12,
    padding: 12, color: C.ink, marginTop: 6, minHeight: 52, textAlignVertical: "top",
  },
  verdictLine: { fontSize: 22, fontWeight: "900", marginBottom: 12, letterSpacing: -0.5 },
  h4: { color: C.inkFaint, fontSize: 11, fontWeight: "700", letterSpacing: 1.4, textTransform: "uppercase", marginBottom: 7 },
  body: { color: C.ink, fontSize: 15, lineHeight: 22 },
  aiBox: {
    backgroundColor: C.panel2, borderColor: C.line, borderWidth: 1, borderLeftColor: C.gold,
    borderLeftWidth: 3, borderRadius: 10, padding: 14,
  },
  splitBar: { flexDirection: "row", height: 34, borderRadius: 9, overflow: "hidden", borderWidth: 1, borderColor: C.line },
  splitPct: { textAlign: "center", color: "#0a0a0c", fontWeight: "800", fontSize: 12 },
  legend: { color: C.inkDim, fontSize: 13, marginTop: 6 },
  share: { backgroundColor: C.accent, borderRadius: 12, paddingVertical: 13, alignItems: "center", marginTop: 18 },
  shareText: { color: "#1a0c04", fontWeight: "800", fontSize: 15 },
  next: { alignSelf: "center", marginTop: 16, borderWidth: 1, borderColor: C.line, borderRadius: 12, paddingHorizontal: 18, paddingVertical: 11 },
});
