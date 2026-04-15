import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import MobileShell from '../components/layout/MobileShell';
import { api } from '../services/api';

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
  const navigate     = useNavigate();
  const { state }    = useLocation();
  const markers      = state?.markers ?? [];
  const extractionId = state?.extractionId ?? '';

  const [selected, setSelected] = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);

  console.log('[GoalsPage] markers:', markers.length, 'extractionId:', extractionId);

  function toggle(id) {
    setSelected((prev) =>
      prev.includes(id)
        ? prev.filter((g) => g !== id)
        : prev.length < 3
          ? [...prev, id]
          : prev
    );
  }

  async function handleGenerate() {
    if (selected.length === 0 || markers.length === 0) return;

    setError(null);
    setLoading(true);
    console.log('[GoalsPage] calling /api/analyze, goals:', selected);

    try {
      const result = await api.analyze(markers, selected, extractionId);
      console.log('[GoalsPage] analyze response — protocol_id:', result.protocol_id);
      navigate(`/protocol/${result.protocol_id}`, {
        state: {
          protocol: result.protocol,
          extractionId,
          backPath: extractionId ? `/review/${extractionId}` : '/',
        },
      });
    } catch (err) {
      console.error('[GoalsPage] analyze error:', err);
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  const backPath = extractionId ? `/review/${extractionId}` : '/';

  return (
    <MobileShell title="Your Goals" backPath={backPath}>
      <div className="flex flex-col gap-4 p-4">

        <p className="text-base text-slate-600">
          What do you want to improve? <strong>Pick up to 3.</strong>
        </p>

        {markers.length === 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl px-4 py-3 text-sm text-amber-800">
            No markers loaded — go back and upload a report first.
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-2xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          {GOALS.map(({ id, label, emoji }) => {
            const active = selected.includes(id);
            return (
              <button
                key={id}
                disabled={loading}
                onClick={() => toggle(id)}
                className={`min-h-[72px] rounded-2xl border-2 flex flex-col items-center
                  justify-center gap-1 transition-colors text-sm font-semibold
                  disabled:opacity-50
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
          disabled={selected.length === 0 || markers.length === 0 || loading}
          onClick={handleGenerate}
          className="w-full min-h-[52px] bg-blue-600 text-white rounded-2xl
            font-semibold text-base hover:bg-blue-700 active:bg-blue-800
            disabled:opacity-40 disabled:pointer-events-none transition-colors shadow
            flex items-center justify-center gap-2"
        >
          {loading && <Loader2 size={20} className="animate-spin" />}
          {loading ? 'Generating protocol…' : 'Generate Protocol →'}
        </button>

        {loading && (
          <p className="text-center text-sm text-slate-500">
            Claude is analysing your markers — this takes about 15 seconds.
          </p>
        )}
      </div>
    </MobileShell>
  );
}
