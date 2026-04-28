'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { signOut, useSession } from 'next-auth/react';

const NAV = [
  { name: 'Dashboard', href: '/dashboard', icon: '📊' },
  { name: 'Brands', href: '/dashboard/brands', icon: '🏢' },
  { name: 'Generate', href: '/dashboard/generate', icon: '✨' },
  { name: 'Content', href: '/dashboard/content', icon: '📝' },
  { name: 'Analytics', href: '/dashboard/analytics', icon: '📈' },
  { name: 'Settings', href: '/dashboard/settings', icon: '⚙️' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { data: session } = useSession();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 font-bold text-xl text-indigo-600">ContentForge</div>
        <nav className="flex-1 mt-4">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href}>
              <div className={`flex items-center px-4 py-3 cursor-pointer ${
                pathname === item.href ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50'
              }`}>
                <span className="text-lg">{item.icon}</span>
                <span className="ml-3 font-medium">{item.name}</span>
              </div>
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-200">
          <p className="text-sm font-medium truncate">{session?.user?.name || session?.user?.email || 'User'}</p>
          <button
            onClick={() => signOut({ callbackUrl: '/login' })}
            className="mt-2 w-full text-left text-red-600 hover:text-red-700 text-sm font-medium"
          >
            Logout
          </button>
        </div>
      </aside>

      <div className="flex-1 overflow-auto">
        <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Free Plan</span>
            <Link href="/dashboard/generate">
              <button className="btn-primary">+ Generate Content</button>
            </Link>
          </div>
        </header>
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}
