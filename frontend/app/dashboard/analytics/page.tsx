'use client';
export const dynamic = 'force-dynamic';

import { useState } from 'react';

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d');

  const stats = {
    totalGenerated: 0,
    publishedCount: 0,
    scheduledCount: 0,
    avgEngagement: '0%',
    topChannels: [
      { name: 'Blog', value: 0 },
      { name: 'Social', value: 0 },
      { name: 'Email', value: 0 },
      { name: 'Pinterest', value: 0 },
    ],
    recentActivity: [],
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Analytics</h2>
        <div className="flex gap-2">
          {['7d', '30d', '90d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-lg text-sm ${
                timeRange === range
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              {range === '7d' ? 'Last 7 Days' : range === '30d' ? 'Last 30 Days' : 'Last 90 Days'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Generated', value: stats.totalGenerated, trend: '+0%' },
          { label: 'Published', value: stats.publishedCount, trend: '+0%' },
          { label: 'Scheduled', value: stats.scheduledCount, trend: '+0%' },
          { label: 'Avg Engagement', value: stats.avgEngagement, trend: '+0%' },
        ].map((stat) => (
          <div key={stat.label} className="card">
            <p className="text-sm font-medium text-gray-600">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
            <span className="text-xs text-green-600 font-medium">{stat.trend}</span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Content by Channel</h3>
        {stats.topChannels.map((channel) => (
          <div key={channel.name} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
            <span className="font-medium">{channel.name}</span>
            <div className="flex items-center gap-3">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '0%' }} />
              </div>
              <span className="text-sm text-gray-600 w-8">{channel.value}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 card">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        {stats.recentActivity.length > 0 ? (
          <div className="space-y-2">
            {stats.recentActivity.map((activity, i) => (
              <div key={i} className="text-sm text-gray-600">
                {activity}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No activity yet. Generate your first piece to see activity here!</p>
        )}
      </div>
    </div>
  );
}

