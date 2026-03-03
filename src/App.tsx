/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef } from "react";
import { Camera, Play, Pause, RotateCcw, BookOpen, Loader2, Mic } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface ScriptBlock {
  speaker: string;
  text: string;
  emotion: string;
}

export default function App() {
  const [loadingState, setLoadingState] = useState<"idle" | "uploading" | "analyzing" | "synthesizing">("idle");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [script, setScript] = useState<ScriptBlock[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [error, setError] = useState<{ message: string; details?: any } | null>(null);

  const [retryCount, setRetryCount] = useState(0);

  const fetchWithRetry = async (url: string, options: RequestInit, maxRetries = 3): Promise<any> => {
    let retries = 0;
    while (retries < maxRetries) {
      try {
        const response = await fetch(url, options);
        
        // Helper to safely parse JSON or get text
        const getBody = async (res: Response) => {
          const text = await res.text();
          try {
            return JSON.parse(text);
          } catch {
            return { error: text || res.statusText };
          }
        };

        if (!response.ok) {
           const body = await getBody(response);
           // If the server sent our structured error format
           if (body.details) {
             throw { message: body.error, details: body.details };
           }
           
           const errorMessage = body.error || `Error ${response.status}`;
           
           // If it's a 500 error, it might be transient, so we retry. 
           if (response.status >= 500) {
             throw new Error(`Server Error (${response.status}): ${errorMessage}`);
           } else {
             // Don't retry client errors (4xx)
             throw new Error(errorMessage);
           }
        }
        
        // Success case
        const data = await getBody(response);
        return data;
        
      } catch (err: any) {
        // If it's our structured error object (has details), don't retry, just throw
        if (err.details) {
           throw err;
        }
        
        retries++;
        setRetryCount(retries);
        console.log(`Attempt ${retries} failed: ${err.message}`);
        
        const isClientError = !err.message.includes("Server Error") && !err.message.includes("fetch failed");
        
        if (retries >= maxRetries || isClientError) {
          const step = url.includes('analyze') ? 'Analysis' : 'Synthesis';
          throw new Error(`${step} Failed: ${err.message}`);
        }
        
        const delay = Math.pow(2, retries - 1) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoadingState("uploading");
    setError(null);
    setAudioUrl(null);
    setScript([]);
    setRetryCount(0);

    try {
      // Convert to Base64
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onloadend = async () => {
        const base64data = reader.result as string;

        try {
          // Step 1: Analyze Page
          setLoadingState("analyzing");
          setRetryCount(0);
          
          const analyzeData = await fetchWithRetry("/api/analyze-page", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ imageBase64: base64data }),
          });
          
          setScript(analyzeData.script);

          // Step 2: Synthesize Audio
          setLoadingState("synthesizing");
          setRetryCount(0);
          
          const synthesizeData = await fetchWithRetry("/api/synthesize-audio", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ script: analyzeData.script }),
          });

          setAudioUrl(synthesizeData.audioUrl);
        } catch (err: any) {
          // Handle both structured and simple errors
          if (err.details) {
            setError({ message: err.message, details: err.details });
          } else {
            setError({ message: err.message });
          }
        } finally {
          setLoadingState("idle");
          setRetryCount(0);
        }
      };
    } catch (err: any) {
      setError({ message: "Failed to read file" });
      setLoadingState("idle");
    }
  };

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleAudioError = () => {
    setIsPlaying(false);
    setError("Failed to load audio. Please check your connection.");
  };

  return (
    <div className="min-h-screen bg-stone-100 text-stone-900 font-sans selection:bg-orange-200">
      <div className="max-w-md mx-auto min-h-screen flex flex-col bg-white shadow-2xl overflow-hidden relative">
        
        {/* Header */}
        <header className="bg-orange-500 text-white p-6 pt-12 rounded-b-[2.5rem] shadow-lg z-10 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
            <div className="absolute top-[-50%] left-[-50%] w-[200%] h-[200%] bg-[radial-gradient(circle,white,transparent)] animate-pulse"></div>
          </div>
          <div className="flex items-center justify-between relative z-10">
            <div>
              <h1 className="text-3xl font-bold tracking-tight font-serif">StoryTime</h1>
              <p className="text-orange-100 text-sm font-medium opacity-90">Magic Reader</p>
            </div>
            <div className="bg-white/20 p-3 rounded-full backdrop-blur-sm">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 flex flex-col items-center justify-center relative">
          
          <AnimatePresence mode="wait">
            {!audioUrl && loadingState === "idle" && !error && (
              <motion.div 
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="text-center w-full"
              >
                <div className="flex gap-4 mb-8 justify-center">
                  {/* Camera Button */}
                  <div className="relative group cursor-pointer flex-1 max-w-[160px]">
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 z-20 cursor-pointer"
                    />
                    <div className="aspect-square mx-auto bg-stone-50 rounded-3xl border-2 border-stone-200 flex flex-col items-center justify-center group-hover:border-orange-400 group-hover:bg-orange-50 transition-all duration-300 shadow-sm">
                      <div className="bg-orange-500 text-white p-4 rounded-full shadow-md group-hover:scale-110 transition-transform duration-300 mb-3">
                        <Camera className="w-8 h-8" />
                      </div>
                      <span className="font-medium text-stone-600 text-sm">Take Photo</span>
                    </div>
                  </div>

                  {/* Gallery Button */}
                  <div className="relative group cursor-pointer flex-1 max-w-[160px]">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 z-20 cursor-pointer"
                    />
                    <div className="aspect-square mx-auto bg-stone-50 rounded-3xl border-2 border-stone-200 flex flex-col items-center justify-center group-hover:border-blue-400 group-hover:bg-blue-50 transition-all duration-300 shadow-sm">
                      <div className="bg-blue-500 text-white p-4 rounded-full shadow-md group-hover:scale-110 transition-transform duration-300 mb-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                      </div>
                      <span className="font-medium text-stone-600 text-sm">Upload Image</span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-2xl border border-blue-100 text-left">
                  <h3 className="text-blue-800 font-semibold mb-1 flex items-center gap-2">
                    <span className="bg-blue-200 text-blue-700 text-xs px-2 py-0.5 rounded-full">Tip</span>
                    How it works
                  </h3>
                  <p className="text-blue-600 text-sm leading-relaxed">
                    Take a photo of a storybook page. We'll identify the characters and read it out loud with different voices!
                  </p>
                </div>
              </motion.div>
            )}

            {loadingState !== "idle" && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center text-center"
              >
                <div className="relative mb-8">
                  <div className="w-32 h-32 border-4 border-orange-100 rounded-full"></div>
                  <div className="absolute inset-0 border-4 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    {loadingState === "uploading" && <Camera className="w-10 h-10 text-orange-500 animate-pulse" />}
                    {loadingState === "analyzing" && <BookOpen className="w-10 h-10 text-orange-500 animate-pulse" />}
                    {loadingState === "synthesizing" && <Mic className="w-10 h-10 text-orange-500 animate-pulse" />}
                  </div>
                </div>
                
                <motion.h2 
                  key={loadingState}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-2xl font-bold text-stone-800 mb-2"
                >
                  {loadingState === "uploading" && "Uploading Image..."}
                  {loadingState === "analyzing" && "Reading the Page..."}
                  {loadingState === "synthesizing" && "Creating Voices..."}
                </motion.h2>
                
                <motion.p 
                  key={`${loadingState}-sub`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-stone-500"
                >
                  {loadingState === "uploading" && "Preparing your photo"}
                  {loadingState === "analyzing" && "Identifying characters and dialogue"}
                  {loadingState === "synthesizing" && "Stitching audio parts together"}
                </motion.p>
                
                {retryCount > 0 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-4 text-orange-600 text-sm font-medium bg-orange-50 px-3 py-1 rounded-full inline-block"
                  >
                    Taking longer than usual... (Attempt {retryCount}/3)
                  </motion.div>
                )}
              </motion.div>
            )}

            {audioUrl && !error && (
              <motion.div
                key="player"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full flex flex-col h-full"
              >
                {/* Audio Player Card */}
                <div className="bg-white rounded-3xl shadow-xl border border-stone-100 overflow-hidden mb-6">
                  <div className="bg-stone-900 p-6 flex flex-col items-center justify-center text-white relative overflow-hidden">
                    <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]"></div>
                    <div className="w-full flex justify-between items-center mb-4 z-10">
                      <span className="text-xs font-mono text-stone-400 uppercase tracking-widest">Now Playing</span>
                      <div className="flex gap-1">
                        {[1,2,3].map(i => (
                          <div key={i} className={`w-1 h-1 rounded-full bg-green-400 ${isPlaying ? 'animate-ping' : ''}`} style={{animationDelay: `${i*0.2}s`}}></div>
                        ))}
                      </div>
                    </div>
                    
                    <button 
                      onClick={togglePlay}
                      className="w-20 h-20 bg-white text-stone-900 rounded-full flex items-center justify-center hover:scale-105 active:scale-95 transition-all shadow-lg z-10"
                    >
                      {isPlaying ? <Pause className="w-8 h-8 fill-current" /> : <Play className="w-8 h-8 fill-current ml-1" />}
                    </button>
                    
                    <audio 
                      ref={audioRef} 
                      src={audioUrl} 
                      onEnded={handleAudioEnded}
                      onPlay={() => setIsPlaying(true)}
                      onPause={() => setIsPlaying(false)}
                      onError={handleAudioError}
                      className="hidden" 
                    />
                  </div>
                  
                  <div className="p-4 bg-stone-50 border-t border-stone-100 flex justify-between items-center">
                     <button 
                      onClick={() => {
                        if(audioRef.current) {
                          audioRef.current.currentTime = 0;
                          audioRef.current.play();
                        }
                      }}
                      className="text-stone-400 hover:text-stone-600 transition-colors"
                    >
                      <RotateCcw className="w-5 h-5" />
                    </button>
                    <span className="text-xs font-medium text-stone-400">Generated by ElevenLabs</span>
                  </div>
                </div>

                {/* Script Display */}
                <div className="flex-1 overflow-y-auto pr-2 space-y-4 pb-20">
                  <h3 className="text-sm font-bold text-stone-400 uppercase tracking-wider mb-2">Detected Script</h3>
                  {script.map((block, idx) => (
                    <div key={idx} className="bg-white p-4 rounded-xl shadow-sm border border-stone-100">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-xs font-bold px-2 py-1 rounded-md uppercase tracking-wide ${
                          block.speaker.toLowerCase().includes('narrator') ? 'bg-stone-100 text-stone-600' :
                          block.speaker.toLowerCase().includes('dragon') ? 'bg-red-100 text-red-600' :
                          'bg-orange-100 text-orange-600'
                        }`}>
                          {block.speaker}
                        </span>
                        <span className="text-xs text-stone-400 italic">{block.emotion}</span>
                      </div>
                      <p className="text-stone-700 leading-relaxed font-medium">
                        {block.text}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Reset Button */}
                <div className="absolute bottom-0 left-0 w-full p-6 bg-gradient-to-t from-white via-white to-transparent pt-12">
                  <button 
                    onClick={() => {
                      setAudioUrl(null);
                      setScript([]);
                    }}
                    className="w-full bg-stone-900 text-white font-semibold py-4 rounded-xl shadow-lg hover:bg-stone-800 transition-colors"
                  >
                    Read Another Page
                  </button>
                </div>
              </motion.div>
            )}

            {error && (
              <motion.div
                key="error"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center p-6"
              >
                <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100 mb-6">
                  <p className="font-bold mb-1">Something went wrong</p>
                  <p className="font-medium text-sm opacity-90">{error.message}</p>
                  
                  {/* Technical Details Block */}
                  {error.details && (
                    <details className="mt-4 text-left bg-white rounded-lg border border-red-100 overflow-hidden group">
                      <summary className="p-3 text-[10px] font-bold text-stone-500 uppercase tracking-wider cursor-pointer hover:bg-stone-50 flex items-center justify-between select-none list-none">
                        <span>Technical Details</span>
                        <span className="group-open:rotate-180 transition-transform duration-200">▼</span>
                      </summary>
                      <div className="p-3 pt-0 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs font-mono text-stone-600">
                        <span className="text-stone-400">Step:</span>
                        <span className="font-semibold text-red-600">{error.details.step}</span>
                        
                        <span className="text-stone-400">Code:</span>
                        <span>{error.details.code}</span>
                        
                        <span className="text-stone-400">Time:</span>
                        <span>{error.details.timestamp?.split('T')[1]?.split('.')[0]}</span>
                        
                        {error.details.technical && (
                          <>
                            <span className="text-stone-400 col-span-2 mt-2">Error Info:</span>
                            <div className="col-span-2 break-all bg-stone-50 p-2 rounded border border-stone-100 max-h-32 overflow-y-auto whitespace-pre-wrap">
                              {error.details.technical}
                            </div>
                          </>
                        )}
                      </div>
                    </details>
                  )}

                  {/* Only show generic fix instructions if it's NOT a specific API rejection we've already debugged */}
                  {(error.message.includes("API Key is missing") || error.message.includes("not set")) && (
                    <div className="mt-4 bg-white p-3 rounded-lg border border-red-100 text-left">
                      <p className="text-xs font-bold text-stone-700 mb-2">How to fix:</p>
                      <ol className="list-decimal list-inside text-xs text-stone-600 space-y-1">
                        <li>Get a free API key from <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-blue-600 underline">Google AI Studio</a></li>
                        <li>Click the <strong>Secrets</strong> button in the bottom panel</li>
                        <li>Add <code className="bg-stone-100 px-1 rounded">GEMINI_API_KEY</code></li>
                      </ol>
                    </div>
                  )}

                  {!error.message.includes("API Key") && !error.details && (
                    <div className="mt-3 pt-3 border-t border-red-100 text-xs font-mono text-red-400 select-all">
                      Ref: {new Date().toISOString().split('T')[1].split('.')[0]}-{Math.random().toString(36).substr(2, 5).toUpperCase()}
                    </div>
                  )}
                </div>
                <button 
                  onClick={() => setError(null)}
                  className="text-stone-500 underline hover:text-stone-800"
                >
                  Try Again
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

