'use client';

import { useState, useRef, useEffect } from 'react';

// Production: https://jimmy-ai-bot.onrender.com, Dev: http://localhost:8000
const API_BASE = typeof window !== 'undefined' 
  ? (process.env.NEXT_PUBLIC_API_BASE || (window.location.hostname.includes('github.io') ? 'https://jimmy-ai-bot.onrender.com' : 'http://localhost:8000'))
  : 'https://jimmy-ai-bot.onrender.com';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: 'Hello! I\'m Jimmy, your AI Bot. How can I help you today?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check backend status on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_BASE}/health`, { 
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        });
        setBackendStatus(response.ok ? 'online' : 'offline');
      } catch (err) {
        setBackendStatus('offline');
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError('');
    setLoading(true);

    try {
      if (backendStatus === 'offline') {
        throw new Error('Backend is offline. Please wait for deployment to complete.');
      }

      // Send to backend real-time API - PRODUCTION ONLY
      const response = await fetch(`${API_BASE}/api/v1/messages/send?user_id=web-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: input,
        }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Backend API endpoint not found. Backend may still be deploying.');
        } else if (response.status === 503) {
          throw new Error('Backend is temporarily unavailable. Please try again in a moment.');
        } else {
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
      }

      const data = await response.json();
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || data.message || 'I received your message but couldn\'t generate a response. Please configure a Google AI API key in Settings.',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);
      setBackendStatus('online');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      setBackendStatus('offline');
      
      // Show error message in chat
      const errorBotMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ Error: ${errorMessage}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorBotMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur border-b border-slate-700">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <span className="text-4xl">🤖</span>
            <span>Jimmy AI Bot</span>
          </h1>
          <p className="text-slate-400 mt-1">Chat with your intelligent assistant</p>
        </div>
      </header>

      {/* Main Chat Container */}
      <div className="max-w-4xl mx-auto h-[calc(100vh-200px)] flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-slate-700 text-slate-100 rounded-bl-none'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs mt-1 opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 text-slate-100 px-4 py-3 rounded-lg rounded-bl-none">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="flex justify-center">
              <div className="bg-red-900/30 border border-red-700 text-red-200 px-4 py-2 rounded-lg text-sm">
                ⚠️ {error}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-700 bg-slate-900/95 backdrop-blur p-4">
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
              className="flex-1 bg-slate-800 border border-slate-600 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
            >
              {loading ? '⏳ Sending...' : '📤 Send'}
            </button>
          </form>
          <p className="text-xs text-slate-400 mt-2 text-center">
            💡 Tip: Type anything and Jimmy will respond intelligently
          </p>
        </div>
      </div>

      {/* Footer Info */}
      <footer className="bg-slate-900 border-t border-slate-700 px-4 py-3 text-center text-xs text-slate-400">
        <p>
          Backend: <span className={`font-semibold ${backendStatus === 'online' ? 'text-green-400' : backendStatus === 'offline' ? 'text-red-400' : 'text-yellow-400'}`}>
            {backendStatus === 'checking' ? '⏳ Checking' : backendStatus === 'online' ? '✅ Online' : '❌ Offline'}
          </span> • 
          API: <span className="text-slate-300">{API_BASE}</span> •
          Mode: <span className="text-blue-400 font-semibold">Live Only</span>
        </p>
      </footer>
    </div>
  );
}
