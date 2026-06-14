import { StyleSheet, Text, View } from "react-native";
import { C } from "../theme";

export default function Toast({ text }) {
  return (
    <View style={styles.wrap} pointerEvents="none">
      <View style={styles.toast}>
        <Text style={styles.text}>{text}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { position: "absolute", left: 0, right: 0, bottom: 80, alignItems: "center" },
  toast: {
    backgroundColor: C.ink,
    borderRadius: 999,
    paddingHorizontal: 18,
    paddingVertical: 10,
    maxWidth: "88%",
  },
  text: { color: "#0a0a0c", fontWeight: "700", fontSize: 14, textAlign: "center" },
});
