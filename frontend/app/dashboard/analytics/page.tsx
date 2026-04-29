'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import api from '@/lib/api';

interface AnalyticsData {
  summary: {
    total: number;
    this_month: number;
    by_type: Record<string, number>;
    by_status: Record<string, number>;
  };
  daily: Array<{ date: string; count: number }>;
  monthly: Array<{ month: string; count: number }>;
  recent: Array<{
    id: number;
    title: string;
    type: string;
    status: string;
    created_at: string;
  }>;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/analytics')
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load analytics'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6">Loading analytics…</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!data) return null;

  const byType = data.summary?.by_type || {};
  const maxType = Math.max(...Object.values(byType), 1);
  const byStatus = data.summary?.by_status || {};
  const maxStatus = Math.max(...Object.values(byStatus), 1);
  const daily = data.daily || [];
  const maxDaily = Math.max(...daily.map((d) => d.count), 1);

  const statusColors: Record<string, string> = {
    generated: 'bg-blue-500',
    published: 'bg-green-500',
    draft: 'bg-yellow-500',
    pending: 'bg-gray-400',
  };

  const typeColors: Record<string, string> = {
    blog: 'bg-indigo-500',
    social: 'bg-pink-500',
    email: 'bg-orange-500',
    image: 'bg-purple-500',
    pinterest: 'bg-red-500',
    hero: 'bg-teal-500',
    default: 'bg-gray-500',
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Analytics</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card bg-indigo-50 border border-indigo-100">
          <p className="text-sm text-gray-500">Total Content</p>
          <p className="text-3xl font-bold text-indigo-700">{data.summary.total}</p>
        </div>
        <div className="card bg-green-50 border border-green-100">
          <p className="text-sm text-gray-500">This Month</p>
          <p className="text-3xl font-bold text-green-700">{data.summary.this_month}</p>
        </div>
        <div className="card bg-purple-50 border border-purple-100">
          <p className="text-sm text-gray-500">Published</p>
          <p className="text-3xl font-bold text-purple-700">{byStatus.published || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Content by Type */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Content by Type</h3>
          <div className="space-y-3">
            {Object.entries(byType).map(([type, count]) => (
              <div key={type}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="capitalize">{type}</span>
                  <span className="font-semibold">{count}</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full ${typeColors[type] || typeColors.default}`}
                    style={{ width: `${(count / maxType) * 100}%` }}
                  />
                </div>
              </div>
            ))}
            {Object.keys(byType).length === 0 && (
              <p className="text-sm text-gray-400">No content generated yet.</p>
            )}
          </div>
        </div>

        {/* Content by Status */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Content by Status</h3>
          <div className="space-y-3">
            {Object.entries(byStatus).map(([status, count]) => (
              <div key={status}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="capitalize">{status}</span>
                  <span className="font-semibold">{count}</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full ${statusColors[status] || 'bg-gray-500'}`}
                    style={{ width: `${(count / maxStatus) * 100}%` }}
                  />
                </div>
              </div>
            ))}
            {Object.keys(byStatus).length === 0 && (
              <p className="text-sm text-gray-400">No content generated yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Daily Trend */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Last 7 Days</h3>
        <div className="flex items-end gap-2 h-32">
          {daily.map((d) => (
            <div key={d.date} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-indigo-500 rounded-t-md"
                style={{ height: `${(d.count / maxDaily) * 100}%`, minHeight: d.count > 0 ? '8px' : '0' }}
              />
              <span className="text-xs text-gray-500">{d.date.slice(5)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="divide-y divide-gray-100">
          {data.recent.map((item) => (
            <div key={item.id} className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-sm">{item.title}</p>
                <p className="text-xs text-gray-500 capitalize">{item.type} · {item.status}</p>
              </div>
              <span className="text-xs text-gray-400">
                {new Date(item.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
          {data.recent.length === 0 && (
            <p className="text-sm text-gray-400 py-4">No recent activity.</p>
          )}
        </div>
      </div>
    </div>
  );
}
