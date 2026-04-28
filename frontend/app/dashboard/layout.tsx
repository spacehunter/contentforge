'use client';

import { useState } from 'react';
import Link from 'next/link';
import useStore from '../../stores';
import { brands, content as contentAPI } from '../../lib/api';

const SIDEBAR_ITEMS = [
  { name: 'Dashboard', href: '/dashboard', icon: '📊' },
  { name: 'Brands', href: '/dashboard/brands', icon: '🏢' },
  { name: 'Generate', href: '/dashboard/generate', icon: '✨' },
  { name: 'Content', href: '/dashboard/content', icon: '📝' },
  { name: 'Analytics', href: '/dashboard/analytics', icon: '📈' },
  { name: 'Settings', href: '/dashboard/settings', icon: '⚙️' },
];

export default function DashboardLayout({ children }) {
  const user = useStore((state) => state.user);
  const logout = useStore((state) => state.logout);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`bg-white border-r border-gray-200 ${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300`}>
        <div className="p-4 flex items-center justify-between">
          {sidebarOpen && <span className="font-bold text-xl text-indigo-600">ContentForge</span>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1">
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>
        <nav className="mt-8">
          {SIDEBAR_ITEMS.map((item) => (
            <Link key={item.href} href={item.href}>
              <div className="flex items-center px-4 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 cursor-pointer">
                <span className="text-lg">{item.icon}</span>
                {sidebarOpen && <span className="ml-3 font-medium">{item.name}</span>}
              </div>
            </Link>
          ))}
        </nav>
        
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          {sidebarOpen && (
            <div className="text-sm">
              <p className="font-medium text-gray-900">{user?.name || 'User'}</p>
              <p className="text-gray-500 truncate">{user?.email}</p>
            </div>
          )}
          <button
            onClick={logout}
            className="mt-2 w-full text-left text-red-600 hover:text-red-700 text-sm font-medium"
          >
            {sidebarOpen ? 'Logout' : '🚪'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex items-center gap-4">
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Free Plan</span>
              <Link href="/dashboard/generate">
                <button className="btn-primary">+ Generate Content</button>
              </Link>
            </div>
          </div>
        </header>
        
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}
