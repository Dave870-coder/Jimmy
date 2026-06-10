'use client';

import { useState, useRef } from 'react';

interface VoiceConversationProps {
  enabled: boolean;
  onMessage: (message: string) => void;
}

export default function VoiceConversation({ enabled, onMessage }: VoiceConversationProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<any>(null);

  const startListening = () => {
    if (!enabled) {
      alert('Voice conversation is not enabled. Enable it in Settings.');
      return;
    }

    // Check browser support
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition not supported in your browser');
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('');
    };

    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setTranscript(transcript);
          onMessage(transcript);
        } else {
          interimTranscript += transcript;
        }
      }
      if (interimTranscript) {
        setTranscript(interimTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  if (!enabled) {
    return null;
  }

  return (
    <div className="flex gap-2 items-center">
      <button
        onClick={isListening ? stopListening : startListening}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
          isListening
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-purple-600 hover:bg-purple-700 text-white'
        }`}
      >
        {isListening ? '🔴 Stop Listening' : '🎤 Voice'}
      </button>
      {transcript && (
        <span className="text-sm text-slate-400 bg-slate-700 px-3 py-2 rounded-lg max-w-xs truncate">
          {transcript}
        </span>
      )}
    </div>
  );
}
