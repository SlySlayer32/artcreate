# StoryTime — Setup Guide

## 1. Install new dependencies

Run this in your project folder:

```bash
npm install express @google/generative-ai dotenv
```

## 2. Add the files

Copy the following files into the **root** of your project (same level as `package.json`):
- `server.js`
- `vite.config.ts`

## 3. Set up your .env file

Create a `.env` file in the root of your project:

```
GEMINI_API_KEY=your_gemini_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

## 4. Update your package.json scripts

Add these two scripts to your `package.json`:

```json
"scripts": {
  "dev": "vite",
  "server": "node server.js",
  "start": "concurrently \"npm run server\" \"npm run dev\""
}
```

Then install concurrently:
```bash
npm install concurrently --save-dev
```

## 5. Run the app

```bash
npm run start
```

This starts both the Express backend (port 3001) and the Vite frontend (port 5173) together.

Open: http://localhost:5173

---

## How it works

1. **Take/upload a photo** of a storybook page
2. **Gemini Vision** reads the page, identifies characters + dialogue, assigns emotions
3. **ElevenLabs** generates audio for each block with different voices and emotional settings
4. The audio chunks are stitched together into one seamless narration

## Voice assignments
- **Narrator** → Daniel (rich, warm storyteller voice)
- **Character 1** → Adam (deep, warm)
- **Character 2** → Sarah (bright, expressive)  
- **Character 3** → Arnold (gravelly, character-y)
- Additional characters cycle through the voice pool

Emotions like "scared", "excited", "angry", "whispering" automatically adjust ElevenLabs' stability and style settings for dramatic effect.
