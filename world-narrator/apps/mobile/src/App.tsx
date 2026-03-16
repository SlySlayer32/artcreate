import React from "react";
import { SafeAreaView, Text, View, Button, StyleSheet } from "react-native";

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>WorldNarrator</Text>
      <View style={styles.card}>
        <Text style={styles.body}>Capture a page and listen to narrated audio.</Text>
        <Button title="Scan Page" onPress={() => {}} />
        <View style={styles.spacer} />
        <Button title="Play Latest" onPress={() => {}} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#f6f5f1",
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    marginBottom: 16,
  },
  card: {
    width: "100%",
    padding: 20,
    borderRadius: 16,
    backgroundColor: "#ffffff",
    shadowColor: "#000000",
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  body: {
    fontSize: 16,
    marginBottom: 16,
  },
  spacer: {
    height: 12,
  },
});
