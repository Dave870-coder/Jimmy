"use client";

import { useEffect, useMemo, useState } from 'react';

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '');
const apiUrl = (path: string) => `${API_BASE}${path}`;

type Analytics = {
  active_users: number;
  total_users: number;
  total_messages: number;
  total_workflows: number;
  average_response_time: number;
  generated_at: string;
};

type UserRow = {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string | null;
};

export default function Home() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [whatsappState, setWhatsappState] = useState<{
    connectionId?: string;
    qrCode?: string;
    status?: string;
    phoneNumber?: string;
    message?: string;
    expiresAt?: string;
  }>({});
  const [telegramInfo, setTelegramInfo] = useState<{ telegram_webhook_url?: string; telegram_configured?: boolean }>({});
  const [settingsForm, setSettingsForm] = useState({
    telegram_bot_token: '',
    google_api_key: '',
    openai_api_key: '',
    whatsapp_access_token: '',
    telegram_webhook_secret: '',
    public_base_url: '',
    database_url: '',
  });
  const [settingsStatus, setSettingsStatus] = useState('');
  const [savingSettings, setSavingSettings] = useState(false);

  useEffect(() => {
    let interval: number | undefined;

    async function loadDashboard() {
      try {
        const [analyticsRes, usersRes, integrationsRes] = await Promise.all([
          fetch(apiUrl('/api/v1/admin/analytics')),
          fetch(apiUrl('/api/v1/admin/users?limit=6')),
          fetch(apiUrl('/api/v1/admin/integrations')),
        ]);

        const analyticsData = analyticsRes.ok ? await analyticsRes.json() : null;
        const usersData = usersRes.ok ? await usersRes.json() : [];
        const integrationsData = integrationsRes.ok ? await integrationsRes.json() : {};

        setAnalytics(analyticsData);
        setUsers(usersData);
        setTelegramInfo(integrationsData);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch (error) {
        console.error('Dashboard load failed:', error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
    interval = window.setInterval(loadDashboard, 10000);

    return () => {
      if (interval) {
        window.clearInterval(interval);
      }
    };
  }, []);

  useEffect(() => {
    let statusInterval: number | undefined;

    async function pollWhatsappStatus() {
      if (!whatsappState.connectionId) return;
      try {
        const statusRes = await fetch(apiUrl(`/api/v1/whatsapp-qr/status/${whatsappState.connectionId}`));
        if (!statusRes.ok) return;
        const statusData = await statusRes.json();
        const connectionStatus = statusData.connection_status;
        setWhatsappState((prev) => ({
          ...prev,
          status: connectionStatus?.status,
          phoneNumber: connectionStatus?.phone_number,
          message: connectionStatus?.error_message || prev.message,
        }));
      } catch (error) {
        console.error('WhatsApp status poll failed:', error);
      }
    }

    if (whatsappState.connectionId) {
      statusInterval = window.setInterval(pollWhatsappStatus, 2000);
      pollWhatsappStatus();
    }

    return () => {
      if (statusInterval) {
        window.clearInterval(statusInterval);
      }
    };
  }, [whatsappState.connectionId]);

  const startWhatsappConnection = async () => {
    setWhatsappState({ status: 'starting', message: 'Generating QR code…' });

    try {
      const response = await fetch(apiUrl('/api/v1/whatsapp-qr/start-connection'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'Jimmy Dashboard' }),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || 'Failed to start WhatsApp connection');
      }

      const data = await response.json();
      setWhatsappState({
        connectionId: data.connection_id,
        qrCode: data.qr_code_data,
        status: data.status === 'success' ? 'qr_ready' : 'error',
        message: data.message,
        expiresAt: new Date(Date.now() + 300000).toLocaleTimeString(),
      });
    } catch (error) {
      console.error('Failed to start WhatsApp connection:', error);
      setWhatsappState({ status: 'error', message: String(error) });
    }
  };

  const saveSettings = async (event: React.FormEvent) => {
    event.preventDefault();
    setSavingSettings(true);
    setSettingsStatus('');

    try {
      const response = await fetch(apiUrl('/api/v1/admin/settings'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settingsForm),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Unable to save settings');
      }

      setSettingsStatus(data.message || 'Settings saved successfully.');
      setSettingsForm((prev) => ({
        ...prev,
        telegram_bot_token: '',
        google_api_key: '',
        openai_api_key: '',
        whatsapp_access_token: '',
        telegram_webhook_secret: '',
        public_base_url: '',
        database_url: '',
      }));
    } catch (error) {
      setSettingsStatus(String(error));
    } finally {
      setSavingSettings(false);
    }
  };

  const summaryCards = useMemo(() => {
    if (!analytics) return [];

    return [
      { label: 'Active users', value: analytics.active_users, tone: 'from-cyan-400 to-sky-500' },
      { label: 'Total users', value: analytics.total_users, tone: 'from-violet-400 to-fuchsia-500' },
      { label: 'Messages', value: analytics.total_messages, tone: 'from-emerald-400 to-green-500' },
      { label: 'Workflows', value: analytics.total_workflows, tone: 'from-amber-400 to-orange-500' },
    ];
  }, [analytics]);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_#111827_0%,_#020617_45%,_#020617_100%)] text-slate-100">
      <section className="mx-auto flex max-w-7xl flex-col gap-8 px-6 py-10 lg:px-10">
        <header className="rounded-3xl border border-white/10 bg-white/8 p-8 shadow-2xl shadow-cyan-950/30 backdrop-blur-xl">
          <p className="text-sm uppercase tracking-[0.35em] text-cyan-300">Jimmy Bot Dashboard</p>
          <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="text-4xl font-semibold text-white lg:text-5xl">Connect your users, monitor your bot, and keep the platform feeling alive.</h1>
              <p className="mt-3 max-w-3xl text-slate-300">This dashboard gives you a real-time view of bot activity, active users, workflows, and the health of the platform in one polished control center.</p>
            </div>
            <div className="flex flex-col gap-2">
              <div className="rounded-2xl border border-emerald-400/40 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">API status: {loading ? 'Loading…' : 'Connected'}</div>
              <a href="/settings" className="rounded-2xl border border-cyan-400/40 bg-cyan-400/10 px-4 py-3 text-center text-sm text-cyan-100 hover:bg-cyan-400/20 transition">
                ⚙️ Integration Settings
              </a>
            </div>
          </div>
        </header>

        <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {summaryCards.map((card) => (
            <article key={card.label} className="rounded-3xl border border-white/10 bg-white/8 p-6 shadow-2xl shadow-slate-950/25 backdrop-blur-xl">
              <div className={`mb-4 h-2 rounded-full bg-gradient-to-r ${card.tone}`} />
              <p className="text-sm uppercase tracking-[0.25em] text-slate-300">{card.label}</p>
              <p className="mt-3 text-4xl font-semibold text-white">{card.value}</p>
            </article>
          ))}
        </section>

        <section className="grid gap-6">
          <article className="rounded-3xl border border-white/10 bg-white/8 p-6 shadow-2xl shadow-slate-950/25 backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.25em] text-cyan-300">Live overview</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">Platform Status</h2>
              </div>
              <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-emerald-100">Active</span>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[
                ['Active Users', analytics?.active_users ?? 0],
                ['Total Users', analytics?.total_users ?? 0],
                ['Total Messages', analytics?.total_messages ?? 0],
                ['Response Time', `${analytics?.average_response_time ?? 0}ms`],
              ].map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-400">{label}</p>
                  <p className="mt-2 text-2xl font-bold text-white">{value}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-2xl border border-white/10 bg-slate-900/60 p-4">
              <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Last Updated</p>
              <p className="mt-2 text-sm text-slate-200">{lastUpdated || 'Loading...'}</p>
            </div>
          </article>

          <article className="rounded-3xl border border-white/10 bg-white/8 p-6 shadow-2xl shadow-slate-950/25 backdrop-blur-xl">
            <p className="text-sm uppercase tracking-[0.25em] text-cyan-300">Recent users</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Connected accounts</h2>
            <div className="mt-6 space-y-3">
              {users.length === 0 && !loading ? (
                <p className="text-sm text-slate-300">No users have been connected yet.</p>
              ) : users.map((user) => (
                <article key={user.id} className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-base font-semibold text-white">{user.username || user.email}</p>
                      <p className="text-sm text-slate-300">{user.email}</p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs uppercase tracking-[0.25em] ${user.is_active ? 'bg-emerald-400/10 text-emerald-200' : 'bg-amber-400/10 text-amber-100'}`}>
                      {user.is_active ? 'Active' : 'Pending'}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-400">Joined {user.created_at ? new Date(user.created_at).toLocaleString() : 'recently'}</p>
                </article>
              ))}
            </div>
          </article>
        </section>
      </section>
    </main>
  );
}
