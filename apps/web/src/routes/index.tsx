import React from 'react';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: IndexComponent,
});

function IndexComponent() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-white">peleton.me</h1>
      <p className="mt-2 text-slate-400">
        National Showcase for Active Commuting, Open Data & AI-Assisted Engineering[cite: 1]
      </p>
    </div>
  );
}