// import React, { useState, useRef } from 'react';
// import { ChatMessage } from '../types';
// import { sendSecureChatMessage } from './security/chatSecurity';

// const AIMessage: React.FC<{ text: string }> = ({ text }) => (
//   <div className="flex justify-start">
//     <div className="bg-gray-200 text-gray-800 p-3 rounded-lg max-w-lg animate-fade-in-up">
//       {text}
//     </div>
//   </div>
// );

// const UserMessage: React.FC<{ text: string }> = ({ text }) => (
//   <div className="flex justify-end">
//     <div className="bg-primary text-white p-3 rounded-lg max-w-lg animate-fade-in-up">
//       {text}
//     </div>
//   </div>
// );

// const LoadingIndicator: React.FC = () => (
//   <div className="flex justify-start">
//     <div className="bg-gray-200 text-gray-500 p-3 rounded-lg max-w-lg animate-fade-in-up">
//       <div className="flex items-center space-x-2">
//         <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
//         <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-200" />
//         <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-400" />
//       </div>
//     </div>
//   </div>
// );

// const SupportPage: React.FC = () => {
//   const [messages, setMessages] = useState<ChatMessage[]>([
//     { id: 1, text: "Hello! I'm the Lama Support Assistant. How can I help you today?", sender: 'ai' },
//   ]);
//   const [input, setInput] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const chatEndRef = useRef<HTMLDivElement>(null);

//   const addMessage = (text: string, sender: 'user' | 'ai') => {
//     setMessages(prev => [...prev, { id: Date.now(), text, sender }]);
//   };

//   const handleSendMessage = (e: React.FormEvent) => {
//     e.preventDefault();
//     if (!input.trim() || isLoading) return;

//     addMessage(input, 'user');
//     sendSecureChatMessage(input, addMessage, setIsLoading);
//     setInput('');
//   };

//   return (
//     <div className="flex h-[calc(100vh-80px)] bg-gray-50">
//       <div className="hidden md:flex flex-col w-1/4 bg-white border-r p-8">
//         <div className="flex items-center space-x-3 mb-8">
//           <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold">L</div>
//           <h1 className="text-2xl font-bold">Lama Support</h1>
//         </div>
//         <p className="text-gray-600">
//           Our AI assistant helps with orders, returns, and product questions.
//         </p>
//       </div>

//       <div className="flex flex-col flex-1">
//         <div className="flex-1 p-6 space-y-6 overflow-y-auto">
//           {messages.map(msg =>
//             msg.sender === 'ai'
//               ? <AIMessage key={msg.id} text={msg.text} />
//               : <UserMessage key={msg.id} text={msg.text} />
//           )}
//           {isLoading && <LoadingIndicator />}
//           <div ref={chatEndRef} />
//         </div>

//         <div className="border-t bg-white p-4">
//           <form onSubmit={handleSendMessage} className="flex space-x-4">
//             <input
//               type="text"
//               value={input}
//               onChange={(e) => setInput(e.target.value)}
//               placeholder="Type your message..."
//               disabled={isLoading}
//               className="flex-1 px-4 py-3 border rounded-full focus:ring-2 focus:ring-primary"
//             />
//             <button
//               type="submit"
//               disabled={isLoading || !input.trim()}
//               className="p-3 bg-primary text-white rounded-full disabled:bg-gray-300"
//             >
//               ➤
//             </button>
//           </form>
//         </div>
//       </div>
//     </div>
//   );
// };
import React, { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
// 🔐 FULL SECURITY INTEGRATION
import { sendSecureChatMessage, sanitizeOutput } from './security/chatSecurity';

interface ChatMessage {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  audioUrl?: string;
  isPlaying?: boolean;
}

const API_BASE_URL = 'http://localhost:8000';

/* =======================
   Toast
======================= */
const Toast: React.FC<{ message: string }> = ({ message }) => (
  <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50">
    {message}
  </div>
);

/* =======================
   Voice Recorder (ROBUST)
======================= */
const useVoiceRecorder = (onStart?: () => void) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    if (isRecording) return;
    onStart?.();

    chunksRef.current = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;

    const recorder = new MediaRecorder(stream);
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = e => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.start(200); // force chunk emission
    setIsRecording(true);
  };

  const stopRecording = (): Promise<Blob | null> =>
    new Promise(resolve => {
      if (!mediaRecorderRef.current) return resolve(null);

      const recorder = mediaRecorderRef.current;

      recorder.onstop = () => {
        streamRef.current?.getTracks().forEach(t => t.stop());
        setIsRecording(false);

        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        resolve(blob.size > 1500 ? blob : null);
      };

      recorder.stop();
    });

  return { isRecording, startRecording, stopRecording };
};

/* =======================
   Message Components
======================= */
const AIMessage: React.FC<{
  text: string;
  audioUrl?: string;
  isPlaying?: boolean;
  isLoading: boolean;
  onPlay: (t: string, a?: string) => void;
  onStop: () => void;
}> = ({ text, audioUrl, isPlaying, onPlay, onStop, isLoading }) => (
  <div className="flex mb-4">
    <div className="bg-gray-100 p-4 rounded-lg max-w-lg shadow-sm">
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown>{text}</ReactMarkdown>
      </div>

      <button
        disabled={isLoading}
        className="mt-3 text-sm px-4 py-1.5 rounded-full bg-blue-100 hover:bg-blue-200 disabled:opacity-50"
        onClick={() => (isPlaying ? onStop() : onPlay(text, audioUrl))}
      >
        {isLoading ? 'Loading audio…' : isPlaying ? '⏹ Stop' : '🔊 Listen'}
      </button>
    </div>
  </div>
);

const UserMessage: React.FC<{ text: string }> = ({ text }) => (
  <div className="flex justify-end mb-4">
    <div className="bg-primary text-white p-4 rounded-lg max-w-lg shadow-sm">
      <div className="prose prose-invert prose-sm max-w-none">
        <ReactMarkdown>{text}</ReactMarkdown>
      </div>
    </div>
  </div>
);

/* =======================
   Main Component
======================= */
const SupportPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 1, text: 'Hello! How can I help you today?', sender: 'ai' },
  ]);

  const [input, setInput] = useState('');
  const [toast, setToast] = useState('');
  const [generating, setGenerating] = useState(false);
  const [ttsLoading, setTtsLoading] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const ttsCache = useRef<Map<string, string>>(new Map());

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setMessages(m => m.map(x => ({ ...x, isPlaying: false })));
  };

  const { isRecording, startRecording, stopRecording } = useVoiceRecorder(stopAudio);

  const showToast = (m: string) => {
    setToast(m);
    setTimeout(() => setToast(''), 3000);
  };

  /* =======================
     TTS
  ======================= */
  const playAudio = async (text: string, audioUrl?: string) => {
    stopAudio();
    setTtsLoading(true);

    let src: string;

    if (audioUrl) {
      src = `data:audio/mp3;base64,${audioUrl}`;
    } else if (ttsCache.current.has(text)) {
      src = ttsCache.current.get(text)!;
    } else {
      const res = await axios.post(`${API_BASE_URL}/text-to-speech`, { text });
      src = `data:audio/mp3;base64,${res.data.audio}`;
      ttsCache.current.set(text, src);
    }

    const audio = new Audio(src);
    audioRef.current = audio;

    setMessages(m => m.map(x => (x.text === text ? { ...x, isPlaying: true } : x)));

    audio.onended = stopAudio;
    audio.oncanplay = () => setTtsLoading(false);
    audio.play();
  };

  /* =======================
     SEND TEXT MESSAGE (SECURE)
  ======================= */
  const sendMessage = () => {
    if (!input.trim() || generating) return;

    const text = input.trim();
    setInput('');
    stopAudio();

    setMessages(m => [...m, { id: Date.now(), text, sender: 'user' }]);

    sendSecureChatMessage(
      text,
      (aiText, sender) => {
        if (sender === 'ai') {
          setMessages(m => [
            ...m,
            { id: Date.now() + 1, text: sanitizeOutput(aiText), sender: 'ai' },
          ]);
        }
      },
      setGenerating
    );
  };

  /* =======================
     VOICE → TEXT (SECURE)
  ======================= */
  const handleVoice = async () => {
    if (isRecording) {
      const blob = await stopRecording();
      if (!blob) return showToast('No speech detected.');

      const form = new FormData();
      form.append('audio_file', blob, 'voice.webm');

      const res = await axios.post(`${API_BASE_URL}/speech-to-text`, form);
      const text = res.data?.text?.trim();

      if (!text) return showToast('No speech detected.');

      // 🔐 text goes through same secure send path
      setInput(text);
    } else {
      startRecording();
    }
  };

  return (
   <div className="flex h-[calc(100vh-80px)] bg-gray-50">
    {toast && <Toast message={toast} />}
       <div className="hidden md:flex flex-col w-1/4 bg-white border-r p-8">
         <div className="flex items-center space-x-3 mb-8">
           <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold">L</div>
           <h1 className="text-2xl font-bold">Lama Support</h1>
         </div>
         <p className="text-gray-600">
           Our AI assistant helps with orders, returns, and product questions.
         </p>
       </div>
      

      <div className="flex flex-col flex-1">
        <div className="flex-1 overflow-y-auto p-4">
          {messages.map(m =>
            m.sender === 'ai' ? (
              <AIMessage
                key={m.id}
                text={m.text}
                audioUrl={m.audioUrl}
                isPlaying={m.isPlaying}
                isLoading={ttsLoading}
                onPlay={playAudio}
                onStop={stopAudio}
              />
            ) : (
              <UserMessage key={m.id} text={m.text} />
            )
          )}

          {generating && <p className="text-sm text-gray-500">Generating response…</p>}
        </div>

        <div className="border-t p-4 flex gap-2">
          <button
            onClick={handleVoice}
            className={`px-4 py-2 rounded ${isRecording ? 'bg-red-400' : 'bg-gray-200'}`}
          >
            {isRecording ? 'Stop 🎤' : '🎤'}
          </button>

          {isRecording ? (
            <div className="flex-1 flex items-center justify-center border rounded bg-red-50">
              <span className="animate-pulse text-red-600 font-medium">Recording… ● ● ●</span>
            </div>
          ) : (
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              className="flex-1 border rounded px-3"
              placeholder="Type your message…"
            />
          )}

          <button onClick={sendMessage} className="px-4 py-2 bg-primary text-white rounded">
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default SupportPage;