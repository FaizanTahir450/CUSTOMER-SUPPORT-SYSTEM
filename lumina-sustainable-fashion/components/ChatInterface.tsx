
import React, { useState, useEffect, useRef } from 'react';
import { Message, Config } from '../types';
import { GeminiService } from '../services/geminiService';
import { authToken } from '../services/client';

const QUICK_QUESTIONS = [
  "What's your return policy?",
  "Check my order status",
  "What are your shipping options?",
  "Tell me about your sustainability efforts"
];

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [config, setConfig] = useState<Config>({
    apiUrl: 'http://localhost:8000',
    userId: 'user123',
    useGemini: false
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize welcome message
    setMessages([
      {
        id: 'initial',
        type: 'bot',
        text: "Hi! I'm Sophia your LUMINA support assistant. I can help you with company information, policies, or check your order status. How can I assist you today?",
        timestamp: new Date()
      }
    ]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const addMessage = (type: 'user' | 'bot', text: string, isError = false) => {
    const newMessage: Message = {
      id: Math.random().toString(36).substr(2, 9),
      type,
      text,
      timestamp: new Date(),
      isError
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async (textToSend: string = input) => {
    const message = textToSend.trim();
    if (!message || isLoading) return;

    addMessage('user', message);
    setInput('');
    setIsLoading(true);

    try {
      let botResponse = "";
      if (config.useGemini) {
        // Instantiate GeminiService right before the call to comply with SDK best practices
        const geminiService = new GeminiService();
        botResponse = await geminiService.generateResponse(message);
      } else {
        // Fallback to local backend
        const token = authToken.get();
        if (!token) {
          throw new Error('Not authenticated. Please login first.');
        }

        const response = await fetch(`${config.apiUrl}/chat`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ message })
        });
        if (!response.ok) throw new Error('Backend disconnected');
        const data = await response.json();
        botResponse = data.response;
      }
      addMessage('bot', botResponse);
    } catch (error: any) {
      addMessage('bot', `Error: ${error.message}. Please check settings.`, true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSendMessage();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-slate-50">
      {/* Settings Panel */}
      <div className={`transition-all duration-300 overflow-hidden ${showSettings ? 'max-h-64 border-b' : 'max-h-0'}`}>
        <div className="p-4 bg-indigo-50 border-indigo-100 flex flex-col gap-4 max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
             <h3 className="font-semibold text-indigo-900">Configuration</h3>
             <label className="flex items-center gap-2 text-sm cursor-pointer">
               <input 
                type="checkbox" 
                checked={config.useGemini} 
                onChange={(e) => setConfig({...config, useGemini: e.target.checked})}
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
               />
               Use AI Engine (Gemini)
             </label>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-indigo-700 mb-1">API URL (Fallback)</label>
              <input 
                type="text" 
                value={config.apiUrl} 
                onChange={(e) => setConfig({...config, apiUrl: e.target.value})}
                className="w-full px-3 py-2 text-sm border border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-indigo-700 mb-1">User ID</label>
              <input 
                type="text" 
                value={config.userId} 
                onChange={(e) => setConfig({...config, userId: e.target.value})}
                className="w-full px-3 py-2 text-sm border border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white px-6 py-4 flex items-center justify-between shadow-sm border-b">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-xl shadow-lg shadow-indigo-200">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Customer Support</h1>
            <p className="text-xs text-slate-500">Active • Typically responds in seconds</p>
          </div>
        </div>
        <button 
          onClick={() => setShowSettings(!showSettings)}
          className="px-4 py-2 text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors"
        >
          {showSettings ? 'Close Settings' : 'Settings'}
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="max-w-4xl mx-auto flex flex-col gap-6 py-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-[80%] ${msg.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  msg.type === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-600'
                }`}>
                  {msg.type === 'user' ? 'YOU' : 'AI'}
                </div>
                <div className={`flex flex-col ${msg.type === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                    msg.type === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-none' 
                      : msg.isError 
                      ? 'bg-red-50 text-red-800 border border-red-100' 
                      : 'bg-white text-slate-800 rounded-tl-none'
                  }`}>
                    {msg.text}
                  </div>
                  <span className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3 items-center">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-200 animate-pulse" />
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t p-4 sm:px-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length < 3 && !isLoading && (
            <div className="flex flex-wrap gap-2">
              {QUICK_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSendMessage(q)}
                  className="px-3 py-1.5 text-xs bg-slate-50 hover:bg-indigo-50 hover:text-indigo-600 border border-slate-200 rounded-full transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything about LUMINA..."
              className="flex-1 px-4 py-3 bg-slate-100 border-none rounded-xl focus:ring-2 focus:ring-indigo-600 outline-none text-sm transition-all"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={isLoading || !input.trim()}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold text-sm flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
              </svg>
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
