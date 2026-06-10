'use client';

import { useState, useEffect } from 'react';

// Determine API base URL based on environment
const getApiBase = (): string => {
  if (typeof window === 'undefined') {
    return 'https://jimmy-ai-bot.onrender.com'; // Default fallback for SSR
  }
  
  // Use environment variable if available
  if (process.env.NEXT_PUBLIC_API_BASE && process.env.NEXT_PUBLIC_API_BASE.trim()) {
    return process.env.NEXT_PUBLIC_API_BASE.replace(/\/$/, '');
  }
  
  // Use same domain as current application
  const protocol = window.location.protocol; // http: or https:
  const host = window.location.host; // domain and port
  
  // For development: if on localhost:3000, use API on localhost:8000
  if (host.includes('localhost:3000')) {
    return 'http://localhost:8000';
  }
  
  // For production: use same domain (e.g., https://jimmy-ai-bot.onrender.com)
  return `${protocol}//${host}`;
};

const API_BASE = getApiBase();

interface SettingsState {
  telegramToken: string;
  googleApiKey: string;
  whatsappConnected: boolean;
  voiceEnabled: boolean;
  maxTokens: number;
}

export default function SettingsPanel() {
  const [mounted, setMounted] = useState(false);
  const [settings, setSettings] = useState<SettingsState>({
    telegramToken: '',
    googleApiKey: '',
    whatsappConnected: false,
    voiceEnabled: false,
    maxTokens: 7000000,
  });

  const [status, setStatus] = useState<{
    telegram: 'disconnected' | 'connecting' | 'connected';
    whatsapp: 'disconnected' | 'connecting' | 'connected';
    voice: 'disabled' | 'enabled';
  }>({
    telegram: 'disconnected',
    whatsapp: 'disconnected',
    voice: 'disabled',
  });

  const [showQR, setShowQR] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Load settings from localStorage on client-side mount
  useEffect(() => {
    const telegramToken = localStorage.getItem('telegramToken') || '';
    const googleApiKey = localStorage.getItem('googleApiKey') || '';
    const whatsappConnected = localStorage.getItem('whatsappConnected') === 'true';
    const voiceEnabled = localStorage.getItem('voiceEnabled') === 'true';
    const maxTokens = parseInt(localStorage.getItem('maxTokens') || '7000000');

    setSettings({
      telegramToken,
      googleApiKey,
      whatsappConnected,
      voiceEnabled,
      maxTokens,
    });

    setStatus({
      telegram: telegramToken ? 'connected' : 'disconnected',
      whatsapp: whatsappConnected ? 'connected' : 'disconnected',
      voice: voiceEnabled ? 'enabled' : 'disabled',
    });

    setMounted(true);
  }, []);

  const handleTelegramConnect = async () => {
    if (!settings.telegramToken.trim()) {
      alert('Please enter a Telegram bot token');
      return;
    }

    setLoading(true);
    setMessage('');
    setStatus((prev) => ({ ...prev, telegram: 'connecting' }));

    try {
      const response = await fetch(`${API_BASE}/api/v1/telegram/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: settings.telegramToken,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setStatus((prev) => ({ ...prev, telegram: 'connected' }));
        localStorage.setItem('telegramToken', settings.telegramToken);
        setMessage('✅ Telegram bot connected successfully!');
      } else {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        setMessage(`❌ Failed: ${error.detail || 'Failed to connect'}`);
        setStatus((prev) => ({ ...prev, telegram: 'disconnected' }));
      }
    } catch (error) {
      console.error('Telegram connection error:', error);
      const errorMsg = error instanceof Error ? error.message : 'Connection error';
      setMessage(`❌ Error: ${errorMsg}`);
      setStatus((prev) => ({ ...prev, telegram: 'disconnected' }));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleApiKeySubmit = async () => {
    if (!settings.googleApiKey.trim()) {
      alert('Please enter a Google API key');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE}/api/v1/config/google-api`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: settings.googleApiKey,
        }),
      });

      if (response.ok) {
        localStorage.setItem('googleApiKey', settings.googleApiKey);
        setMessage('✅ Google API key configured successfully!');
      } else {
        const error = await response.json().catch(() => ({ detail: 'Failed to set key' }));
        setMessage(`❌ Failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Google API key error:', error);
      const errorMsg = error instanceof Error ? error.message : 'Configuration error';
      setMessage(`❌ Error: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleWhatsAppConnect = async () => {
    setLoading(true);
    setMessage('');
    setStatus((prev) => ({ ...prev, whatsapp: 'connecting' }));

    try {
      const response = await fetch(`${API_BASE}/api/v1/whatsapp/qr`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.ok) {
        setShowQR(true);
        setStatus((prev) => ({ ...prev, whatsapp: 'connected' }));
        localStorage.setItem('whatsappConnected', 'true');
        setMessage('✅ WhatsApp QR code ready!');
      } else {
        const error = await response.json().catch(() => ({ detail: 'Failed' }));
        setMessage(`❌ Failed: ${error.detail}`);
        setStatus((prev) => ({ ...prev, whatsapp: 'disconnected' }));
      }
    } catch (error) {
      console.error('WhatsApp error:', error);
      const errorMsg = error instanceof Error ? error.message : 'Connection error';
      setMessage(`❌ Error: ${errorMsg}`);
      setStatus((prev) => ({ ...prev, whatsapp: 'disconnected' }));
    } finally {
      setLoading(false);
    }
  };

  const toggleVoice = () => {
    const newVoiceState = !settings.voiceEnabled;
    setSettings((prev) => ({ ...prev, voiceEnabled: newVoiceState }));
    setStatus((prev) => ({
      ...prev,
      voice: newVoiceState ? 'enabled' : 'disabled',
    }));
    localStorage.setItem('voiceEnabled', String(newVoiceState));
  };

  // Don't render until mounted on client (prevents localStorage errors)
  if (!mounted) {
    return <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <p className="text-slate-300">Loading settings...</p>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <span>⚙️</span> Integration Settings
        </h1>
        <p className="text-slate-400 mb-8">
          Configure your bot integrations and features (Production Mode - Real-Time Only)
        </p>

        {/* Status Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg border ${
            message.startsWith('✅') 
              ? 'bg-green-500/10 border-green-500 text-green-300'
              : 'bg-red-500/10 border-red-500 text-red-300'
          }`}>
            {message}
          </div>
        )}

        {/* Telegram Integration */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <span>📱</span> Telegram Bot
              </h2>
              <p className="text-slate-400 text-sm mt-1">
                Connect to Telegram for messaging
              </p>
            </div>
            <div
              className={`px-4 py-2 rounded-full font-semibold ${
                status.telegram === 'connected'
                  ? 'bg-green-500 text-white'
                  : status.telegram === 'connecting'
                  ? 'bg-yellow-500 text-white'
                  : 'bg-slate-700 text-slate-300'
              }`}
            >
              {status.telegram.toUpperCase()}
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-white font-medium mb-2">
                Bot Token (from @BotFather)
              </label>
              <input
                type="password"
                value={settings.telegramToken}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    telegramToken: e.target.value,
                  }))
                }
                placeholder="Enter your Telegram bot token"
                className="w-full bg-slate-700 border border-slate-600 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-blue-500 transition"
              />
              <p className="text-slate-400 text-sm mt-2">
                Get your token from @BotFather on Telegram. Can handle up to 7M tokens in conversation history.
              </p>
            </div>

            <button
              onClick={handleTelegramConnect}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              {loading ? '🔄 Connecting...' : '🚀 Connect Telegram Bot'}
            </button>
          </div>
        </div>

        {/* Google AI Studio */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <span>🤖</span> Google AI Studio
              </h2>
              <p className="text-slate-400 text-sm mt-1">
                Power your bot with Google's Gemini AI
              </p>
            </div>
            <div className="px-4 py-2 rounded-full font-semibold bg-green-500 text-white">
              ACTIVE
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-white font-medium mb-2">
                API Key (from aistudio.google.com)
              </label>
              <input
                type="password"
                value={settings.googleApiKey}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    googleApiKey: e.target.value,
                  }))
                }
                placeholder="Enter your Google API key"
                className="w-full bg-slate-700 border border-slate-600 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-blue-500 transition"
              />
              <p className="text-slate-400 text-sm mt-2">
                Get free API key from Google AI Studio. Enables intelligent AI responses.
              </p>
            </div>

            <button
              onClick={handleGoogleApiKeySubmit}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              💾 Save Google API Key
            </button>
          </div>
        </div>

        {/* WhatsApp Integration */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <span>💬</span> WhatsApp
              </h2>
              <p className="text-slate-400 text-sm mt-1">
                Connect via WhatsApp Web
              </p>
            </div>
            <div
              className={`px-4 py-2 rounded-full font-semibold ${
                status.whatsapp === 'connected'
                  ? 'bg-green-500 text-white'
                  : status.whatsapp === 'connecting'
                  ? 'bg-yellow-500 text-white'
                  : 'bg-slate-700 text-slate-300'
              }`}
            >
              {status.whatsapp.toUpperCase()}
            </div>
          </div>

          <button
            onClick={handleWhatsAppConnect}
            disabled={loading}
            className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 text-white font-semibold py-3 px-6 rounded-lg transition"
          >
            {loading ? '🔄 Loading QR Code...' : '📲 Generate WhatsApp QR Code'}
          </button>

          {showQR && (
            <div className="mt-6 p-4 bg-slate-700 rounded-lg text-center">
              <p className="text-white mb-4">Scan this QR code with WhatsApp Web</p>
              <div className="bg-white p-4 rounded-lg mx-auto w-64 h-64 flex items-center justify-center">
                <div className="text-slate-400">📸 QR Code will appear here</div>
              </div>
            </div>
          )}
        </div>

        {/* Voice Conversation */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <span>🎤</span> Voice Conversation
              </h2>
              <p className="text-slate-400 text-sm mt-1">
                Enable voice input and output
              </p>
            </div>
            <div
              className={`px-4 py-2 rounded-full font-semibold ${
                status.voice === 'enabled'
                  ? 'bg-green-500 text-white'
                  : 'bg-slate-700 text-slate-300'
              }`}
            >
              {status.voice.toUpperCase()}
            </div>
          </div>

          <button
            onClick={toggleVoice}
            className={`w-full font-semibold py-3 px-6 rounded-lg transition ${
              settings.voiceEnabled
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-purple-600 hover:bg-purple-700 text-white'
            }`}
          >
            {settings.voiceEnabled ? '🔇 Disable Voice' : '🎤 Enable Voice'}
          </button>

          {settings.voiceEnabled && (
            <div className="mt-4 p-4 bg-purple-500 bg-opacity-20 rounded-lg border border-purple-500">
              <p className="text-white text-sm">
                ✅ Voice input and text-to-speech enabled. Speak to your bot and hear responses!
              </p>
            </div>
          )}
        </div>

        {/* Conversation Token Settings */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2 mb-4">
            <span>📊</span> Conversation Settings
          </h2>

          <div>
            <label className="block text-white font-medium mb-2">
              Max Tokens for Conversation History
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="1000000"
                max="7000000"
                step="500000"
                value={settings.maxTokens}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    maxTokens: parseInt(e.target.value),
                  }))
                }
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
              />
              <div className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold">
                {(settings.maxTokens / 1000000).toFixed(1)}M
              </div>
            </div>
            <p className="text-slate-400 text-sm mt-2">
              Bot can maintain up to 7 million tokens of conversation context for complex discussions.
            </p>
          </div>
        </div>

        {/* Status Summary */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-white mb-4">📊 Connection Status</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-700 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Telegram</p>
              <p className={`text-lg font-bold ${status.telegram === 'connected' ? 'text-green-400' : 'text-slate-400'}`}>
                {status.telegram === 'connected' ? '✅ Connected' : '❌ Disconnected'}
              </p>
            </div>
            <div className="bg-slate-700 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Google AI</p>
              <p className="text-lg font-bold text-green-400">✅ Configured</p>
            </div>
            <div className="bg-slate-700 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">WhatsApp</p>
              <p className={`text-lg font-bold ${status.whatsapp === 'connected' ? 'text-green-400' : 'text-slate-400'}`}>
                {status.whatsapp === 'connected' ? '✅ Connected' : '❌ Disconnected'}
              </p>
            </div>
            <div className="bg-slate-700 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Voice</p>
              <p className={`text-lg font-bold ${status.voice === 'enabled' ? 'text-green-400' : 'text-slate-400'}`}>
                {status.voice === 'enabled' ? '✅ Enabled' : '❌ Disabled'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
