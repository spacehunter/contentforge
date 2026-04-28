export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-indigo-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">ContentForge</h1>
          <p className="text-xl text-indigo-200 mb-8 max-w-2xl mx-auto">
            AI-powered content generation platform. Create blogs, social posts, and marketing assets 
            that match your brand voice — automatically.
          </p>
          <div className="flex justify-center gap-4">
            <a href="/login" className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 font-medium">Get Started Free</a>
            <a href="/dashboard" className="bg-white/10 text-white px-6 py-3 rounded-lg hover:bg-white/20 font-medium">Dashboard →</a>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { title: 'Brand Voice Training', desc: 'Teach AI your unique brand voice once, apply everywhere' },
            { title: 'Multi-Channel Content', desc: 'Blogs, social posts, pins, emails — all from one platform' },
            { title: 'Local AI First', desc: 'Runs on your DGX Spark. Private, fast, zero cloud API costs' },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-xl shadow-sm p-6 text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-600">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export const metadata = { title: 'ContentForge - AI Marketing Platform' };
