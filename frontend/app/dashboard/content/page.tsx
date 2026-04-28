'use client';
export const dynamic = 'force-dynamic';

import useStore from '@/stores';

export default function ContentPage() {
  const content = useStore((state) => state.contents);

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Content Library</h2>

      {content.length > 0 ? (
        <div className="space-y-3">
          {content.map((item) => (
            <div key={item.id} className="card flex items-center justify-between">
              <div>
                <h4 className="font-semibold">{item.title}</h4>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  item.status === 'published'
                    ? 'bg-green-100 text-green-800'
                    : item.status === 'scheduled'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {item.status}
                </span>
              </div>
              <div className="flex gap-2">
                <button className="text-sm text-indigo-600 hover:text-indigo-800">View</button>
                <button className="text-sm text-gray-600 hover:text-gray-800">Edit</button>
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

