'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import api, { billing } from '@/lib/api';

export default function SettingsPage() {
  const { data: session } = useSession();
  const [pinterestConnected, setPinterestConnected] = useState(false);
  const [pinterestUser, setPinterestUser] = useState<any>(null);
  const [boards, setBoards] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Billing state
  const [plan, setPlan] = useState('free');
  const [billingLoading, setBillingLoading] = useState(false);
  const [billingMsg, setBillingMsg] = useState('');
  const [referral, setReferral] = useState<any>(null);

  useEffect(() => {
    checkPinterestStatus();
    fetchBilling();
    fetchReferral();
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

  const fetchReferral = async () => {
    try {
      const res = await api.get('/referral/info');
      setReferral(res.data);
    } catch {
      setReferral(null);
    }
  };

  const fetchBilling = async () => {
    try {
      const res = await billing.subscription();
      const data = res.data;
      if (data && data.plan_id && data.status !== 'none') {
        setPlan(data.plan_id);
      } else {
        setPlan('free');
      }
    } catch {
      setPlan('free');
    }
  };

  const handleCheckout = async (plan_id: string) => {
    setBillingLoading(true);
    setBillingMsg('');
    try {
      const res = await billing.checkout(plan_id);
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (err: any) {
      setBillingMsg(err.response?.data?.detail || 'Checkout failed');
    } finally {
      setBillingLoading(false);
    }
  };

  const openPortal = async () => {
    setBillingLoading(true);
    try {
      const res = await billing.portal();
      if (res.data.portal_url) {
        window.location.href = res.data.portal_url;
      }
    } catch (err: any) {
      setBillingMsg(err.response?.data?.detail || 'Portal failed');
    } finally {
      setBillingLoading(false);
    }
  };

  // Check for OAuth callback code in URL (after redirect back from Pinterest)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      handleOAuthCallback(code);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  // Check for checkout success/cancel
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('checkout') === 'success') {
      setBillingMsg('Subscription activated!');
      fetchBilling();
      window.history.replaceState({}, '', window.location.pathname);
    }
    if (params.get('checkout') === 'cancel') {
      setBillingMsg('Checkout cancelled.');
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

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
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Current Plan: <span className="capitalize">{plan}</span></p>
                <p className="text-sm text-gray-500">
                  {plan === 'pro'
                    ? 'You have unlimited access. Thank you!'
                    : plan === 'starter'
                    ? 'You are on the Starter plan.'
                    : 'Upgrade to unlock unlimited content generation'}
                </p>
              </div>
              {plan === 'free' ? (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleCheckout('starter')}
                    disabled={billingLoading}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {billingLoading ? '…' : 'Upgrade Starter'}
                  </button>
                  <button
                    onClick={() => handleCheckout('pro')}
                    disabled={billingLoading}
                    className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
                  >
                    {billingLoading ? '…' : 'Upgrade Pro'}
                  </button>
                </div>
              ) : (
                <button
                  onClick={openPortal}
                  disabled={billingLoading}
                  className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
                >
                  {billingLoading ? '…' : 'Manage Billing'}
                </button>
              )}
            </div>
            {billingMsg && (
              <div className={`text-sm px-3 py-2 rounded-lg ${billingMsg.includes('activated') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                {billingMsg}
              </div>
            )}
          </div>
        </div>
        {/* Referrals */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Referrals</h3>
          {referral ? (
            <div className="space-y-3">
              <p className="text-sm text-gray-600">Share your link to earn <strong>10 bonus content pieces</strong> per friend who signs up and generates their first piece.</p>
              <div className="flex items-center gap-2">
                <input
                  readOnly
                  value={referral.referral_link || ''}
                  className="flex-1 rounded-lg border border-gray-300 px-3 py-2 bg-gray-50 text-sm"
                />
                <button
                  onClick={() => navigator.clipboard.writeText(referral.referral_link).then(() => alert('Copied!'))}
                  className="bg-indigo-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-indigo-700"
                >
                  Copy
                </button>
              </div>
              <div className="flex gap-4 text-sm text-gray-600">
                <span><strong>{referral.referrals || 0}</strong> referrals</span>
                <span><strong>{referral.bonus_pieces || 0}</strong> bonus pieces earned</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">Loading referral info…</p>
          )}
        </div>
      </div>
    </div>
  );
}
