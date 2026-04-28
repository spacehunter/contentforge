'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import useStore from '../stores';
import { auth } from '../lib/api';

export default function Home() {
  const [loginMode, setLoginMode] = useState(true);
  const [form, setForm] = useState({ email: '', password: '', name: '' });
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const setToken = useStore((state) => state.setToken);
  const setUser = useStore((state) => state.setUser);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = loginMode ? await auth.login(form) : await auth.register(form);
      const { access_token } = res.data;
      setToken(access_token);
      // Fetch user data (simplified)
      setUser({ email: form.email, name: form.name || form.email });
      router.push('/dashboard');
    } catch (err) {
      alert(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-indigo-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            ContentForge
          </h1>
          <p className="text-xl text-indigo-200 mb-8 max-w-2xl mx-auto">
            AI-powered content generation platform. Create blogs, social posts, and marketing assets 
            that match your brand voice — automatically.
          </p>
        </div>

        <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            {loginMode ? 'Welcome Back' : 'Get Started Free'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({...form, email: e.target.value})}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm({...form, password: e.target.value})}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>
            {!loginMode && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({...form, name: e.target.value})}
                  className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium"
            >
              {loading ? 'Loading...' : (loginMode ? 'Sign In' : 'Create Account')}
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-600">
            {loginMode ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => setLoginMode(!loginMode)}
              className="text-indigo-600 hover:text-indigo-500 font-medium"
            >
              {loginMode ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>

        {/* Features Grid */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { title: 'Brand Voice Training', desc: 'Teach AI your unique brand voice once, apply everywhere' },
            { title: 'Multi-Channel Content', desc: 'Blogs, social posts, pins, emails — all from one platform' },
            { title: 'Local AI First', desc: 'Runs on your DGX Spark. Private, fast, zero cloud API costs' },
          ].map((feature) => (
            <div key={feature.title} className="card text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
