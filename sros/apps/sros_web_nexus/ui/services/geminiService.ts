import { GoogleGenAI, Type, SchemaType, Modality } from "@google/genai";
import { ModuleConfig, AgentMessage, AgentConfig } from '../types';

// Ensure API key is present
const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

// --- Types for Service ---
interface SimulationResult {
  logs: string[];
  data: { v1: number; v2: number }[];
}

// --- Helper: Decode Audio ---
async function decodeAudioData(
    data: Uint8Array,
    ctx: AudioContext,
    sampleRate: number,
    numChannels: number,
  ): Promise<AudioBuffer> {
    const dataInt16 = new Int16Array(data.buffer);
    const frameCount = dataInt16.length / numChannels;
    const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);
  
    for (let channel = 0; channel < numChannels; channel++) {
      const channelData = buffer.getChannelData(channel);
      for (let i = 0; i < frameCount; i++) {
        channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
      }
    }
    return buffer;
}

function base64ToUint8Array(base64: string): Uint8Array {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
}


// --- 1. Simulation Kernel (Legacy Support) ---
export const runKernelPrompt = async (
  promptContext: string,
  config: ModuleConfig
): Promise<SimulationResult | null> => {
  if (!apiKey) return null;
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: promptContext,
      config: {
        temperature: config.temperature,
        topK: config.topK,
        topP: config.topP,
        responseMimeType: "application/json",
        // Schema removed to prevent 500 errors on creative simulation tasks.
        // We rely on the prompt to enforce structure.
      }
    });
    let text = response.text || "{}";
    text = text.replace(/```json\n?|```/g, '').trim();
    return JSON.parse(text) as SimulationResult;
  } catch (error) {
    console.error("Kernel Fault:", error);
    return null;
  }
};

// --- 2. Prime Agent: Chat & Reasoning ---
export const runAgentChat = async (
  history: AgentMessage[],
  newMessage: string,
  options: {
    thinking: boolean;
    grounding: { search: boolean; maps: boolean };
    imageAttachment?: { data: string; mimeType: string };
    config?: AgentConfig;
  }
) => {
    if (!apiKey) throw new Error("API Key Missing");

    const model = options.thinking ? 'gemini-3-pro-preview' : 'gemini-2.5-flash';
    
    // Construct Tools
    const tools = [];
    if (options.grounding.search) tools.push({ googleSearch: {} });
    if (options.grounding.maps) tools.push({ googleMaps: {} });

    // Config
    const config: any = {
        tools: tools.length > 0 ? tools : undefined,
        systemInstruction: options.config?.systemInstruction,
        temperature: options.config?.temperature,
        topK: options.config?.topK,
        topP: options.config?.topP
    };

    if (options.thinking) {
        // Max budget for 3-pro
        config.thinkingConfig = { thinkingBudget: 32768 }; 
    }

    // Build Content
    const parts: any[] = [{ text: newMessage }];
    if (options.imageAttachment) {
        parts.unshift({
            inlineData: {
                data: options.imageAttachment.data.split(',')[1],
                mimeType: options.imageAttachment.mimeType
            }
        });
    }

    try {
        const response = await ai.models.generateContent({
            model,
            contents: { parts },
            config
        });

        // Extract Grounding
        const groundingChunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
        const sources = groundingChunks?.map((chunk: any) => {
            if (chunk.web) return { title: chunk.web.title, uri: chunk.web.uri };
            if (chunk.maps?.placeAnswerSources?.length) return { title: 'Maps Place', uri: chunk.maps.placeAnswerSources[0].reviewSnippets?.[0]?.uri || ''};
            return null;
        }).filter(Boolean) || [];

        return {
            text: response.text || "",
            sources
        };
    } catch (e) {
        console.error("Agent Chat Error", e);
        throw e;
    }
};

// --- 3. Holo Forge: Image Generation & Editing ---
export const generateHoloImage = async (prompt: string, size: '1K' | '2K' | '4K' = '1K', aspectRatio: '1:1' | '3:4' | '4:3' | '9:16' | '16:9' = '16:9') => {
    if (!apiKey) return null;
    try {
        const response = await ai.models.generateContent({
            model: 'gemini-3-pro-image-preview',
            contents: { parts: [{ text: prompt }] },
            config: {
                imageConfig: {
                    imageSize: size,
                    aspectRatio: aspectRatio 
                }
            }
        });
        
        for (const part of response.candidates?.[0]?.content?.parts || []) {
             if (part.inlineData) {
                 return `data:image/png;base64,${part.inlineData.data}`;
             }
        }
        return null;
    } catch (e) {
        console.warn("Gemini 3 Pro Image Gen failed. Falling back to Gemini 2.5 Flash Image.", e);
        try {
            // Fallback to gemini-2.5-flash-image
            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash-image',
                contents: { parts: [{ text: prompt }] },
                config: {
                    imageConfig: {
                        // Flash Image doesn't support imageSize, so we omit it
                        aspectRatio: aspectRatio
                    }
                }
            });
            for (const part of response.candidates?.[0]?.content?.parts || []) {
                if (part.inlineData) {
                    return `data:image/png;base64,${part.inlineData.data}`;
                }
           }
           return null;
        } catch (fallbackError) {
             console.error("Holo Gen Fallback Error", fallbackError);
             throw fallbackError;
        }
    }
};

export const editHoloImage = async (base64Image: string, prompt: string) => {
    if (!apiKey) return null;
    try {
        const mimeType = base64Image.split(';')[0].split(':')[1];
        const data = base64Image.split(',')[1];
        
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash-image',
            contents: {
                parts: [
                    { inlineData: { mimeType, data } },
                    { text: prompt }
                ]
            }
        });

        for (const part of response.candidates?.[0]?.content?.parts || []) {
            if (part.inlineData) {
                return `data:image/png;base64,${part.inlineData.data}`;
            }
       }
       return null;
    } catch (e) {
        console.error("Holo Edit Error", e);
        throw e;
    }
};

// --- 4. Veo Core: Video Generation ---
export const generateVeoVideo = async (prompt: string, aspectRatio: '16:9' | '9:16' = '16:9', imageBase64?: string) => {
    if (!apiKey) return null;
    try {
        const request: any = {
            model: 'veo-3.1-fast-generate-preview',
            prompt: prompt,
            config: {
                numberOfVideos: 1,
                resolution: '720p',
                aspectRatio: aspectRatio
            }
        };

        if (imageBase64) {
             const parts = imageBase64.split(',');
             if (parts.length === 2) {
                const mimeType = parts[0].split(':')[1].split(';')[0];
                const data = parts[1];
                request.image = {
                    imageBytes: data,
                    mimeType: mimeType
                };
             }
        }

        // Check for key if needed, assuming env key is valid
        let operation = await ai.models.generateVideos(request);

        // Poll
        while (!operation.done) {
            await new Promise(resolve => setTimeout(resolve, 5000));
            operation = await ai.operations.getVideosOperation({ operation });
        }

        const videoUri = operation.response?.generatedVideos?.[0]?.video?.uri;
        if (videoUri) {
            // Fetch the actual bytes
            const res = await fetch(`${videoUri}&key=${apiKey}`);
            const blob = await res.blob();
            return URL.createObjectURL(blob);
        }
        return null;
    } catch (e) {
        console.error("Veo Error", e);
        throw e;
    }
};

// --- 5. Speech Synthesis (TTS) ---
export const generateSpeech = async (text: string) => {
    if (!apiKey) return null;
    try {
        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash-preview-tts",
            contents: [{ parts: [{ text }] }],
            config: {
                responseModalities: [Modality.AUDIO],
                speechConfig: {
                    voiceConfig: {
                        prebuiltVoiceConfig: { voiceName: 'Kore' },
                    },
                },
            },
        });
        const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
        return base64Audio;
    } catch (e) {
        console.error("TTS Error", e);
        return null;
    }
};

export const playAudio = async (base64Audio: string) => {
    try {
        const outputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
        const raw = base64ToUint8Array(base64Audio);
        const buffer = await decodeAudioData(raw, outputAudioContext, 24000, 1);
        const source = outputAudioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(outputAudioContext.destination);
        source.start();
    } catch(e) {
        console.error("Playback failed", e);
    }
}

// --- 6. Live API: Sovereign Voice ---
// returns a cleanup function
export const connectLiveSession = async (
    onAudioData: (buffer: AudioBuffer) => void,
    onTranscription: (text: string, isUser: boolean) => void,
    onError: (err: any) => void
) => {
    const inputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
    const outputAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
    
    // Get Mic
    let stream: MediaStream;
    try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
        console.error("Microphone permission denied or not available", e);
        onError(new Error("Microphone access denied. Please allow permissions."));
        return () => {};
    }
    
    const sessionPromise = ai.live.connect({
        model: 'gemini-2.5-flash-native-audio-preview-09-2025',
        config: {
            responseModalities: [ "AUDIO" ],
            speechConfig: {
                voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } }
            },
            systemInstruction: "",

            inputAudioTranscription: {},
            outputAudioTranscription: {}
        },
        callbacks: {
            onopen: () => {
                console.log("SROS LIVE LINK ESTABLISHED");
                // Setup Input Stream
                const source = inputAudioContext.createMediaStreamSource(stream);
                const scriptProcessor = inputAudioContext.createScriptProcessor(4096, 1, 1);
                
                scriptProcessor.onaudioprocess = (e) => {
                    const inputData = e.inputBuffer.getChannelData(0);
                    // PCM16 conversion
                    const l = inputData.length;
                    const int16 = new Int16Array(l);
                    for (let i = 0; i < l; i++) {
                         int16[i] = inputData[i] * 32768;
                    }
                    const base64 = btoa(String.fromCharCode(...new Uint8Array(int16.buffer)));
                    
                    sessionPromise.then(session => {
                        session.sendRealtimeInput({
                            media: {
                                mimeType: 'audio/pcm;rate=16000',
                                data: base64
                            }
                        });
                    });
                };
                
                source.connect(scriptProcessor);
                scriptProcessor.connect(inputAudioContext.destination);
            },
            onmessage: async (msg) => {
                // Transcription
                if (msg.serverContent?.inputTranscription) {
                    onTranscription(msg.serverContent.inputTranscription.text, true);
                }
                if (msg.serverContent?.outputTranscription) {
                    onTranscription(msg.serverContent.outputTranscription.text, false);
                }

                // Audio Output
                const audioData = msg.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
                if (audioData) {
                    const raw = base64ToUint8Array(audioData);
                    const buffer = await decodeAudioData(raw, outputAudioContext, 24000, 1);
                    onAudioData(buffer);
                }
            },
            onerror: onError,
            onclose: () => console.log("SROS LIVE LINK TERMINATED")
        }
    });

    return () => {
        sessionPromise.then(s => s.close());
        inputAudioContext.close();
        outputAudioContext.close();
        stream.getTracks().forEach(t => t.stop());
    };
};

// --- Re-exports for legacy components if needed ---
export const runImageEditPrompt = async (base64Image: string, mimeType: string, prompt: string) => {
    return editHoloImage(base64Image, prompt).then(img => ({ imageBase64: img ? img.split(',')[1] : null, text: img ? 'Edit Complete' : 'Failed' }));
};
export const runImageGenPrompt = async (prompt: string) => {
    return generateHoloImage(prompt).then(img => ({ imageBase64: img ? img.split(',')[1] : null, text: img ? 'Gen Complete' : 'Failed' }));
};