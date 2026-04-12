import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';

const GOALS = [
  { id: 'cardiovascular_health', label: 'Heart Health',   emoji: '❤️' },
  { id: 'energy_vitality',       label: 'Energy',         emoji: '⚡' },
  { id: 'fat_loss',              label: 'Fat Loss',       emoji: '🏃' },
  { id: 'hormonal_balance',      label: 'Hormones',       emoji: '🧬' },
  { id: 'cognitive_performance', label: 'Brain Power',    emoji: '🧠' },
  { id: 'athletic_performance',  label: 'Athletic',       emoji: '💪' },
  { id: 'immune_function',       label: 'Immunity',       emoji: '🛡️' },
  { id: 'stress_resilience',     label: 'Stress',         emoji: '🧘' },
  { id: 'longevity',             label: 'Longevity',      emoji: '🕐' },
  { id: 'gut_health',            label: 'Gut Health',     emoji: '🌿' },
];

export default function GoalsPage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState([]);

  function toggle(id) {
    setSelected((prev) =>
      prev.includes(id)
        ? prev.filter((g) => g !== id)
        : prev.length < 3
          ? [...prev, id]
          : prev
    );
  }

  return (
    <MobileShell title="Your Goals" backPath="/review">
      <div className="flex flex-col gap-4 p-4">

        <p className="text-base text-slate-600">
          What do you want to improve? <strong>Pick up to 3.</strong>
        </p>

        <div className="grid grid-cols-2 gap-3">
          {GOALS.map(({ id, label, emoji }) => {
            const active = selected.includes(id);
            return (
              <button
                key={id}
                onClick={() => toggle(id)}
                className={`min-h-[72px] rounded-2xl border-2 flex flex-col items-center
                  justify-center gap-1 transition-colors text-sm font-semibold
                  ${active
                    ? 'border-blue-600 bg-blue-50 text-blue-700'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                  }`}
              >
                <span className="text-2xl">{emoji}</span>
                <span>{label}</span>
              </button>
            );
          })}
        </div>

        <button
          disabled={selected.length === 0}
          onClick={() => navigate('/protocol')}
          className="w-full min-h-[52px] bg-blue-600 text-white rounded-2xl
            font-semibold text-base hover:bg-blue-700 active:bg-blue-800
            disabled:opacity-40 disabled:pointer-events-none transition-colors shadow"
        >
          Generate Protocol →
        </button>
      </div>
    </MobileShell>
  );
}
