'use client';

import { useState } from 'react';

interface SettingsState {
  telegramToken: string;
  googleApiKey: string;
  whatsappConnected: boolean;
  voiceEnabled: boolean;
  maxTokens: number;
}

export default function SettingsPanel() {
  const [settings, setSettings] = useState<SettingsState>({
    telegramToken: '',
    googleApiKey: '',
    whatsappConnected: false,
    voiceEnabled: false,
    maxTokens: 7000000, // 7 million tokens
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

  const handleTelegramConnect = async () => {
    if (!settings.telegramToken.trim()) {
      alert('Please enter a Telegram bot token');
      return;
    }

    setLoading(true);
    setStatus((prev) => ({ ...prev, telegram: 'connecting' }));

    try {
      const response = await fetch('/api/v1/telegram/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: settings.telegramToken,
        }),
      });

      if (response.ok) {
        setStatus((prev) => ({ ...prev, telegram: 'connected' }));
        localStorage.setItem('telegramToken', settings.telegramToken);
      } else {
        alert('Failed to connect Telegram bot');
        setStatus((prev) => ({ ...prev, telegram: 'disconnected' }));
      }
    } catch (error) {
      console.error('Telegram connection error:', error);
      alert('Error connecting to Telegram');
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

    try {
      const response = await fetch('/api/v1/config/google-api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: settings.googleApiKey,
        }),
      });

      if (response.ok) {
        alert('Google API key configured successfully!');
        localStorage.setItem('googleApiKey', settings.googleApiKey);
      } else {
        alert('Failed to set Google API key');
      }
    } catch (error) {
      console.error('Google API key error:', error);
      alert('Error configuring Google API key');
    }
  };

  const handleWhatsAppConnect = async () => {
    setLoading(true);
    setStatus((prev) => ({ ...prev, whatsapp: 'connecting' }));

    try {
      const response = await fetch('/api/v1/whatsapp/qr');
      if (response.ok) {
        setShowQR(true);
        setStatus((prev) => ({ ...prev, whatsapp: 'connected' }));
      } else {
        alert('Failed to generate WhatsApp QR code');
        setStatus((prev) => ({ ...prev, whatsapp: 'disconnected' }));
      }
    } catch (error) {
      console.error('WhatsApp error:', error);
      alert('Error generating WhatsApp QR');
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <span>⚙️</span> Integration Settings
        </h1>
        <p className="text-slate-400 mb-8">
          Configure your bot integrations and features
        </p>

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
