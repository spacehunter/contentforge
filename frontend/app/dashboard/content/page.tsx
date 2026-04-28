'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import useStore from '@/stores';
import api from '@/lib/api';

export default function ContentPage() {
  const contents = useStore((state) => state.contents);
  const setContents = useStore((state) => state.setContents);
  const [boards, setBoards] = useState<any[]>([]);
  const [pinterestConnected, setPinterestConnected] = useState(false);
  const [publishLoading, setPublishLoading] = useState<Record<number,boolean>>({});

  useEffect(() => {
    api.get('/content').then((res) => setContents(res.data)).catch(()=>{});
    // Check Pinterest status
    api.get('/pinterest/me')
      .then(() => setPinterestConnected(true))
      .catch(() => setPinterestConnected(false));
    // Load boards if connected
    if (pinterestConnected) {
      api.get('/pinterest/boards').then((res) => setBoards(res.data.boards || [])).catch(()=>{});
    }
  }, [setContents, pinterestConnected]);

  const handlePublishPinterest = async (content: any) => {
    if (!pinterestConnected) {
      alert('Connect Pinterest in Settings first.');
      return;
    }
    if (!boards.length) {
      alert('No Pinterest boards found. Check your Pinterest account.');
      return;
    }
    const boardId = boards[0].id;
    if (!confirm(`Publish "${content.title}" to Pinterest board "${boards[0].name}"?`)) return;
    setPublishLoading((p) => ({ ...p, [content.id]: true }));
    try {
      const res = await api.post('/pinterest/pin', {
        content_id: content.id,
        board_id: String(boardId),
        title: content.title,
        description: content.prompt,
        link: '',
      });
      alert('Published! ' + res.data.pinterest_url);
      api.get('/content').then((r) => setContents(r.data));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Publish failed');
    } finally {
      setPublishLoading((p) => ({ ...p, [content.id]: false }));
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Content Library</h2>

      {!pinterestConnected && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
          Pinterest not connected. <a href="/dashboard/settings" className="underline">Connect in Settings</a> to publish pins.
        </div>
      )}

      {contents.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {contents.map((item) => (
            <div key={item.id} className="card flex flex-col">
              {item.image_url && (
                <div className="-mx-6 -mt-6 mb-4 rounded-t-lg overflow-hidden bg-gray-100">
                  <img
                    src={`http://localhost:8000${item.image_url}`}
                    alt={item.title}
                    className="w-full h-48 object-cover"
                    onError={(e) => { (e.target as HTMLImageElement).style.display='none'; }}
                  />
                </div>
              )}
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{item.title}</h4>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">{item.prompt}</p>
                <div className="mt-3 flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    item.status === 'published'
                      ? 'bg-green-100 text-green-800'
                      : item.status === 'scheduled'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {item.status}
                  </span>
                  <span className="text-xs text-gray-400">{item.content_type}</span>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                {item.content_type === 'image' && item.status !== 'published' && (
                  <button
                    onClick={() => handlePublishPinterest(item)}
                    disabled={publishLoading[item.id]}
                    className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
                  >
                    {publishLoading[item.id] ? 'Publishing…' : '📌 Pin it'}
                  </button>
                )}
                <button className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">No content generated yet. Head to Generate to create your first piece!</p>
        </div>
      )}
    </div>
  );
}
