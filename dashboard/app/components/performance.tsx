'use client';

import { useEffect, useState } from 'react';

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '');
const apiUrl = (path: string) => `${API_BASE}${path}`;

type PerformanceMetrics = {
  avg_response_time: number;
  p95_response_time: number;
  p99_response_time: number;
  error_rate: number;
  cache_hit_rate: number;
  uptime_percent: number;
  request_count: number;
  error_count: number;
};

export default function Performance() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(3000);

  useEffect(() => {
    async function loadMetrics() {
      try {
        const response = await fetch(apiUrl('/api/v1/admin/analytics/performance'));
        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
        }
      } catch (error) {
        console.error('Failed to load performance metrics:', error);
      } finally {
        setLoading(false);
      }
    }

    loadMetrics();
    const interval = setInterval(loadMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading performance metrics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <h1 className="text-2xl font-bold text-slate-100">Performance Monitoring</h1>
        <p className="text-slate-400">Real-time API performance and system metrics</p>
      </div>

      {/* Refresh Interval Control */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <label className="block text-sm font-medium text-slate-300 mb-3">Update Frequency</label>
        <div className="flex gap-2">
          {[1000, 3000, 5000].map((interval) => (
            <button
              key={interval}
              onClick={() => setRefreshInterval(interval)}
              className={`px-4 py-2 rounded-lg transition-all text-sm ${
                refreshInterval === interval
                  ? 'bg-cyan-500 text-white'
                  : 'bg-white/10 text-slate-300 hover:bg-white/20'
              }`}
            >
              {interval / 1000}s
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      {metrics && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">Average Response Time</p>
              <p className="text-4xl font-bold text-cyan-300">{metrics.avg_response_time.toFixed(0)}</p>
              <p className="text-xs text-slate-500 mt-2">milliseconds</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-emerald-500/20 to-green-600/20 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">P95 Response Time</p>
              <p className="text-4xl font-bold text-emerald-300">{metrics.p95_response_time.toFixed(0)}</p>
              <p className="text-xs text-slate-500 mt-2">95th percentile</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-amber-500/20 to-orange-600/20 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">P99 Response Time</p>
              <p className="text-4xl font-bold text-amber-300">{metrics.p99_response_time.toFixed(0)}</p>
              <p className="text-xs text-slate-500 mt-2">99th percentile</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-red-500/20 to-pink-600/20 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">Error Rate</p>
              <p className="text-4xl font-bold text-red-300">{(metrics.error_rate * 100).toFixed(2)}%</p>
              <p className="text-xs text-slate-500 mt-2">failed requests</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-fuchsia-500/20 to-purple-600/20 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">Cache Hit Rate</p>
              <p className="text-4xl font-bold text-fuchsia-300">{(metrics.cache_hit_rate * 100).toFixed(1)}%</p>
              <p className="text-xs text-slate-500 mt-2">cached responses</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-violet-500/20 to-indigo-600/20 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">Uptime</p>
              <p className="text-4xl font-bold text-violet-300">{metrics.uptime_percent.toFixed(2)}%</p>
              <p className="text-xs text-slate-500 mt-2">system availability</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">Total Requests</p>
              <div className="flex items-baseline gap-2">
                <p className="text-4xl font-bold text-cyan-300">{metrics.request_count.toLocaleString()}</p>
                <p className="text-xs text-slate-500">requests processed</p>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
              <p className="text-sm text-slate-400 mb-2">Error Count</p>
              <div className="flex items-baseline gap-2">
                <p className={`text-4xl font-bold ${metrics.error_count > 0 ? 'text-red-300' : 'text-emerald-300'}`}>
                  {metrics.error_count}
                </p>
                <p className="text-xs text-slate-500">failed requests</p>
              </div>
            </div>
          </div>

          {/* Performance Bars */}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <p className="text-slate-300 font-medium">Error Rate</p>
                <p className="text-sm text-slate-400">{(metrics.error_rate * 100).toFixed(2)}%</p>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-emerald-500 to-green-600 h-2 rounded-full"
                  style={{ width: `${Math.max(0, Math.min(100, 100 - metrics.error_rate * 10000))}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <p className="text-slate-300 font-medium">Cache Efficiency</p>
                <p className="text-sm text-slate-400">{(metrics.cache_hit_rate * 100).toFixed(1)}%</p>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full"
                  style={{ width: `${metrics.cache_hit_rate * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <p className="text-slate-300 font-medium">System Health</p>
                <p className="text-sm text-slate-400">{metrics.uptime_percent.toFixed(2)}%</p>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-emerald-500 to-green-600 h-2 rounded-full"
                  style={{ width: `${metrics.uptime_percent}%` }}
                />
              </div>
            </div>
          </div>

          {/* Health Status */}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">System Health Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-slate-400">API Response Time</p>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    metrics.avg_response_time < 100
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : metrics.avg_response_time < 500
                      ? 'bg-amber-500/20 text-amber-300'
                      : 'bg-red-500/20 text-red-300'
                  }`}
                >
                  {metrics.avg_response_time < 100 ? '✅ Excellent' : metrics.avg_response_time < 500 ? '⚠️ Good' : '🔴 Slow'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-slate-400">Error Rate</p>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    metrics.error_rate < 0.01
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : metrics.error_rate < 0.05
                      ? 'bg-amber-500/20 text-amber-300'
                      : 'bg-red-500/20 text-red-300'
                  }`}
                >
                  {metrics.error_rate < 0.01 ? '✅ Excellent' : metrics.error_rate < 0.05 ? '⚠️ Good' : '🔴 High'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-slate-400">System Uptime</p>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    metrics.uptime_percent >= 99.9
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : metrics.uptime_percent >= 99
                      ? 'bg-amber-500/20 text-amber-300'
                      : 'bg-red-500/20 text-red-300'
                  }`}
                >
                  {metrics.uptime_percent >= 99.9 ? '✅ Excellent' : metrics.uptime_percent >= 99 ? '⚠️ Good' : '🔴 Poor'}
                </span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
