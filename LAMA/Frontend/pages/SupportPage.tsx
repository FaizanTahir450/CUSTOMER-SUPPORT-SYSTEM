import React, { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { classifyAndRouteQuery } from './utils/queryRouter';
import { sanitizeOutput } from './security/chatSecurity';

/* Interface for ChatMessage */
interface ChatMessage {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  audioUrl?: string;
  isPlaying?: boolean;
}

/* Voice Recorder Hook */
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

    recorder.start(200); // Emit audio chunks every 200ms
    setIsRecording(true);
  };

  const stopRecording = (): Promise<Blob | null> =>
    new Promise(resolve => {
      const recorder = mediaRecorderRef.current;
      if (!recorder) return resolve(null);

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

/* Components for Messages */
const AIMessage: React.FC<{ text: string }> = ({ text }) => (
  <div className="flex mb-4">
    <div className="bg-gray-100 p-4 rounded-lg max-w-lg shadow-sm">
      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  </div>
);

const UserMessage: React.FC<{ text: string }> = ({ text }) => (
  <div className="flex justify-end mb-4">
    <div className="bg-primary text-white p-4 rounded-lg max-w-lg shadow-sm">
      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  </div>
);

const Toast: React.FC<{ message: string }> = ({ message }) => (
  <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50">
    {message}
  </div>
);

/* Main SupportPage Component */
const ROUTER_BASE_URL = import.meta.env.VITE_ROUTER_URL || '';
const AGENT1_BASE_URL = import.meta.env.VITE_AGENT1_URL || 'http://localhost:8000';

const SupportPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 1, text: 'Hello! How can I help you today?', sender: 'ai' },
  ]);
  const [input, setInput] = useState('');
  const [generating, setGenerating] = useState(false);
  const [toast, setToast] = useState('');
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const { isRecording, startRecording, stopRecording } = useVoiceRecorder();

  /* Show Toast Notification */
  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(''), 3000);
  };

  /* Send Text Message */
  const sendMessage = async () => {
    if (!input.trim() || generating) return;

    const text = input.trim();
    setInput('');
    setMessages(m => [...m, { id: Date.now(), text, sender: 'user' }]);

    setGenerating(true);

    try {
      // 🔄 Classify and route query intelligently
      const response = await classifyAndRouteQuery(text);
      setMessages(m => [
        ...m,
        { id: Date.now() + 1, text: sanitizeOutput(response), sender: 'ai' },
      ]);
    } catch {
      showToast('Unable to process your query.');
      setMessages(m => [
        ...m,
        { id: Date.now() + 1, text: 'Something went wrong. Please try again later.', sender: 'ai' },
      ]);
    } finally {
      setGenerating(false);
    }
  };

  /* Handle Voice Input */
  const handleVoice = async () => {
    if (isRecording) {
      const blob = await stopRecording();
      if (!blob) return showToast('No speech detected.');

      const form = new FormData();
      form.append('audio_file', blob, 'voice.webm');

      try {
        const res = await axios.post(`${AGENT1_BASE_URL}/speech-to-text`, form);
        const text = res.data?.text?.trim();

        if (!text) return showToast('No speech detected.');

        // 🔄 Process transcribed text using query router
        const response = await classifyAndRouteQuery(text);
        setMessages(m => [
          ...m,
          { id: Date.now(), text, sender: 'user' },
          { id: Date.now() + 1, text: sanitizeOutput(response), sender: 'ai' },
        ]);
      } catch {
        showToast('Speech-to-text conversion failed.');
      }
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
            m.sender === 'ai' ? <AIMessage key={m.id} text={m.text} /> : <UserMessage key={m.id} text={m.text} />
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
          {!isRecording && (
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