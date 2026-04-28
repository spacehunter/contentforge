'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import api from '@/lib/api';

export default function SettingsPage() {
  const { data: session } = useSession();
  const [pinterestConnected, setPinterestConnected] = useState(false);
  const [pinterestUser, setPinterestUser] = useState<any>(null);
  const [boards, setBoards] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Check for OAuth callback code in URL (after redirect back from Pinterest)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');
    if (code) {
      handleOAuthCallback(code);
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  useEffect(() => {
    checkPinterestStatus();
  }, []);

  const checkPinterestStatus = async () => {
    try {
      const res = await api.get('/pinterest/me');
      setPinterestConnected(true);
      setPinterestUser(res.data.user);
      const bRes = await api.get('/pinterest/boards');
      setBoards(bRes.data.boards || []);
    } catch {
      setPinterestConnected(false);
    }
  };

  const handleOAuthCallback = async (code: string) => {
    setLoading(true);
    try {
      await api.post('/pinterest/connect', { code });
      await checkPinterestStatus();
      alert('Pinterest connected successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to connect Pinterest');
    } finally {
      setLoading(false);
    }
  };

  const connectPinterest = async () => {
    try {
      const res = await api.get('/pinterest/auth-url');
      window.location.href = res.data.auth_url;
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Pinterest OAuth not configured');
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Settings</h2>

      <div className="space-y-6 max-w-2xl">
        {/* Profile */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Profile</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Display Name</label>
              <input
                defaultValue={session?.user?.name || 'Demo User'}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={session?.user?.email || ''}
                disabled
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50"
              />
            </div>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">Save Changes</button>
          </div>
        </div>

        {/* Integrations */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Integrations</h3>

          <div className="space-y-4">
            {/* Pinterest */}
            <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📌</span>
                <div>
                  <p className="font-medium">Pinterest</p>
                  <p className="text-sm text-gray-500">
                    {pinterestConnected
                      ? `Connected as ${pinterestUser?.username || pinterestUser?.business_name || 'Pinterest User'}`
                      : 'Not connected'}
                  </p>
                  {boards.length > 0 && (
                    <p className="text-xs text-gray-400 mt-0.5">{boards.length} boards available</p>
                  )}
                </div>
              </div>
              {pinterestConnected ? (
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Connected</span>
              ) : (
                <button
                  onClick={connectPinterest}
                  disabled={loading}
                  className="bg-red-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-red-700 disabled:opacity-50"
                >
                  {loading ? 'Connecting…' : 'Connect'}
                </button>
              )}
            </div>

            {/* AI Services */}
            {[
              { name: 'LM Studio (Local)', status: 'connected', url: 'http://localhost:1234' },
              { name: 'vLLM Server', status: 'disconnected', url: 'http://localhost:8000' },
              { name: 'ComfyUI (Images)', status: 'connected', url: 'http://localhost:8188' },
            ].map((integration) => (
              <div key={integration.name} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="font-medium">{integration.name}</p>
                  <p className="text-sm text-gray-500">{integration.url}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  integration.status === 'connected'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {integration.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Subscription */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Subscription</h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Current Plan: Free</p>
              <p className="text-sm text-gray-500">Upgrade to unlock unlimited content generation</p>
            </div>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">Upgrade to Pro</button>
          </div>
        </div>
      </div>
    </div>
  );
}
