"use client";

import { useEffect, useMemo, useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || (typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000');

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
    telegram_webhook_secret: '',
    public_base_url: '',
  });
  const [settingsStatus, setSettingsStatus] = useState('');
  const [savingSettings, setSavingSettings] = useState(false);

  useEffect(() => {
    let interval: number | undefined;

    async function loadDashboard() {
      try {
        const [analyticsRes, usersRes, integrationsRes] = await Promise.all([
          fetch(`${API_BASE}/api/v1/admin/analytics`),
          fetch(`${API_BASE}/api/v1/admin/users?limit=6`),
          fetch(`${API_BASE}/api/v1/admin/integrations`),
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
        const statusRes = await fetch(`${API_BASE}/api/v1/whatsapp-qr/status/${whatsappState.connectionId}`);
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
      const response = await fetch(`${API_BASE}/api/v1/whatsapp-qr/start-connection`, {
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
      const response = await fetch(`${API_BASE}/api/v1/admin/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settingsForm),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Unable to save settings');
      }

      setSettingsStatus(data.message || 'Settings saved successfully.');
      setSettingsForm((prev) => ({ ...prev, telegram_bot_token: '', google_api_key: '', telegram_webhook_secret: '', public_base_url: '' }));
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
            <div className="rounded-2xl border border-emerald-400/40 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">API status: {loading ? 'Loading…' : 'Connected'}</div>
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

        <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <article className="rounded-3xl border border-white/10 bg-white/8 p-6 shadow-2xl shadow-slate-950/25 backdrop-blur-xl">
            <p className="text-sm uppercase tracking-[0.25em] text-cyan-300">Production setup</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Connect Telegram and Google AI Studio</h2>
            <p className="mt-3 text-slate-300">Save the keys here for the current runtime, then set the same values in your Render dashboard for persistent production deployment.</p>

            <form onSubmit={saveSettings} className="mt-6 space-y-4">
              <label className="block text-sm text-slate-200">
                Telegram bot token
                <input
                  type="password"
                  value={settingsForm.telegram_bot_token}
                  onChange={(event) => setSettingsForm((prev) => ({ ...prev, telegram_bot_token: event.target.value }))}
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-400"
                  placeholder="123456:ABCDEF"
                />
              </label>
              <label className="block text-sm text-slate-200">
                Google AI Studio API key
                <input
                  type="password"
                  value={settingsForm.google_api_key}
                  onChange={(event) => setSettingsForm((prev) => ({ ...prev, google_api_key: event.target.value }))}
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-400"
                  placeholder="AIza..."
                />
              </label>
              <label className="block text-sm text-slate-200">
                Telegram webhook secret
                <input
                  type="password"
                  value={settingsForm.telegram_webhook_secret}
                  onChange={(event) => setSettingsForm((prev) => ({ ...prev, telegram_webhook_secret: event.target.value }))}
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-400"
                  placeholder="optional secret"
                />
              </label>
              <label className="block text-sm text-slate-200">
                Public base URL
                <input
                  type="url"
                  value={settingsForm.public_base_url}
                  onChange={(event) => setSettingsForm((prev) => ({ ...prev, public_base_url: event.target.value }))}
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-400"
                  placeholder="https://your-app.onrender.com"
                />
              </label>

              <button
                type="submit"
                disabled={savingSettings}
                className="w-full rounded-2xl bg-cyan-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {savingSettings ? 'Saving…' : 'Save production settings'}
              </button>
            </form>

            {settingsStatus ? <p className="mt-4 rounded-2xl border border-cyan-400/30 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100">{settingsStatus}</p> : null}
          </article>
          <article className="rounded-3xl border border-white/10 bg-white/8 p-6 shadow-2xl shadow-slate-950/25 backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.25em] text-cyan-300">Live overview</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">What’s running right now</h2>
              </div>
              <span className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-cyan-100">Bot ready</span>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {[
                ['Average response time', `${analytics?.average_response_time ?? 0} ms`],
                ['Last sync', analytics?.generated_at ? new Date(analytics.generated_at).toLocaleString() : '—'],
                ['Platform mode', 'AI-first messaging'],
                ['Connection flow', 'Telegram + WhatsApp + Web'],
              ].map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-400">{label}</p>
                  <p className="mt-2 text-lg font-semibold text-white">{value}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 rounded-3xl border border-white/10 bg-slate-900/70 p-6 shadow-2xl shadow-slate-950/25">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.25em] text-cyan-300">WhatsApp connection</p>
                  <h3 className="mt-2 text-2xl font-semibold text-white">Scan to connect your WhatsApp bot</h3>
                </div>
                <div className="rounded-2xl bg-slate-800/70 px-4 py-2 text-xs uppercase tracking-[0.25em] text-slate-300">
                  {whatsappState.status ? whatsappState.status.replace('_', ' ') : 'Idle'}
                </div>
              </div>

              <div className="mt-6 grid gap-4 lg:grid-cols-2">
                <div className="rounded-3xl border border-white/10 bg-slate-900/60 p-4">
                  {whatsappState.qrCode ? (
                    <img src={whatsappState.qrCode} alt="WhatsApp QR code" className="mx-auto max-h-72 object-contain" />
                  ) : (
                    <div className="flex min-h-[220px] items-center justify-center rounded-3xl bg-slate-950/40 text-slate-300">
                      <div className="text-sm text-slate-300">Start a connection to display the QR code.</div>
                    </div>
                  )}
                </div>
                <div className="space-y-4 rounded-3xl border border-white/10 bg-slate-900/60 p-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Instructions</p>
                    <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-200">
                      <li>Open WhatsApp on your phone.</li>
                      <li>Go to Settings &gt; Linked Devices &gt; Link a Device.</li>
                      <li>Point your camera at the QR code shown here.</li>
                      <li>Wait for confirmation in this dashboard.</li>
                    </ol>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4 text-sm text-slate-300">
                    <p className="font-semibold text-white">Status</p>
                    <p className="mt-2">{whatsappState.message || 'Ready to start a new connection.'}</p>
                    {whatsappState.phoneNumber ? (
                      <p className="mt-2 text-emerald-300">Connected: {whatsappState.phoneNumber}</p>
                    ) : null}
                    {whatsappState.expiresAt ? (
                      <p className="mt-2 text-xs text-slate-500">QR expires at {whatsappState.expiresAt}</p>
                    ) : null}
                  </div>

                  <button
                    className="w-full rounded-2xl bg-cyan-500 px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-cyan-400"
                    onClick={startWhatsappConnection}
                  >
                    {whatsappState.status === 'qr_ready' ? 'Refresh QR Code' : 'Start WhatsApp connection'}
                  </button>
                </div>
              </div>

              <div className="mt-6 rounded-3xl border border-white/10 bg-slate-950/40 p-4 text-sm text-slate-300">
                <p className="font-semibold text-white">Telegram webhook setup</p>
                <p className="mt-2">Use your public API hostname with the Telegram webhook endpoint below.</p>
                <p className="mt-3 break-all text-slate-200">{telegramInfo.telegram_webhook_url || `${API_BASE}/api/v1/telegram/webhook`}</p>
                <p className="mt-3 text-xs text-slate-500">
                  {telegramInfo.telegram_configured
                    ? 'Telegram is configured with a webhook and secret.'
                    : 'Configure TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET, and PUBLIC_BASE_URL for production.'}
                </p>
              </div>
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
