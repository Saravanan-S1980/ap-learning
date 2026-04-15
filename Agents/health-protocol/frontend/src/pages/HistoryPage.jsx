import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';
import { FileText, Loader2, ChevronRight } from 'lucide-react';
import { api } from '../services/api';

const GOAL_LABELS = {
  cardiovascular_health: 'Heart Health',
  energy_vitality:       'Energy',
  fat_loss:              'Fat Loss',
  hormonal_balance:      'Hormones',
  cognitive_performance: 'Brain Power',
  athletic_performance:  'Athletic',
  immune_function:       'Immunity',
  stress_resilience:     'Stress',
  longevity:             'Longevity',
  gut_health:            'Gut Health',
};

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export default function HistoryPage() {
  const navigate = useNavigate();
  const [protocols, setProtocols] = useState(null); // null = loading
  const [error,     setError]     = useState(null);

  useEffect(() => {
    api.getProtocols()
      .then(setProtocols)
      .catch(err => { setError(err.message); setProtocols([]); });
  }, []);

  return (
    <MobileShell title="History">
      <div className="flex flex-col gap-4 p-4 page-enter">

        {protocols === null && (
          <div className="flex items-center justify-center py-20 gap-3 text-muted">
            <Loader2 size={26} className="animate-spin" style={{ color: '#FF6B6B' }} />
            <span className="text-base font-medium">Loading history…</span>
          </div>
        )}

        {error && (
          <div className="rounded-2xl px-4 py-3 text-sm"
               style={{ background: 'rgba(231,76,111,.1)', color: '#C0334E',
                        border: '1px solid rgba(231,76,111,.25)' }}>
            {error}
          </div>
        )}

        {protocols?.length === 0 && (
          <div className="rounded-2xl border border-warm-border px-4 py-16
                          text-center text-muted text-base" style={{ background: '#fff' }}>
            <p className="text-4xl mb-3">🩸</p>
            <p className="font-heading font-semibold text-charcoal mb-1">No reports yet</p>
            <p className="text-sm">Upload your first blood test on the home screen.</p>
          </div>
        )}

        {protocols?.length > 0 && (
          <>
            <p className="text-xs font-heading font-bold text-muted uppercase tracking-widest px-1">
              {protocols.length} Report{protocols.length !== 1 ? 's' : ''}
            </p>

            <div className="rounded-2xl overflow-hidden"
                 style={{ background: '#fff', boxShadow: 'var(--shadow-warm-md)' }}>
              {protocols.map((p, i) => {
                const goalLabels = (p.goals ?? []).map(g => GOAL_LABELS[g] ?? g);
                return (
                  <button
                    key={p.id}
                    onClick={() => navigate(`/protocol/${p.id}`, {
                      state: { extractionId: p.extraction_id, backPath: '/history' },
                    })}
                    className="w-full flex items-center gap-3 px-4 min-h-[76px]
                               transition-colors duration-150 text-left"
                    style={{
                      borderTop: i > 0 ? '1px solid #F5EFE9' : 'none',
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = '#FFF9F5'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    {/* Teal left accent */}
                    <div className="w-1 self-stretch rounded-full shrink-0"
                         style={{ background: 'linear-gradient(180deg,#2D6A6A,#3D8A8A)',
                                  minHeight: 44 }} />

                    <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                         style={{ background: 'rgba(45,106,106,.1)' }}>
                      <FileText size={18} style={{ color: '#2D6A6A' }} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="font-heading font-bold text-charcoal text-base truncate">
                        {p.lab_name || 'Unknown Lab'}
                      </p>
                      <p className="text-xs text-muted mt-0.5">
                        {p.report_date || formatDate(p.created_at)}
                        {p.marker_count > 0 && ` · ${p.marker_count} markers`}
                      </p>
                      {goalLabels.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {goalLabels.map((g, gi) => (
                            <span key={gi}
                                  className="text-xs px-2 py-0.5 rounded-full font-medium"
                                  style={{ background: 'rgba(255,107,107,.1)', color: '#FF6B6B' }}>
                              {g}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <ChevronRight size={16} style={{ color: '#C8BDB5' }} className="shrink-0" />
                  </button>
                );
              })}
            </div>
          </>
        )}
      </div>
    </MobileShell>
  );
}
