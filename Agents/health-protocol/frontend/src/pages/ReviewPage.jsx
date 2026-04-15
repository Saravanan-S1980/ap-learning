import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { api } from '../services/api';

const FLAG_STYLES = {
  normal:        { bar: 'bg-green-400',  text: 'text-green-700',  label: 'Normal'   },
  low:           { bar: 'bg-yellow-400', text: 'text-yellow-700', label: 'Low'      },
  high:          { bar: 'bg-orange-400', text: 'text-orange-700', label: 'High'     },
  critical_low:  { bar: 'bg-red-500',    text: 'text-red-700',    label: 'Critical' },
  critical_high: { bar: 'bg-red-500',    text: 'text-red-700',    label: 'Critical' },
};

function MarkerRow({ marker }) {
  const style = FLAG_STYLES[marker.flag] ?? FLAG_STYLES.normal;
  const val   = marker.value != null
    ? `${marker.value} ${marker.unit}`
    : marker.qualitative_value ?? '—';

  return (
    <div className="px-4 py-3 min-h-[56px]">
      <div className="flex justify-between items-baseline">
        <span className="font-medium text-slate-800 text-base">{marker.reported_name}</span>
        <span className={`text-sm font-semibold ${style.text}`}>{val}</span>
      </div>
      <div className="flex items-center gap-2 mt-1">
        <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className={`h-full w-1/2 ${style.bar} rounded-full`} />
        </div>
        <span className={`text-xs font-medium ${style.text}`}>{style.label}</span>
      </div>
      {(marker.reference_low != null || marker.reference_high != null) && (
        <p className="text-xs text-slate-400 mt-0.5">
          Ref: {marker.reference_low ?? '—'} – {marker.reference_high ?? '—'} {marker.unit}
        </p>
      )}
    </div>
  );
}

function groupByCategory(markers) {
  const groups = {};
  for (const m of markers) {
    const cat = m.category ?? 'Other';
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(m);
  }
  return groups;
}

export default function ReviewPage() {
  const { id }     = useParams();
  const navigate   = useNavigate();
  const { state }  = useLocation();

  // Use state passed from UploadPage if available (avoids a round-trip)
  const [extraction, setExtraction] = useState(state?.extraction ?? null);
  const [loading,    setLoading]    = useState(!state?.extraction);
  const [error,      setError]      = useState(null);

  useEffect(() => {
    if (!id) {
      navigate('/', { replace: true });
      return;
    }
    if (extraction) return; // already have data from navigation state

    setLoading(true);
    api.getExtraction(id)
      .then((data) => { setExtraction(data); setLoading(false); })
      .catch(() => { navigate('/', { replace: true }); });
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  const markers  = extraction?.markers ?? [];
  const abnormal = markers.filter((m) => m.flag !== 'normal');
  const grouped  = groupByCategory(markers);

  console.log('[ReviewPage] extraction_id:', id, 'markers:', markers.length);

  function handleContinue() {
    navigate('/goals', { state: { markers, extractionId: id } });
  }

  return (
    <MobileShell title="Review Report" backPath="/">
      <div className="flex flex-col gap-4 p-4">

        {/* Loading state */}
        {loading && (
          <div className="flex items-center justify-center py-16 gap-3 text-slate-500">
            <Loader2 size={28} className="animate-spin text-blue-500" />
            <span className="text-base">Loading report…</span>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-2xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {extraction && (
          <>
            {/* Report meta */}
            <div className="bg-white rounded-2xl border border-slate-200 px-4 py-3">
              <p className="text-sm text-slate-500">Lab</p>
              <p className="font-semibold text-slate-900">{extraction.lab_name ?? '—'}</p>
              <p className="text-sm text-slate-500 mt-1">Date</p>
              <p className="font-semibold text-slate-900">{extraction.report_date ?? '—'}</p>
            </div>

            {/* Alert banner */}
            {abnormal.length > 0 && (
              <div className="bg-amber-50 border border-amber-300 rounded-2xl px-4 py-3
                flex items-center gap-3">
                <AlertTriangle size={20} className="text-amber-500 shrink-0" />
                <p className="text-amber-800 text-sm font-medium">
                  {abnormal.length} marker{abnormal.length > 1 ? 's' : ''} outside reference range
                </p>
              </div>
            )}

            {/* Marker list grouped by category */}
            {markers.length === 0 ? (
              <div className="bg-white rounded-2xl border border-slate-200 px-4 py-8
                text-slate-400 text-base text-center">
                No markers found in this report.
              </div>
            ) : (
              Object.entries(grouped).map(([category, mks]) => (
                <div key={category} className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
                  <div className="px-4 py-2 bg-slate-50 border-b border-slate-100">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      {category}
                    </p>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {mks.map((m, i) => <MarkerRow key={i} marker={m} />)}
                  </div>
                </div>
              ))
            )}

            {/* CTA */}
            <button
              onClick={handleContinue}
              disabled={markers.length === 0}
              className="w-full min-h-[52px] bg-blue-600 text-white rounded-2xl
                font-semibold text-base hover:bg-blue-700 active:bg-blue-800
                disabled:opacity-40 disabled:pointer-events-none transition-colors shadow"
            >
              Continue to Goals →
            </button>

            {/* Extraction warnings */}
            {extraction.warnings?.length > 0 && (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                  Parser warnings
                </p>
                {extraction.warnings.map((w, i) => (
                  <p key={i} className="text-xs text-slate-500">{w}</p>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </MobileShell>
  );
}
