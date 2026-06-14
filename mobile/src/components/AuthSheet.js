import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { useAuth } from "../auth";
import { C } from "../theme";

export default function AuthSheet({ onClose }) {
  const { login, signup } = useAuth();
  const [mode, setMode] = useState("signup");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setErr("");
    setBusy(true);
    try {
      if (mode === "signup") await signup(email.trim(), name.trim(), password);
      else await login(email.trim(), password);
      onClose();
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.overlay} onPress={onClose}>
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}>
          <Pressable style={styles.card} onPress={() => {}}>
            <Text style={styles.title}>
              {mode === "signup" ? "Claim your Coach Score" : "Welcome back"}
            </Text>
            <Text style={styles.sub}>
              {mode === "signup"
                ? "Track your record vs real coaches."
                : "Sign in to keep building your record."}
            </Text>

            {mode === "signup" && (
              <Field label="Coach name" value={name} onChangeText={setName} placeholder="Leaderboard name" />
            )}
            <Field
              label="Email"
              value={email}
              onChangeText={setEmail}
              placeholder="you@email.com"
              keyboardType="email-address"
              autoCapitalize="none"
            />
            <Field
              label="Password"
              value={password}
              onChangeText={setPassword}
              placeholder={mode === "signup" ? "At least 8 characters" : "••••••••"}
              secureTextEntry
            />

            {err ? <Text style={styles.err}>{err}</Text> : <View style={{ height: 8 }} />}

            <Pressable style={styles.primary} onPress={submit} disabled={busy}>
              {busy ? (
                <ActivityIndicator color="#1a0c04" />
              ) : (
                <Text style={styles.primaryText}>
                  {mode === "signup" ? "Create account" : "Sign in"}
                </Text>
              )}
            </Pressable>

            <Pressable
              onPress={() => {
                setErr("");
                setMode(mode === "signup" ? "login" : "signup");
              }}
            >
              <Text style={styles.switch}>
                {mode === "signup"
                  ? "Already have an account? Sign in"
                  : "New to Oaksy? Create one"}
              </Text>
            </Pressable>
          </Pressable>
        </KeyboardAvoidingView>
      </Pressable>
    </Modal>
  );
}

function Field({ label, ...props }) {
  return (
    <View style={{ marginBottom: 12 }}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        style={styles.input}
        placeholderTextColor={C.inkFaint}
        {...props}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.7)",
    alignItems: "center",
    justifyContent: "center",
    padding: 18,
  },
  card: {
    width: 360,
    maxWidth: "100%",
    backgroundColor: C.panel,
    borderColor: C.line,
    borderWidth: 1,
    borderRadius: 16,
    padding: 22,
  },
  title: { color: C.ink, fontSize: 21, fontWeight: "900", letterSpacing: -0.5 },
  sub: { color: C.inkDim, fontSize: 14, marginTop: 4, marginBottom: 16 },
  label: { color: C.inkDim, fontSize: 12, marginBottom: 5 },
  input: {
    backgroundColor: C.bg,
    borderColor: C.line,
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 13,
    paddingVertical: 11,
    color: C.ink,
    fontSize: 15,
  },
  err: { color: C.red, fontSize: 13, marginVertical: 6 },
  primary: {
    backgroundColor: C.accent,
    borderRadius: 12,
    paddingVertical: 13,
    alignItems: "center",
  },
  primaryText: { color: "#1a0c04", fontWeight: "800", fontSize: 15 },
  switch: { color: C.gold, fontWeight: "700", textAlign: "center", marginTop: 14, fontSize: 13 },
});
