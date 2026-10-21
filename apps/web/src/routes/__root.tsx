import React from 'react';
import { createRootRoute, Link, Outlet } from '@tanstack/react-router';
import { Bike } from 'lucide-react';

export const Route = createRootRoute({
  component: () => (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg text-emerald-400">
          <Bike className="w-5 h-5" /> peleton.me
        </Link>
        <nav className="flex gap-6 text-sm font-medium text-slate-400">
          <Link to="/" activeProps={{ className: 'text-white' }}>Dashboard</Link>
          <Link to="/effects" activeProps={{ className: 'text-white' }}>Effects</Link>
        </nav>
      </header>
      <main className="flex-1"><Outlet /></main>
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-600">
        Hosted by Tour of Norway · 100% Serverless Lakehouse Architecture[cite: 1, 2]
      </footer>
    </div>
  ),
});