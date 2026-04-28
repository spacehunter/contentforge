'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import useStore from '@/stores';
import api from '@/lib/api';

const IMAGE_TEMPLATES = [
  { id: 'pinterest', name: 'Pinterest Pin', icon: '📌', dimensions: '768x1344' },
  { id: 'hero', name: 'Hero Banner', icon: '🖼️', dimensions: '1344x768' },
  { id: 'before_after', name: 'Before/After', icon: '⚡', dimensions: '1024x1024' },
];

export default function GenerateImagePage() {
  const [form, setForm] = useState({
    prompt: '',
    template_type: 'pinterest',
    brand_id: null as number | null,
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [brandsList, setBrandsList] = useState<any[]>([]);
  const addContent = useStore((state) => state.addContent);

  useEffect(() => {
    api.get('/brands').then(res => setBrandsList(res.data)).catch(() => setBrandsList([]));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload: any = { ...form };
      if (!payload.brand_id) delete payload.brand_id;
      const res = await api.post('/content/generate-image', payload);
      setResult(res.data);
      addContent?.(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Image generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Generate Images</h2>
      
      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Image Template</label>
          <div className="mt-1 grid grid-cols-3 gap-3">
            {IMAGE_TEMPLATES.map((tmpl) => (
              <button
                key={tmpl.id}
                type="button"
                onClick={() => setForm({...form, template_type: tmpl.id})}
                className={`flex flex-col items-center p-3 rounded-lg border ${
                  form.template_type === tmpl.id
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <span className="text-2xl">{tmpl.icon}</span>
                <span className="text-sm mt-1 font-medium">{tmpl.name}</span>
                <span className="text-xs text-gray-400">{tmpl.dimensions}</span>
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
          <label className="block text-sm font-medium text-gray-700">What should we generate?</label>
          <textarea
            value={form.prompt}
            onChange={(e) => setForm({...form, prompt: e.target.value})}
            rows={4}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
            placeholder="Describe the image you want to generate..."
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Generating (this takes ~30s)...' : '🎨 Generate Image'}
        </button>
      </form>

      {result && (
        <div className="mt-6 card">
          <h3 className="font-semibold text-lg mb-2">Generated Image</h3>
          <div className="rounded-lg overflow-hidden bg-gray-100">
            <img 
              src={`http://localhost:8000${result.image_url}`} 
              alt="Generated" 
              className="w-full h-auto max-h-[600px] object-contain"
              onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder.png'; }}
            />
          </div>
          <div className="mt-4 flex gap-2">
            <button 
              onClick={() => window.location.href = '/dashboard/content'}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700"
            >
              Publish Now
            </button>
            <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50">
              Schedule
            </button>
            <button 
              onClick={() => setResult(null)}
              className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50"
            >
              Regenerate
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

