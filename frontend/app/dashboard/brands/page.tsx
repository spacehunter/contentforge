'use client';
export const dynamic = 'force-dynamic';

import { useState } from 'react';
import useStore from '@/stores';
import { brands } from '@/lib/api';

export default function BrandsPage() {
  const [form, setForm] = useState({ name: '', voice: '', industry: '', target_audience: '' });
  const [loading, setLoading] = useState(false);
  const brandList = useStore((state) => state.brands);
  const addBrand = useStore((state) => state.addBrand);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await brands.create(form);
      addBrand(res.data);
      setForm({ name: '', voice: '', industry: '', target_audience: '' });
      alert('Brand created!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create brand');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Your Brands</h2>

      {/* Create Brand Form */}
      <div className="card mb-6">
        <h3 className="text-lg font-semibold mb-4">Add New Brand</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Brand Name</label>
            <input
              value={form.name}
              onChange={(e) => setForm({...form, name: e.target.value})}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Brand Voice (describe personality)</label>
            <textarea
              value={form.voice}
              onChange={(e) => setForm({...form, voice: e.target.value})}
              rows={3}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
              placeholder="e.g., Professional but approachable, uses humor, avoids jargon..."
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Industry</label>
              <input
                value={form.industry}
                onChange={(e) => setForm({...form, industry: e.target.value})}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Target Audience</label>
              <input
                value={form.target_audience}
                onChange={(e) => setForm({...form, target_audience: e.target.value})}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                required
              />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Creating...' : 'Create Brand'}
          </button>
        </form>
      </div>

      {/* Brand List */}
      {brandList.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {brandList.map((brand) => (
            <div key={brand.id} className="card">
              <h4 className="font-semibold text-lg">{brand.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{brand.industry}</p>
              <p className="text-sm text-gray-500 mt-2 line-clamp-2">{brand.voice}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">No brands yet. Create your first brand above!</p>
        </div>
      )}
    </div>
  );
}

