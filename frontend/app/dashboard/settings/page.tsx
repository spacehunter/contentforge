'use client';
export const dynamic = 'force-dynamic';

export default function SettingsPage() {
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
                defaultValue="Demo User"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                defaultValue="user@example.com"
                disabled
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50"
              />
            </div>
            <button className="btn-primary">Save Changes</button>
          </div>
        </div>

        {/* AI Integrations */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">AI Integrations</h3>
          <div className="space-y-3">
            {[
              { name: 'LM Studio (Local)', status: 'connected', url: 'http://localhost:1234' },
              { name: 'vLLM Server', status: 'disconnected', url: 'http://localhost:8000' },
              { name: 'ComfyUI (Images)', status: 'connected', url: 'http://localhost:8188' },
            ].map((integration) => (
              <div key={integration.name} className="flex items-center justify-between py-2">
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
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
              Upgrade to Pro
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

