import "dotenv/config";
import express from "express";
import { createServer as createViteServer } from "vite";
import multer from "multer";
import cors from "cors";
import fs from "fs";
import path from "path";
import md5 from "md5";
import axios from "axios";
import { GoogleGenAI } from "@google/genai";
import { fileURLToPath } from "url";

// Fix for __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: "100mb" })); // Increase limit for base64 images

// Request Logging Middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Ensure cache directory exists
const CACHE_DIR = path.join(__dirname, "cache");
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR);
}

// Serve cached audio files statically
app.use("/cache", express.static(CACHE_DIR));

// Configure Multer for memory storage (if we were using multipart, but we'll accept base64 JSON for simplicity as requested)
const upload = multer({ storage: multer.memoryStorage() });

// --- Gemini Setup ---
// We use lazy initialization for the API key to avoid crashes if it's missing at startup
const getGeminiClient = () => {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not set");
  }
  return new GoogleGenAI({ apiKey });
};

// --- ElevenLabs Setup ---
const getElevenLabsKey = () => {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  if (!apiKey) {
    throw new Error("ELEVENLABS_API_KEY is not set");
  }
  return apiKey;
};

// Voice Mapping (You can customize these IDs)
// These are standard ElevenLabs pre-made voices
const VOICE_MAPPING: Record<string, string> = {
  narrator: "21m00Tcm4TlvDq8ikWAM", // Rachel
  dragon: "nPczCjzI2devNBz1zQrb", // Brian (Deep voice)
  little_girl: "AZnzlk1XvdvUeBnXmlld", // Domi
  default: "21m00Tcm4TlvDq8ikWAM", // Rachel (Fallback)
};

// --- API Routes ---

// --- Helper for Structured Errors ---
const sendError = (res: express.Response, status: number, message: string, step: string, technical?: any) => {
  const errorDetails = {
    step,
    code: status,
    technical: technical instanceof Error ? technical.message : (typeof technical === 'object' ? JSON.stringify(technical, null, 2) : technical),
    timestamp: new Date().toISOString()
  };
  console.error(`[Error] Step: ${step} | Message: ${message} | Details:`, errorDetails);
  
  res.status(status).json({
    error: message,
    details: errorDetails
  });
};

// --- API Routes ---

app.post("/api/analyze-page", async (req, res) => {
  try {
    const { imageBase64 } = req.body;

    if (!imageBase64) {
      return sendError(res, 400, "No image provided", "Input Validation");
    }

    console.log("Received image, processing with Gemini...");
    
    // Debug: Check if key exists
    if (!process.env.GEMINI_API_KEY) {
      return sendError(res, 500, "Gemini API Key is missing in server environment", "Configuration");
    }

    // Step A: Vision (Gemini)
    let apiKey = process.env.GEMINI_API_KEY.trim();
    
    // Sanitize key
    if ((apiKey.startsWith('"') && apiKey.endsWith('"')) || (apiKey.startsWith("'") && apiKey.endsWith("'"))) {
      apiKey = apiKey.slice(1, -1);
    }

    // Strict Debugging for API Key
    const keyPrefix = apiKey.substring(0, 4);
    const keyLength = apiKey.length;
    console.log(`DEBUG: Gemini API Key loaded. Prefix: '${keyPrefix}', Length: ${keyLength}`);

    // Check for common placeholder patterns
    if (apiKey.startsWith("MY_") || apiKey.startsWith("YOUR_") || apiKey === "GEMINI_API_KEY") {
      return sendError(res, 401, "Placeholder API Key Detected", "Configuration", {
        message: `The API key '${apiKey}' appears to be a placeholder.`,
        action: "Please open the Secrets panel (bottom left) and paste your actual Google Gemini API key (it should start with 'AIza').",
        keyPrefix: keyPrefix
      });
    }

    if (!apiKey.startsWith("AIza")) {
      console.warn("WARNING: Gemini API Key does not start with 'AIza'. Proceeding anyway, but this key might be invalid.");
    }
    
    const ai = new GoogleGenAI({ apiKey });
    
    // Detect mime type
    const mimeMatch = imageBase64.match(/^data:(image\/\w+);base64,/);
    const mimeType = mimeMatch ? mimeMatch[1] : "image/jpeg";
    const cleanBase64 = imageBase64.replace(/^data:image\/\w+;base64,/, "");

    console.log(`Processing image with mimeType: ${mimeType}`);

    const systemInstruction = `You are an expert children's book voice director. Read the text on this page and look at the illustrations. Break the text down into sequential dialogue and narrative blocks. Identify who is speaking (e.g., narrator, dragon, little_girl). Output ONLY a valid JSON array of objects matching this interface: { speaker: string; text: string; emotion: string; }.`;

    // Switch to the user-requested model
    const modelName = "gemini-2.5-flash";

    try {
      const response = await ai.models.generateContent({
        model: modelName,
        contents: {
          parts: [
            { inlineData: { mimeType: mimeType, data: cleanBase64 } },
            { text: "Analyze this page according to the system instructions." },
          ],
        },
        config: {
          systemInstruction: systemInstruction,
          responseMimeType: "application/json",
        },
      });

      const jsonText = response.text;
      if (!jsonText) {
        return sendError(res, 500, "Empty response from Gemini", "Gemini Analysis");
      }
      
      // Clean Markdown code blocks if present
      const cleanJsonText = jsonText.replace(/```json\n?|\n?```/g, "").trim();

      // Parse JSON
      let script: Array<{ speaker: string; text: string; emotion: string }>;
      try {
        script = JSON.parse(cleanJsonText);
      } catch (e) {
        return sendError(res, 500, "Failed to parse AI response as JSON", "Response Parsing", {
          originalResponse: cleanJsonText.substring(0, 200) + "..." // Log first 200 chars
        });
      }

      res.json({ script });

    } catch (apiError: any) {
       // Check for specific API errors
       const isAuthError = apiError.message?.includes("API key") || apiError.status === 400 || apiError.status === 401;
       const status = isAuthError ? 401 : 500;
       const msg = isAuthError ? "Gemini API Key rejected" : "Gemini API call failed";
       
       // Add key debug info to the error response
       const debugInfo = {
         keyPrefix: keyPrefix,
         keyLength: keyLength,
         model: modelName,
         originalError: apiError
       };

       return sendError(res, status, msg, "Gemini Analysis", debugInfo);
    }

  } catch (error: any) {
    return sendError(res, 500, "Unexpected server error during analysis", "General Analysis", error);
  }
});

app.post("/api/synthesize-audio", async (req, res) => {
  try {
    const { script } = req.body;

    if (!script || !Array.isArray(script)) {
      return sendError(res, 400, "Invalid script format provided", "Input Validation");
    }

    // Step B: Credit-Saving Cache
    const scriptHash = md5(JSON.stringify(script));
    const cachedFilePath = path.join(CACHE_DIR, `${scriptHash}.mp3`);
    
    const protocol = req.headers['x-forwarded-proto'] || req.protocol;
    const host = req.headers['x-forwarded-host'] || req.get('host');
    const cachedFileUrl = `${protocol}://${host}/cache/${scriptHash}.mp3`;

    if (fs.existsSync(cachedFilePath)) {
      console.log("Cache hit! Returning existing audio.");
      res.json({ audioUrl: cachedFileUrl });
      return;
    }

    console.log("Cache miss. Generating audio with ElevenLabs...");

    // Step C: ElevenLabs Generation
    let elevenLabsKey;
    try {
      elevenLabsKey = getElevenLabsKey();
    } catch (e) {
      return sendError(res, 500, "ElevenLabs API Key is missing", "Configuration");
    }

    const audioBuffers: Buffer[] = [];

    for (const [index, block] of script.entries()) {
      const speakerKey = block.speaker.toLowerCase().replace(/\s+/g, "_");
      let voiceId = VOICE_MAPPING["default"];
      
      if (VOICE_MAPPING[speakerKey]) {
        voiceId = VOICE_MAPPING[speakerKey];
      } else if (speakerKey.includes("dragon") || speakerKey.includes("monster")) {
        voiceId = VOICE_MAPPING["dragon"];
      } else if (speakerKey.includes("girl") || speakerKey.includes("child")) {
        voiceId = VOICE_MAPPING["little_girl"];
      }

      console.log(`Generating audio for block ${index + 1}/${script.length} (${block.speaker})...`);

      try {
        const ttsResponse = await axios.post(
          `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
          {
            text: block.text,
            model_id: "eleven_turbo_v2_5",
            voice_settings: {
              stability: 0.5,
              similarity_boost: 0.75,
            },
          },
          {
            headers: {
              "xi-api-key": elevenLabsKey,
              "Content-Type": "application/json",
            },
            responseType: "arraybuffer",
          }
        );
        audioBuffers.push(Buffer.from(ttsResponse.data));
      } catch (err: any) {
        // Log individual block failure but try to continue if possible? 
        // Or fail the whole request? Failing whole request is safer for consistency.
        // Let's return error immediately.
        const isAuthError = err.response?.status === 401;
        return sendError(res, isAuthError ? 401 : 500, "Failed to generate audio for a block", "Audio Synthesis", {
          blockIndex: index,
          speaker: block.speaker,
          elevenLabsError: err.response?.data ? JSON.parse(Buffer.from(err.response.data).toString()) : err.message
        });
      }
    }

    if (audioBuffers.length === 0) {
      return sendError(res, 500, "No audio was generated", "Audio Synthesis");
    }

    // Step E: Audio Stitching
    try {
      const finalBuffer = Buffer.concat(audioBuffers);
      fs.writeFileSync(cachedFilePath, finalBuffer);
    } catch (writeErr) {
      return sendError(res, 500, "Failed to save audio file to disk", "File System", writeErr);
    }

    console.log("Audio generation complete.");
    res.json({ audioUrl: cachedFileUrl });

  } catch (error: any) {
    return sendError(res, 500, "Unexpected server error during synthesis", "General Synthesis", error);
  }
});

// --- Server Start ---
async function startServer() {
  // Vite middleware for development (so the web preview works)
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    // In production, serve static files from dist
    app.use(express.static(path.join(__dirname, "dist")));
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
