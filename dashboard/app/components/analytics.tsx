'use client';

import { useEffect, useState } from 'react';

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '');
const apiUrl = (path: string) => `${API_BASE}${path}`;

type AnalyticsData = {
  dates: string[];
  message_counts: number[];
  user_counts: number[];
  response_times: number[];
};

export default function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7'); // days

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const response = await fetch(apiUrl(`/api/v1/admin/analytics/messages?days=${timeRange}`));
        if (response.ok) {
          const data = await response.json();
          setAnalytics(data);
        }
      } catch (error) {
        console.error('Failed to load analytics:', error);
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, [timeRange]);

  const exportData = (format: 'json' | 'csv') => {
    if (!analytics) return;

    let content = '';
    let filename = `analytics-${new Date().toISOString().split('T')[0]}.`;

    if (format === 'json') {
      content = JSON.stringify(analytics, null, 2);
      filename += 'json';
    } else {
      // CSV format
      content = 'Date,Messages,Users,Avg Response Time\n';
      analytics.dates.forEach((date, i) => {
        content += `${date},${analytics.message_counts[i]},${analytics.user_counts[i]},${analytics.response_times[i]}\n`;
      });
      filename += 'csv';
    }

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading analytics...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <h1 className="text-2xl font-bold text-slate-100">Analytics</h1>
        <p className="text-slate-400">Message volume, user growth, and performance metrics</p>
      </div>

      {/* Time Range Selector */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <label className="block text-sm font-medium text-slate-300 mb-3">Time Range</label>
        <div className="flex gap-2">
          {['7', '14', '30', '90'].map((days) => (
            <button
              key={days}
              onClick={() => setTimeRange(days)}
              className={`px-4 py-2 rounded-lg transition-all ${
                timeRange === days
                  ? 'bg-cyan-500 text-white'
                  : 'bg-white/10 text-slate-300 hover:bg-white/20'
              }`}
            >
              {days} days
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 p-6 backdrop-blur-xl">
            <p className="text-sm text-slate-400">Total Messages</p>
            <p className="text-3xl font-bold text-cyan-300">
              {analytics.message_counts.reduce((a, b) => a + b, 0)}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-emerald-500/20 to-green-600/20 p-6 backdrop-blur-xl">
            <p className="text-sm text-slate-400">Peak Messages/Day</p>
            <p className="text-3xl font-bold text-emerald-300">
              {Math.max(...analytics.message_counts, 0)}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-amber-500/20 to-orange-600/20 p-6 backdrop-blur-xl">
            <p className="text-sm text-slate-400">Avg Response Time</p>
            <p className="text-3xl font-bold text-amber-300">
              {(analytics.response_times.reduce((a, b) => a + b, 0) / analytics.response_times.length).toFixed(0)}ms
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-fuchsia-500/20 to-purple-600/20 p-6 backdrop-blur-xl">
            <p className="text-sm text-slate-400">Total Users</p>
            <p className="text-3xl font-bold text-fuchsia-300">
              {Math.max(...analytics.user_counts, 0)}
            </p>
          </div>
        </div>
      )}

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <h3 className="text-lg font-semibold text-slate-100 mb-4">Message Volume Trend</h3>
          <div className="h-64 flex items-center justify-center text-slate-400">
            Chart visualization (connect Recharts for graphs)
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <h3 className="text-lg font-semibold text-slate-100 mb-4">Response Time Distribution</h3>
          <div className="h-64 flex items-center justify-center text-slate-400">
            Chart visualization (connect Recharts for graphs)
          </div>
        </div>
      </div>

      {/* Export Buttons */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <h3 className="text-lg font-semibold text-slate-100 mb-4">Export Analytics</h3>
        <div className="flex gap-3">
          <button
            onClick={() => exportData('json')}
            className="px-6 py-2 rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 transition-all border border-cyan-500/50"
          >
            Export as JSON
          </button>
          <button
            onClick={() => exportData('csv')}
            className="px-6 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 transition-all border border-emerald-500/50"
          >
            Export as CSV
          </button>
        </div>
      </div>
    </div>
  );
}
