'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import useStore from '@/stores';
import api from '@/lib/api';

const CONTENT_TYPES = [
  { id: 'blog', name: 'Blog Post', icon: '📝' },
  { id: 'social', name: 'Social Media', icon: '📱' },
  { id: 'email', name: 'Email Newsletter', icon: '📧' },
  { id: 'pinterest', name: 'Pinterest Pin', icon: '📌' },
];

export default function GeneratePage() {
  const [form, setForm] = useState({
    title: '',
    content_type: 'blog',
    prompt: '',
    tone: 'professional',
    brand_id: null as number | null,
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [brandsList, setBrandsList] = useState<any[]>([]);
  const [planError, setPlanError] = useState<string | null>(null);
  const addContent = useStore((state) => state.addContent);

  useEffect(() => {
    api.get('/brands').then(res => setBrandsList(res.data)).catch(() => setBrandsList([]));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setPlanError(null);
    try {
      const payload: any = { ...form };
      if (!payload.brand_id) delete payload.brand_id;
      const res = await api.post('/content/generate', payload);
      setResult(res.data);
      addContent(res.data);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Generation failed';
      if (msg.toLowerCase().includes('plan limit') || msg.toLowerCase().includes('upgrade')) {
        setPlanError(msg);
      } else {
        alert(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Generate Content</h2>
      
      {planError && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-medium">{planError}</p>
          <div className="mt-2 flex gap-2">
            <button
              onClick={() => window.location.href = '/dashboard/settings'}
              className="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-indigo-700"
            >
              Upgrade Plan
            </button>
            <button
              onClick={() => setPlanError(null)}
              className="bg-white border border-gray-300 text-gray-700 px-3 py-1.5 rounded-lg text-sm hover:bg-gray-50"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Title</label>
          <input
            value={form.title}
            onChange={(e) => setForm({...form, title: e.target.value})}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
            placeholder="Summer Campaign Blog Post"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Content Type</label>
          <div className="mt-1 grid grid-cols-2 md:grid-cols-4 gap-3">
            {CONTENT_TYPES.map((type) => (
              <button
                key={type.id}
                type="button"
                onClick={() => setForm({...form, content_type: type.id})}
                className={`flex flex-col items-center p-3 rounded-lg border ${
                  form.content_type === type.id
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <span className="text-2xl">{type.icon}</span>
                <span className="text-sm mt-1">{type.name}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Brand</label>
          <select
            value={form.brand_id ?? ''}
            onChange={(e) => setForm({...form, brand_id: e.target.value ? Number(e.target.value) : null})}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
          >
            <option value="">-- No brand (generic) --</option>
            {brandsList.map((b) => (
              <option key={b.id} value={b.id}>{b.name} ({b.industry})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">What should we write about?</label>
          <textarea
            value={form.prompt}
            onChange={(e) => setForm({...form, prompt: e.target.value})}
            rows={4}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
            placeholder="Describe the topic, key points, angle..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Tone</label>
          <select
            value={form.tone}
            onChange={(e) => setForm({...form, tone: e.target.value})}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
          >
            <option value="professional">Professional</option>
            <option value="casual">Casual</option>
            <option value="playful">Playful</option>
            <option value="authoritative">Authoritative</option>
            <option value="friendly">Friendly</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : '✨ Generate Content'}
        </button>
      </form>

      {result && (
        <div className="mt-6 card">
          <h3 className="font-semibold text-lg mb-2">Generated: {result.title}</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap" style={{fontFamily: 'system-ui'}}>
              {result.generated_text}
            </pre>
          </div>
          <div className="mt-4 flex gap-2">
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700">
              Publish Now
            </button>
            <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50">
              Schedule
            </button>
            <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50">
              Regenerate
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

