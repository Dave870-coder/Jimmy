'use client';

import { useEffect, useState } from 'react';

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '');
const apiUrl = (path: string) => `${API_BASE}${path}`;

type Message = {
  id: string;
  user_id: string;
  content: string;
  sender: 'user' | 'bot';
  created_at: string;
  channel: 'telegram' | 'whatsapp' | 'web';
};

export default function Messages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [channelFilter, setChannelFilter] = useState('all');
  const [senderFilter, setSenderFilter] = useState('all');
  const [page, setPage] = useState(1);
  const limit = 30;

  useEffect(() => {
    async function loadMessages() {
      try {
        const offset = (page - 1) * limit;
        const response = await fetch(apiUrl(`/api/v1/admin/messages?limit=${limit}&offset=${offset}`));
        if (response.ok) {
          const data = await response.json();
          setMessages(data);
        }
      } catch (error) {
        console.error('Failed to load messages:', error);
      } finally {
        setLoading(false);
      }
    }

    loadMessages();
  }, [page]);

  const filteredMessages = messages.filter((msg) => {
    const matchesSearch = msg.content.toLowerCase().includes(search.toLowerCase());
    const matchesChannel = channelFilter === 'all' || msg.channel === channelFilter;
    const matchesSender = senderFilter === 'all' || msg.sender === senderFilter;
    return matchesSearch && matchesChannel && matchesSender;
  });

  const exportMessages = () => {
    const csv = [
      'ID,User ID,Sender,Channel,Created At,Content',
      ...messages.map((m) =>
        `${m.id},"${m.user_id}",${m.sender},${m.channel},${m.created_at},"${m.content.replace(/"/g, '""')}"`
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `messages-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading messages...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <h1 className="text-2xl font-bold text-slate-100">Message History</h1>
        <p className="text-slate-400">View and search all bot messages</p>
      </div>

      {/* Filters */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl space-y-4">
        <div className="flex gap-3 flex-col md:flex-row">
          <input
            type="text"
            placeholder="Search messages..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 rounded-lg bg-white/10 px-4 py-2 text-slate-100 placeholder-slate-500 border border-white/20 focus:border-cyan-500 focus:outline-none"
          />
          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="rounded-lg bg-white/10 px-4 py-2 text-slate-100 border border-white/20 focus:border-cyan-500 focus:outline-none"
          >
            <option value="all">All Channels</option>
            <option value="telegram">Telegram</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="web">Web</option>
          </select>
          <select
            value={senderFilter}
            onChange={(e) => setSenderFilter(e.target.value)}
            className="rounded-lg bg-white/10 px-4 py-2 text-slate-100 border border-white/20 focus:border-cyan-500 focus:outline-none"
          >
            <option value="all">All Senders</option>
            <option value="user">Users</option>
            <option value="bot">Bot</option>
          </select>
          <button
            onClick={exportMessages}
            className="px-6 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 transition-all border border-emerald-500/50"
          >
            Export
          </button>
        </div>
        <p className="text-sm text-slate-400">{filteredMessages.length} messages found</p>
      </div>

      {/* Messages List */}
      <div className="space-y-3">
        {filteredMessages.map((msg) => (
          <div
            key={msg.id}
            className={`rounded-xl p-4 border border-white/10 backdrop-blur-xl ${
              msg.sender === 'bot'
                ? 'bg-gradient-to-r from-cyan-500/10 to-blue-600/10'
                : 'bg-gradient-to-r from-emerald-500/10 to-green-600/10'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className={`text-xs font-semibold px-2 py-1 rounded ${
                  msg.sender === 'bot'
                    ? 'bg-cyan-500/30 text-cyan-300'
                    : 'bg-emerald-500/30 text-emerald-300'
                }`}>
                  {msg.sender === 'bot' ? '🤖 Bot' : '👤 User'}
                </span>
                <span className="text-xs text-slate-400 px-2 py-1 bg-white/5 rounded">
                  {msg.channel.toUpperCase()}
                </span>
              </div>
              <span className="text-xs text-slate-500">{new Date(msg.created_at).toLocaleString()}</span>
            </div>
            <p className="text-slate-100 text-sm break-words">{msg.content}</p>
            <p className="text-xs text-slate-500 mt-2">User: {msg.user_id}</p>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl flex justify-between items-center">
        <button
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
          className="px-4 py-2 rounded-lg bg-white/10 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20"
        >
          Previous
        </button>
        <p className="text-slate-400">
          Page <span className="text-slate-100">{page}</span>
        </p>
        <button
          onClick={() => setPage(page + 1)}
          disabled={filteredMessages.length < limit}
          className="px-4 py-2 rounded-lg bg-white/10 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20"
        >
          Next
        </button>
      </div>
    </div>
  );
}
