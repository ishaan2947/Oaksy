import { useCallback, useEffect, useState } from "react";
import {
  Pressable,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { AuthProvider, useAuth } from "./src/auth";
import { api } from "./src/api";
import { C } from "./src/theme";
import DailyCallScreen from "./src/screens/DailyCallScreen";
import DebateScreen from "./src/screens/DebateScreen";
import GMScreen from "./src/screens/GMScreen";
import ScoreScreen from "./src/screens/ScoreScreen";
import AuthSheet from "./src/components/AuthSheet";
import Toast from "./src/components/Toast";

const TABS = [
  { id: "daily", label: "Daily", icon: "🏈" },
  { id: "debate", label: "Debate", icon: "⚔️" },
  { id: "gm", label: "GM Mode", icon: "🏀" },
  { id: "score", label: "Score", icon: "🏆" },
];

function Shell() {
  const { user, ready, logout } = useAuth();
  const [tab, setTab] = useState("daily");
  const [showAuth, setShowAuth] = useState(false);
  const [score, setScore] = useState(null);
  const [toast, setToast] = useState(null);

  const refreshScore = useCallback(() => {
    if (!user) return setScore(null);
    api.myScore().then(setScore).catch(() => {});
  }, [user]);

  useEffect(() => {
    refreshScore();
  }, [refreshScore]);

  const showToast = useCallback((msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2600);
  }, []);

  if (!ready) {
    return (
      <View style={[styles.center, { flex: 1, backgroundColor: C.bg }]}>
        <Text style={{ color: C.inkFaint, fontWeight: "700" }}>Oaksy…</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.app}>
      <StatusBar barStyle="light-content" />
      <View style={styles.topbar}>
        <Text style={styles.brand}>
          Oaksy<Text style={{ color: C.accent }}>.</Text>
        </Text>
        {user ? (
          <View style={styles.row}>
            {score ? (
              <Pressable style={styles.chip} onPress={() => setTab("score")}>
                <Text style={styles.chipText}>
                  Score <Text style={{ color: C.ink, fontWeight: "800" }}>{score.win_rate}%</Text>
                </Text>
              </Pressable>
            ) : null}
            <Pressable onPress={logout}>
              <Text style={styles.link}>Log out</Text>
            </Pressable>
          </View>
        ) : (
          <Pressable style={styles.signin} onPress={() => setShowAuth(true)}>
            <Text style={styles.signinText}>Sign in</Text>
          </Pressable>
        )}
      </View>

      <View style={{ flex: 1 }}>
        {tab === "daily" && (
          <DailyCallScreen coachScore={score} onPicked={refreshScore} onToast={showToast} />
        )}
        {tab === "debate" && (
          <DebateScreen
            user={user}
            onLogin={() => setShowAuth(true)}
            onToast={showToast}
          />
        )}
        {tab === "gm" && <GMScreen onSubmitted={refreshScore} onToast={showToast} />}
        {tab === "score" && (
          <ScoreScreen
            user={user}
            score={score}
            onLogin={() => setShowAuth(true)}
          />
        )}
      </View>

      <View style={styles.tabbar}>
        {TABS.map((t) => {
          const active = t.id === tab;
          return (
            <Pressable key={t.id} style={styles.tabItem} onPress={() => setTab(t.id)}>
              <Text style={{ fontSize: 18, opacity: active ? 1 : 0.5 }}>{t.icon}</Text>
              <Text style={[styles.tabLabel, active && { color: C.ink }]}>{t.label}</Text>
            </Pressable>
          );
        })}
      </View>

      {showAuth && <AuthSheet onClose={() => setShowAuth(false)} />}
      {toast && <Toast text={toast} />}
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <Shell />
      </AuthProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: C.bg },
  center: { alignItems: "center", justifyContent: "center" },
  row: { flexDirection: "row", alignItems: "center", gap: 10 },
  topbar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: C.line,
  },
  brand: { color: C.ink, fontSize: 24, fontWeight: "900", letterSpacing: -1 },
  chip: {
    backgroundColor: C.panel,
    borderColor: C.line,
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  chipText: { color: C.inkDim, fontSize: 13, fontWeight: "700" },
  link: { color: C.inkDim, fontWeight: "700", fontSize: 14 },
  signin: {
    backgroundColor: C.accent,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 9,
  },
  signinText: { color: "#1a0c04", fontWeight: "800" },
  tabbar: {
    flexDirection: "row",
    borderTopWidth: 1,
    borderTopColor: C.line,
    backgroundColor: C.bg2,
    paddingBottom: 6,
    paddingTop: 8,
  },
  tabItem: { flex: 1, alignItems: "center", gap: 3 },
  tabLabel: { color: C.inkFaint, fontSize: 11, fontWeight: "700" },
});
