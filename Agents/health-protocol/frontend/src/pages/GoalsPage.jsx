import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Check } from 'lucide-react';
import MobileShell from '../components/layout/MobileShell';
import { api } from '../services/api';

const GOALS = [
  { id: 'cardiovascular_health', label: 'Heart Health',  emoji: '❤️' },
  { id: 'energy_vitality',       label: 'Energy',        emoji: '⚡' },
  { id: 'fat_loss',              label: 'Fat Loss',      emoji: '🏃' },
  { id: 'hormonal_balance',      label: 'Hormones',      emoji: '🧬' },
  { id: 'cognitive_performance', label: 'Brain Power',   emoji: '🧠' },
  { id: 'athletic_performance',  label: 'Athletic',      emoji: '💪' },
  { id: 'immune_function',       label: 'Immunity',      emoji: '🛡️' },
  { id: 'stress_resilience',     label: 'Stress',        emoji: '🧘' },
  { id: 'longevity',             label: 'Longevity',     emoji: '🕐' },
  { id: 'gut_health',            label: 'Gut Health',    emoji: '🌿' },
];

const STEPS = [
  { text: 'Reading your markers…',      icon: '🔬' },
  { text: 'Analysing patterns…',        icon: '📊' },
  { text: 'Matching to your goals…',   icon: '🎯' },
  { text: 'Crafting your protocol…',   icon: '✨' },
];

export default function GoalsPage() {
  const navigate     = useNavigate();
  const { state }    = useLocation();
  const markers      = state?.markers ?? [];
  const extractionId = state?.extractionId ?? '';

  const [selected,  setSelected]  = useState([]);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const [stepIndex, setStepIndex] = useState(0);

  /* Cycle through loading steps */
  useEffect(() => {
    if (!loading) { setStepIndex(0); return; }
    const t = setInterval(() => setStepIndex(i => (i + 1) % STEPS.length), 3500);
    return () => clearInterval(t);
  }, [loading]);

  function toggle(id) {
    setSelected(prev =>
      prev.includes(id)
        ? prev.filter(g => g !== id)
        : prev.length < 3 ? [...prev, id] : prev,
    );
  }

  async function handleGenerate() {
    if (!selected.length || !markers.length) return;
    setError(null);
    setLoading(true);
    try {
      const result = await api.analyze(markers, selected, extractionId);
      navigate(`/protocol/${result.protocol_id}`, {
        state: {
          protocol:    result.protocol,
          extractionId,
          backPath:    extractionId ? `/review/${extractionId}` : '/',
        },
      });
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  const backPath = extractionId ? `/review/${extractionId}` : '/';

  return (
    <MobileShell title="Your Goals" backPath={backPath}>

      {/* ── Full-screen loading overlay ──────────────────────────── */}
      {loading && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center px-8"
             style={{ backgroundColor: '#FFF9F5' }}>
          {/* Animated step icon */}
          <div key={`icon-${stepIndex}`} className="text-6xl mb-6 step-fade">
            {STEPS[stepIndex].icon}
          </div>

          {/* Cycling step text */}
          <div key={`text-${stepIndex}`} className="text-center mb-8 step-fade">
            <p className="font-heading font-bold text-xl text-charcoal mb-1">
              {STEPS[stepIndex].text}
            </p>
            <p className="text-sm text-muted">Claude is crafting your personalised plan</p>
          </div>

          {/* Step dots */}
          <div className="flex gap-2 mb-6">
            {STEPS.map((_, i) => (
              <div key={i} className="rounded-full transition-all duration-500"
                   style={{
                     width:   i === stepIndex ? 24 : 8,
                     height:  8,
                     background: i <= stepIndex ? '#FF6B6B' : '#E8DDD5',
                   }} />
            ))}
          </div>

          {/* Progress bar */}
          <div className="w-full max-w-xs rounded-full overflow-hidden"
               style={{ height: 4, background: '#E8DDD5' }}>
            <div className="h-full rounded-full transition-all duration-700"
                 style={{
                   width:      `${((stepIndex + 1) / STEPS.length) * 100}%`,
                   background: 'linear-gradient(90deg,#FF6B6B,#FF8E53)',
                 }} />
          </div>
        </div>
      )}

      <div className="flex flex-col gap-4 p-4 page-enter">

        <div>
          <h2 className="font-heading font-bold text-2xl text-charcoal tracking-tight">
            What matters most to you?
          </h2>
          <p className="text-muted text-sm mt-1">
            Pick up to 3 goals for your personalised protocol
          </p>
        </div>

        {markers.length === 0 && (
          <div className="rounded-2xl px-4 py-3 text-sm"
               style={{ background: 'rgba(244,162,97,.12)', color: '#2D3436',
                        border: '1px solid rgba(244,162,97,.3)' }}>
            No markers loaded — go back and upload a report first.
          </div>
        )}

        {error && (
          <div className="rounded-2xl px-4 py-3 text-sm"
               style={{ background: 'rgba(231,76,111,.1)', color: '#C0334E',
                        border: '1px solid rgba(231,76,111,.25)' }}>
            {error}
          </div>
        )}

        {/* Goal grid */}
        <div className="grid grid-cols-2 gap-3">
          {GOALS.map(({ id, label, emoji }) => {
            const active   = selected.includes(id);
            const maxed    = !active && selected.length >= 3;
            return (
              <button
                key={id}
                disabled={maxed}
                onClick={() => toggle(id)}
                className="relative rounded-2xl flex flex-col items-center justify-center
                           gap-2 transition-all duration-200"
                style={{
                  minHeight:   88,
                  padding:     '16px 12px',
                  background:  active
                    ? 'linear-gradient(135deg,#FF6B6B 0%,#FF8E53 100%)'
                    : '#fff',
                  boxShadow:   active
                    ? '0 6px 20px -4px rgba(255,107,107,.45)'
                    : 'var(--shadow-warm)',
                  border:      active ? 'none' : '1.5px solid #E8DDD5',
                  transform:   active ? 'scale(1.04)' : 'scale(1)',
                  opacity:     maxed ? .38 : 1,
                  cursor:      maxed ? 'not-allowed' : 'pointer',
                }}
              >
                {/* Selected checkmark badge */}
                {active && (
                  <div className="absolute top-2 right-2 w-5 h-5 rounded-full flex items-center
                                  justify-center" style={{ background: 'rgba(255,255,255,.3)' }}>
                    <Check size={12} color="white" strokeWidth={3} />
                  </div>
                )}
                <span style={{ fontSize: 32 }}>{emoji}</span>
                <span className="text-sm font-heading font-semibold leading-tight text-center"
                      style={{ color: active ? '#fff' : '#2D3436' }}>
                  {label}
                </span>
              </button>
            );
          })}
        </div>

        {selected.length > 0 && (
          <p className="text-center text-xs text-muted">
            {selected.length}/3 goals selected
            {selected.length === 3 && ' — maximum reached'}
          </p>
        )}

        <div className="pb-2">
          <button
            disabled={!selected.length || !markers.length}
            onClick={handleGenerate}
            className="btn-coral"
          >
            Generate My Protocol →
          </button>
        </div>
      </div>
    </MobileShell>
  );
}
