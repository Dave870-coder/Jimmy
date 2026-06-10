'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + '/');

  return (
    <nav className="bg-slate-900 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 text-xl font-bold text-white hover:text-blue-400 transition-colors">
              <span>🤖</span>
              <span>Jimmy</span>
            </Link>
            
            <div className="flex gap-4">
              <Link
                href="/"
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  isActive('/') && !isActive('/chat')
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                📊 Dashboard
              </Link>
              <Link
                href="/chat"
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  isActive('/chat')
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                💬 Chat with Bot
              </Link>
            </div>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span className="text-slate-400">Online</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
