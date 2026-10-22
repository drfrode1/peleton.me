import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/effects')({
  component: EffectsComponent,
});

function EffectsComponent() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-white">Active Commuting Effects</h1>
      <p className="mt-2 text-slate-400">
        Translating bike telemetry into health, traffic reduction, and ESG impact metrics.
      </p>
    </div>
  );
}
