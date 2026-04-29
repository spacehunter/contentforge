'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LandingPage() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [waitlistCount, setWaitlistCount] = useState(null);
  const router = useRouter();

  useEffect(() => {
    fetch('http://localhost:8000/waitlist/count')
      .then(r => r.json())
      .then(d => setWaitlistCount(d.count))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/waitlist', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name }),
      });
      if (res.ok) setSubmitted(true);
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <span className="text-xl font-bold text-indigo-600">ContentForge</span>
          <div className="flex gap-3 items-center">
            <a href="/login" className="text-gray-600 hover:text-gray-900 font-medium">Sign In</a>
            <a href="/login?mode=register" className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-medium">
              Get Started
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-gradient-to-b from-indigo-50 to-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 mb-6 leading-tight">
            AI-Powered Content<br />That Sounds Like <span className="text-indigo-600">You</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Generate blogs, social posts, Pinterest pins, and marketing assets — all trained on your brand voice. 
            Zero cloud API costs. Runs entirely on your hardware.
          </p>

          {/* Waitlist form */}
          <div className="max-w-md mx-auto">
            {!submitted ? (
              <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
                <input
                  type="text" placeholder="Your name (optional)" value={name} onChange={e => setName(e.target.value)}
                  className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
                <input
                  type="email" required placeholder="Enter your email" value={email} onChange={e => setEmail(e.target.value)}
                  className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
                <button
                  type="submit" disabled={loading}
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
                >
                  {loading ? '...' : 'Join Waitlist'}
                </button>
              </form>
            ) : (
              <div className="bg-green-50 text-green-800 px-4 py-3 rounded-lg font-medium">
                ✅ You're on the waitlist! We'll email you when early access opens.
              </div>
            )}
            {waitlistCount !== null && (
              <p className="text-sm text-gray-500 mt-3">
                {waitlistCount}+ people on the waitlist
              </p>
            )}
          </div>

          <div className="mt-10 flex justify-center gap-6 text-sm text-gray-500">
            <span>⚡ No credit card required</span>
            <span>🚀 Free 3-piece trial</span>
            <span>🔒 100% local AI</span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Everything You Need to Scale Your Brand
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: '✍️', title: 'Brand Voice', desc: 'Train the AI once on your tone, style, and industry. Every piece reads like you wrote it.' },
              { icon: '🖼️', title: 'Image Generation', desc: 'Create Pinterest pins, hero banners, and before/after visuals with Flux — directly from prompts.' },
              { icon: '📌', title: 'One-Click Publishing', desc: 'Push content to Pinterest and WordPress without leaving the dashboard.' },
              { icon: '📊', title: 'Analytics', desc: 'Track what you create, when, and how much. Monthly and daily trend views built-in.' },
              { icon: '💰', title: 'Monetization Ready', desc: 'Starter ($49/mo) and Pro ($149/mo) plans with gated features. Stripe Checkout pre-wired.' },
              { icon: '🖥️', title: 'On-Device First', desc: 'Runs on your DGX Spark. No API keys. No tokens. No cloud dependencies.' },
            ].map(f => (
              <div key={f.title} className="bg-gray-50 rounded-xl p-6 hover:shadow-md transition">
                <div className="text-3xl mb-3">{f.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-gray-900 text-white py-20">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Simple Pricing</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: 'Free', price: '$0', desc: '3 content pieces, 1 brand. No card required.', cta: 'Start Now', href: '/login?mode=register' },
              { name: 'Starter', price: '$49/mo', desc: '5 brands, 100 pieces/mo, image gen, Pinterest + WordPress.', cta: 'Join Waitlist', href: '#waitlist' },
              { name: 'Pro', price: '$149/mo', desc: 'Unlimited everything. All integrations. Priority support.', cta: 'Join Waitlist', href: '#waitlist' },
            ].map(p => (
              <div key={p.name} className={`rounded-xl p-6 text-center ${p.name === 'Starter' ? 'bg-indigo-600 ring-2 ring-indigo-400' : 'bg-gray-800'}`}>
                <h3 className="text-xl font-semibold mb-2">{p.name}</h3>
                <div className="text-3xl font-bold mb-2">{p.price}</div>
                <p className="text-gray-300 text-sm mb-6">{p.desc}</p>
                <a href={p.href} className="inline-block bg-white text-gray-900 px-5 py-2 rounded-lg font-medium hover:bg-gray-100">
                  {p.cta}
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-10">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          © {new Date().getFullYear()} ContentForge. AI content generation for brands.
        </div>
      </footer>
    </div>
  );
}
