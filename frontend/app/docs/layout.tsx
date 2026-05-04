export const metadata = {
  title: 'Documentation — ContentForge',
}

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-5xl mx-auto px-4 py-8 md:py-12 flex gap-8">
        <aside className="hidden md:block w-64 shrink-0">
          <nav className="sticky top-8 space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2">Documentation</h3>
              <ul className="space-y-1">
                <li><a href="#quick-start" className="block text-sm text-gray-600 hover:text-indigo-600">Quick Start</a></li>
                <li><a href="#api-reference" className="block text-sm text-gray-600 hover:text-indigo-600">API Reference</a></li>
                <li><a href="#brand-voice" className="block text-sm text-gray-600 hover:text-indigo-600">Brand Voice Guide</a></li>
              </ul>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <a href="/" className="text-sm text-indigo-600 hover:text-indigo-700">← Back to Home</a>
            </div>
          </nav>
        </aside>
        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>
    </div>
  )
}
