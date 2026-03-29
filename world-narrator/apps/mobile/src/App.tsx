import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Linking,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

type JobStatus = {
  job_id: string;
  status: string;
  stage: string;
  progress: number;
  audio_id?: string | null;
  stream_url?: string | null;
  message?: string | null;
  error_message?: string | null;
  preview_text?: string | null;
};

type HistoryItem = JobStatus & { requestedAt: string; imageUrl: string };

const gatewayBase = "http://localhost:8000";
const starterUrl = "https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=1024&q=80";

export default function App() {
  const [imageUrl, setImageUrl] = useState(starterUrl);
  const [job, setJob] = useState<JobStatus | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [gatewayUrl, setGatewayUrl] = useState(gatewayBase);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollable = useMemo(() => {
    return job && job.status !== "ready" && job.status !== "failed";
  }, [job]);

  useEffect(() => {
    if (!pollable || !job) {
      return;
    }
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`${gatewayUrl}/v1/jobs/${job.job_id}`);
        const payload: JobStatus = await response.json();
        setJob(payload);
        setHistory((current) =>
          current.map((item) => (item.job_id === payload.job_id ? { ...item, ...payload } : item))
        );
      } catch {
        setError("Unable to refresh job status.");
      }
    }, 2500);
    return () => clearInterval(timer);
  }, [gatewayUrl, job, pollable]);

  const submitImage = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await fetch(`${gatewayUrl}/v1/narrate/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_url: imageUrl, strategy_mode: "faithful" }),
      });
      const payload: JobStatus = await response.json();
      if (!response.ok) {
        throw new Error(payload.error_message || payload.message || "Upload failed");
      }
      setJob(payload);
      setHistory((current) => [
        { ...payload, requestedAt: new Date().toISOString(), imageUrl },
        ...current.filter((item) => item.job_id !== payload.job_id),
      ]);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Upload failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const openAudio = async (target?: string | null) => {
    if (!target) {
      return;
    }
    const normalized = target.startsWith("http") ? target : `${gatewayUrl}${target}`;
    await Linking.openURL(normalized);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>WorldNarrator</Text>
        <Text style={styles.subtitle}>Submit an image URL, watch the async pipeline, then open the generated audio.</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Gateway URL</Text>
          <TextInput style={styles.input} value={gatewayUrl} onChangeText={setGatewayUrl} autoCapitalize="none" />
          <Text style={styles.label}>Image URL</Text>
          <TextInput style={[styles.input, styles.largeInput]} value={imageUrl} onChangeText={setImageUrl} autoCapitalize="none" multiline />
          <Pressable style={styles.primaryButton} onPress={submitImage} disabled={isSubmitting}>
            <Text style={styles.primaryButtonText}>{isSubmitting ? "Submitting..." : "Start Narration Job"}</Text>
          </Pressable>
          {error ? <Text style={styles.error}>{error}</Text> : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Latest Job</Text>
          {job ? (
            <>
              <Text style={styles.jobLine}>Job: {job.job_id}</Text>
              <Text style={styles.jobLine}>Status: {job.status}</Text>
              <Text style={styles.jobLine}>Stage: {job.stage}</Text>
              <Text style={styles.jobLine}>Progress: {job.progress}%</Text>
              <Text style={styles.jobLine}>Message: {job.message || "-"}</Text>
              {job.preview_text ? <Text style={styles.preview}>{job.preview_text}</Text> : null}
              {pollable ? <ActivityIndicator color="#8a3b12" style={styles.spinner} /> : null}
              <Pressable style={styles.secondaryButton} onPress={() => openAudio(job.stream_url)} disabled={!job.stream_url}>
                <Text style={styles.secondaryButtonText}>Open Audio</Text>
              </Pressable>
            </>
          ) : (
            <Text style={styles.empty}>No jobs yet.</Text>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Recent Jobs</Text>
          {history.length === 0 ? <Text style={styles.empty}>History appears here after submission.</Text> : null}
          {history.map((item) => (
            <View key={item.job_id} style={styles.historyItem}>
              <Text style={styles.historyTitle}>{item.stage.toUpperCase()} ? {item.progress}%</Text>
              <Text style={styles.jobLine}>{item.imageUrl}</Text>
              <Text style={styles.jobLine}>{item.preview_text || item.message || item.status}</Text>
              <Pressable style={styles.linkButton} onPress={() => openAudio(item.stream_url)} disabled={!item.stream_url}>
                <Text style={styles.linkText}>Open Result</Text>
              </Pressable>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f3ecdf",
  },
  content: {
    padding: 20,
    gap: 16,
  },
  title: {
    fontSize: 32,
    fontWeight: "800",
    color: "#2d1c10",
  },
  subtitle: {
    fontSize: 15,
    color: "#5f4634",
    lineHeight: 22,
  },
  card: {
    backgroundColor: "#fffaf1",
    borderRadius: 18,
    padding: 18,
    gap: 10,
    borderWidth: 1,
    borderColor: "#e2d0bc",
  },
  label: {
    fontSize: 13,
    fontWeight: "700",
    color: "#6f513d",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  input: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#d6c0a9",
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
  },
  largeInput: {
    minHeight: 84,
    textAlignVertical: "top",
  },
  primaryButton: {
    backgroundColor: "#8a3b12",
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 4,
  },
  primaryButtonText: {
    color: "#fff7f2",
    fontSize: 16,
    fontWeight: "700",
  },
  secondaryButton: {
    backgroundColor: "#efe2cf",
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
  },
  secondaryButtonText: {
    color: "#4c2a16",
    fontWeight: "700",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: "#2d1c10",
  },
  jobLine: {
    fontSize: 14,
    color: "#5f4634",
  },
  preview: {
    fontSize: 15,
    color: "#2d1c10",
    lineHeight: 22,
  },
  spinner: {
    marginVertical: 8,
  },
  empty: {
    color: "#7a6656",
  },
  error: {
    color: "#9f1c1c",
    fontWeight: "600",
  },
  historyItem: {
    borderTopWidth: 1,
    borderTopColor: "#eadccb",
    paddingTop: 12,
    gap: 4,
  },
  historyTitle: {
    fontSize: 13,
    fontWeight: "800",
    color: "#8a3b12",
  },
  linkButton: {
    paddingVertical: 6,
  },
  linkText: {
    color: "#8a3b12",
    fontWeight: "700",
  },
});
