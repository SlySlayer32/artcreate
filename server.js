import express from "express";
import dotenv from "dotenv";
import { GoogleGenerativeAI } from "@google/generative-ai";

dotenv.config();

const app = express();
app.use(express.json({ limit: "25mb" }));

// ─── Helpers ────────────────────────────────────────────────────────────────

function structuredError(res, status, message, details = {}) {
  return res.status(status).json({
    error: message,
    details: {
      timestamp: new Date().toISOString(),
      ...details,
    },
  });
}

// Map emotion → ElevenLabs voice settings for expressive storytelling
function emotionToVoiceSettings(emotion = "") {
  const e = emotion.toLowerCase();

  if (e.includes("excit") || e.includes("happy") || e.includes("joyful")) {
    return { stability: 0.25, similarity_boost: 0.75, style: 0.8, use_speaker_boost: true };
  }
  if (e.includes("scare") || e.includes("fear") || e.includes("nervous")) {
    return { stability: 0.2, similarity_boost: 0.7, style: 0.7, use_speaker_boost: true };
  }
  if (e.includes("angry") || e.includes("fierce") || e.includes("furious")) {
    return { stability: 0.15, similarity_boost: 0.8, style: 0.9, use_speaker_boost: true };
  }
  if (e.includes("sad") || e.includes("cry") || e.includes("upset")) {
    return { stability: 0.45, similarity_boost: 0.75, style: 0.6, use_speaker_boost: true };
  }
  if (e.includes("whisper") || e.includes("quiet") || e.includes("soft")) {
    return { stability: 0.7, similarity_boost: 0.6, style: 0.3, use_speaker_boost: false };
  }
  if (e.includes("dramatic") || e.includes("tense") || e.includes("suspense")) {
    return { stability: 0.3, similarity_boost: 0.8, style: 0.75, use_speaker_boost: true };
  }
  if (e.includes("gentle") || e.includes("calm") || e.includes("warm")) {
    return { stability: 0.6, similarity_boost: 0.75, style: 0.4, use_speaker_boost: true };
  }

  // Default narrator tone — measured and clear
  return { stability: 0.5, similarity_boost: 0.8, style: 0.45, use_speaker_boost: true };
}

// Assign a voice ID by speaker name — narrator gets a warm storyteller voice,
// characters rotate through a small cast so each sounds distinct.
const VOICE_POOL = [
  "pNInz6obpgDQGcFmaJgB", // Adam  — warm, deep
  "EXAVITQu4vr4xnSDxMaL", // Sarah — bright, expressive
  "VR6AewLTigWG4xSOukaG", // Arnold — gravelly, character-y
  "TX3LPaxmHKxFdv7VOQHJ", // Liam  — young, energetic
  "XB0fDUnXU5powFXDhCwa", // Charlotte — playful
];
const NARRATOR_VOICE = "onwK4e9ZLuTAKqWW03F9"; // Daniel — rich narrator

function getVoiceForSpeaker(speaker, speakerIndex) {
  if (speaker.toLowerCase() === "narrator") return NARRATOR_VOICE;
  return VOICE_POOL[speakerIndex % VOICE_POOL.length];
}

// ─── Route: Analyze Page ─────────────────────────────────────────────────────

app.post("/api/analyze-page", async (req, res) => {
  const { imageBase64 } = req.body;

  if (!process.env.GEMINI_API_KEY) {
    return structuredError(res, 500, "Gemini API Key is missing", {
      step: "analyze-page",
      code: "MISSING_KEY",
    });
  }

  if (!imageBase64) {
    return structuredError(res, 400, "No image provided", {
      step: "analyze-page",
      code: "NO_IMAGE",
    });
  }

  try {
    // Strip the data URL prefix and grab the mime type
    const matches = imageBase64.match(/^data:(image\/\w+);base64,(.+)$/);
    if (!matches) {
      return structuredError(res, 400, "Invalid image format", {
        step: "analyze-page",
        code: "BAD_FORMAT",
      });
    }
    const mimeType = matches[1];
    const base64Data = matches[2];

    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `You are analyzing a children's storybook page to create a dramatic read-aloud script.

Your job:
1. Read ALL text on the page carefully.
2. Split it into speaker blocks — "Narrator" for story text, character names for dialogue.
3. Detect the emotional tone of each block based on context, punctuation, and story events.
4. If a character's name is unknown, infer it from context or call them "Character".

Return ONLY a raw JSON array — no markdown, no explanation, no code fences.

Each object must have exactly these fields:
- "speaker": string — "Narrator" or the character's name
- "text": string — the exact words from the page
- "emotion": string — one of: gentle, excited, dramatic, scared, angry, sad, whispering, joyful, tense, fierce, warm

Example output:
[
  {"speaker":"Narrator","text":"The forest was dark and very quiet.","emotion":"tense"},
  {"speaker":"Lily","text":"Hello? Is anyone there?","emotion":"scared"},
  {"speaker":"Owl","text":"Who goes there!","emotion":"dramatic"}
]

Now analyze the storybook page in the image and return the JSON array.`;

    const result = await model.generateContent([
      prompt,
      { inlineData: { mimeType, data: base64Data } },
    ]);

    const rawText = result.response.text().trim();

    // Safely parse — strip any accidental markdown fences
    const cleaned = rawText.replace(/^```(?:json)?\s*/i, "").replace(/\s*```\s*$/, "").trim();
    let script;
    try {
      script = JSON.parse(cleaned);
    } catch {
      return structuredError(res, 500, "Failed to parse script from Gemini response", {
        step: "analyze-page",
        code: "PARSE_ERROR",
        technical: rawText.slice(0, 500),
      });
    }

    if (!Array.isArray(script) || script.length === 0) {
      return structuredError(res, 500, "No readable text found on this page", {
        step: "analyze-page",
        code: "EMPTY_SCRIPT",
      });
    }

    return res.json({ script });
  } catch (err) {
    console.error("analyze-page error:", err);
    return structuredError(res, 500, "Failed to analyze the image", {
      step: "analyze-page",
      code: "GEMINI_ERROR",
      technical: err.message,
    });
  }
});

// ─── Route: Synthesize Audio ─────────────────────────────────────────────────

app.post("/api/synthesize-audio", async (req, res) => {
  const { script } = req.body;

  if (!process.env.ELEVENLABS_API_KEY) {
    return structuredError(res, 500, "ElevenLabs API Key is missing", {
      step: "synthesize-audio",
      code: "MISSING_KEY",
    });
  }

  if (!Array.isArray(script) || script.length === 0) {
    return structuredError(res, 400, "No script provided", {
      step: "synthesize-audio",
      code: "NO_SCRIPT",
    });
  }

  try {
    // Build a speaker→index map so each unique character gets a consistent voice
    const speakerMap = {};
    let speakerCount = 0;
    for (const block of script) {
      const key = block.speaker.toLowerCase();
      if (!(key in speakerMap)) {
        speakerMap[key] = speakerCount++;
      }
    }

    // Generate audio for each block, in order
    const audioChunks = [];

    for (const block of script) {
      const speakerIndex = speakerMap[block.speaker.toLowerCase()];
      const voiceId = getVoiceForSpeaker(block.speaker, speakerIndex);
      const voiceSettings = emotionToVoiceSettings(block.emotion);

      const elevenRes = await fetch(
        `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
        {
          method: "POST",
          headers: {
            "xi-api-key": process.env.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            Accept: "audio/mpeg",
          },
          body: JSON.stringify({
            text: block.text,
            model_id: "eleven_multilingual_v2", // best expressiveness
            voice_settings: voiceSettings,
          }),
        }
      );

      if (!elevenRes.ok) {
        const errBody = await elevenRes.text();
        return structuredError(res, 502, "ElevenLabs rejected the request", {
          step: "synthesize-audio",
          code: "ELEVEN_ERROR",
          technical: `Status ${elevenRes.status}: ${errBody.slice(0, 300)}`,
        });
      }

      const arrayBuffer = await elevenRes.arrayBuffer();
      audioChunks.push(Buffer.from(arrayBuffer));
    }

    // Stitch all MP3 chunks together — browsers handle concatenated MP3s fine
    const combined = Buffer.concat(audioChunks);
    const audioUrl = `data:audio/mpeg;base64,${combined.toString("base64")}`;

    return res.json({ audioUrl });
  } catch (err) {
    console.error("synthesize-audio error:", err);
    return structuredError(res, 500, "Failed to generate audio", {
      step: "synthesize-audio",
      code: "SYNTHESIS_ERROR",
      technical: err.message,
    });
  }
});

// ─── Start ───────────────────────────────────────────────────────────────────

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`✅ StoryTime backend running on http://localhost:${PORT}`);
});
