'use client';
export const dynamic = 'force-dynamic';

import { useRouter } from 'next/navigation';
import useStore from '@/stores';

export default function DashboardRoute() {
  const user = useStore((state) => state.user);
  const token = useStore((state) => state.token);
  const router = useRouter();

  // Already in dashboard, show overview
  return (
    <div>
      <h2 className="text-lg font-medium text-gray-900 mb-4">Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Stat Cards */}
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Content Generated</p>
          <p className="text-3xl font-bold text-indigo-600 mt-2">0</p>
          <p className="text-sm text-gray-500 mt-1">This month</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Active Brands</p>
          <p className="text-3xl font-bold text-indigo-600 mt-2">0</p>
          <p className="text-sm text-gray-500 mt-1">Set up brands</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-600">Plan</p>
          <p className="text-3xl font-bold text-indigo-600 mt-2">Free</p>
          <p className="text-sm text-gray-500 mt-1">Upgrade for more</p>
        </div>
      </div>

      <div className="mt-8 card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <button onClick={() => router.push('/dashboard/generate')} className="btn-primary">
            ✨ Generate New Content
          </button>
          <button onClick={() => router.push('/dashboard/brands')} className="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50">
            🏢 Add Brand
          </button>
        </div>
      </div>

      <div className="mt-8 card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Getting Started</h3>
        <div className="space-y-3">
          {[
            { step: 1, label: 'Create your brand voice profile', done: false },
            { step: 2, label: 'Generate your first content piece', done: false },
            { step: 3, label: 'Publish to your channels', done: false },
            { step: 4, label: 'Review analytics & optimize', done: false },
          ].map((item) => (
            <div key={item.step} className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${item.done ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-600'}`}>
                {item.done ? '✓' : item.step}
              </div>
              <span className={item.done ? 'text-gray-500 line-through' : 'text-gray-900'}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

