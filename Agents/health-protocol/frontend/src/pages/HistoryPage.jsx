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

function formatDate(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export default function HistoryPage() {
  const navigate = useNavigate();
  const [protocols, setProtocols] = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);

  useEffect(() => {
    api.getProtocols()
      .then((data) => { setProtocols(data); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, []);

  return (
    <MobileShell title="History">
      <div className="flex flex-col gap-4 p-4">

        {loading && (
          <div className="flex items-center justify-center py-16 gap-3 text-slate-500">
            <Loader2 size={28} className="animate-spin text-blue-500" />
            <span className="text-base">Loading history…</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-2xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {!loading && protocols.length === 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 px-4 py-12
            text-center text-slate-400 text-base">
            No reports yet — upload your first blood test on the home screen.
          </div>
        )}

        {protocols.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
            {protocols.map((p) => {
              const goalLabels = (p.goals ?? []).map((g) => GOAL_LABELS[g] ?? g);
              return (
                <button
                  key={p.id}
                  onClick={() => navigate(`/protocol/${p.id}`, {
                    state: { extractionId: p.extraction_id, backPath: '/history' },
                  })}
                  className="w-full flex items-center gap-3 px-4 min-h-[72px]
                    hover:bg-slate-50 active:bg-slate-100 transition-colors text-left"
                >
                  <FileText size={22} className="text-blue-500 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-slate-900 font-semibold text-base truncate">
                      {p.lab_name || 'Unknown Lab'}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {p.report_date || formatDate(p.created_at)}
                      {p.marker_count > 0 && ` · ${p.marker_count} markers`}
                    </p>
                    {goalLabels.length > 0 && (
                      <p className="text-xs text-blue-600 mt-0.5 truncate">
                        {goalLabels.join(', ')}
                      </p>
                    )}
                  </div>
                  <ChevronRight size={18} className="text-slate-300 shrink-0" />
                </button>
              );
            })}
          </div>
        )}
      </div>
    </MobileShell>
  );
}
