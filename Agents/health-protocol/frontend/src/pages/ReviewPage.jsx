import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';
import { AlertTriangle, Loader2, ChevronDown, ChevronRight, FlaskConical } from 'lucide-react';
import { api } from '../services/api';

/* ── Flag → visual config ─────────────────────────────────────────────────── */
const FLAG = {
  normal:        { border: '#6BBF7B', bg: 'rgba(107,191,123,.07)', badge: '#6BBF7B', label: 'Normal'   },
  low:           { border: '#F4A261', bg: 'rgba(244,162,97,.07)',  badge: '#F4A261', label: 'Low'      },
  high:          { border: '#F4A261', bg: 'rgba(244,162,97,.07)',  badge: '#F4A261', label: 'High'     },
  critical_low:  { border: '#E74C6F', bg: 'rgba(231,76,111,.07)', badge: '#E74C6F', label: 'Critical' },
  critical_high: { border: '#E74C6F', bg: 'rgba(231,76,111,.07)', badge: '#E74C6F', label: 'Critical' },
};

/* ── Range bar with gradient track + position dot ─────────────────────────── */
function RangeBar({ marker }) {
  const { value, reference_low: lo, reference_high: hi } = marker;

  if (value == null || lo == null || hi == null) {
    const c = (FLAG[marker.flag] || FLAG.normal).badge;
    return (
      <div className="h-2 rounded-full mt-2" style={{ background: '#F5EFE9' }}>
        <div className="h-full w-1/2 rounded-full" style={{ background: c }} />
      </div>
    );
  }

  const range   = hi - lo;
  const pad     = range * 0.6;
  const min     = lo - pad;
  const max     = hi + pad;
  const pct     = Math.max(2, Math.min(98, ((value - min) / (max - min)) * 100));

  return (
    <div className="relative h-2 rounded-full mt-2" style={{ background: '#F5EFE9' }}>
      {/* Gradient track: red → yellow → green → yellow → red */}
      <div className="absolute inset-0 rounded-full" style={{
        background: 'linear-gradient(to right,#E74C6F 0%,#F4A261 22%,#6BBF7B 38%,#6BBF7B 62%,#F4A261 78%,#E74C6F 100%)',
      }} />
      {/* Dot indicator */}
      <div className="absolute top-1/2 w-4 h-4 rounded-full bg-white border-2 border-charcoal"
           style={{
             left: `${pct}%`,
             transform: 'translate(-50%,-50%)',
             boxShadow: '0 1px 4px rgba(0,0,0,.25)',
           }} />
    </div>
  );
}

/* ── Single marker row with tap-to-expand ─────────────────────────────────── */
function MarkerRow({ marker }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = FLAG[marker.flag] ?? FLAG.normal;
  const val = marker.value != null
    ? `${marker.value} ${marker.unit}`
    : (marker.qualitative_value ?? '—');

  return (
    <div
      className="px-4 py-3 transition-colors duration-100"
      style={{
        borderLeft: `3px solid ${cfg.border}`,
        background: expanded ? cfg.bg : 'transparent',
        minHeight: 56,
      }}
    >
      {/* Top row: name + value + expand toggle */}
      <div className="flex items-center gap-2" onClick={() => setExpanded(v => !v)}
           style={{ cursor: 'pointer' }}>
        <div className="flex-1 min-w-0">
          <p className="font-heading font-semibold text-charcoal text-base leading-tight truncate">
            {marker.reported_name}
          </p>
        </div>
        <span className="text-base font-bold shrink-0" style={{ color: cfg.badge }}>
          {val}
        </span>
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full shrink-0"
              style={{ background: `${cfg.badge}20`, color: cfg.badge }}>
          {cfg.label}
        </span>
        {expanded
          ? <ChevronDown  size={14} style={{ color: '#8B7E74' }} className="shrink-0" />
          : <ChevronRight size={14} style={{ color: '#8B7E74' }} className="shrink-0" />}
      </div>

      {/* Range bar */}
      <RangeBar marker={marker} />

      {/* Expanded detail */}
      {expanded && (
        <div className="mt-2 space-y-1">
          {(marker.reference_low != null || marker.reference_high != null) && (
            <p className="text-xs text-muted">
              Reference: {marker.reference_low ?? '—'} – {marker.reference_high ?? '—'} {marker.unit}
            </p>
          )}
          {marker.category && (
            <p className="text-xs text-muted">Category: {marker.category}</p>
          )}
        </div>
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

/* ── Page ─────────────────────────────────────────────────────────────────── */
export default function ReviewPage() {
  const { id }    = useParams();
  const navigate  = useNavigate();
  const { state } = useLocation();

  const [extraction, setExtraction] = useState(state?.extraction ?? null);
  const [loading,    setLoading]    = useState(!state?.extraction);
  const [error,      setError]      = useState(null);

  useEffect(() => {
    if (!id) { navigate('/', { replace: true }); return; }
    if (extraction) return;
    setLoading(true);
    api.getExtraction(id)
      .then(d => { setExtraction(d); setLoading(false); })
      .catch(() => navigate('/', { replace: true }));
  }, [id]); // eslint-disable-line

  const markers  = extraction?.markers ?? [];
  const abnormal = markers.filter(m => m.flag !== 'normal');
  const grouped  = groupByCategory(markers);

  return (
    <MobileShell title="Review Report" backPath="/">
      <div className="flex flex-col gap-4 p-4 page-enter">

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-20 gap-3 text-muted">
            <Loader2 size={28} className="animate-spin" style={{ color: '#FF6B6B' }} />
            <span className="text-base font-medium">Loading report…</span>
          </div>
        )}

        {error && (
          <div className="rounded-2xl px-4 py-3 text-sm"
               style={{ background: 'rgba(231,76,111,.1)', color: '#C0334E' }}>
            {error}
          </div>
        )}

        {extraction && (
          <>
            {/* Teal lab info banner */}
            <div className="rounded-2xl px-5 py-4 text-white"
                 style={{ background: 'linear-gradient(135deg,#2D6A6A 0%,#3D8A8A 100%)',
                          boxShadow: '0 4px 14px -2px rgba(45,106,106,.35)' }}>
              <div className="flex items-center gap-2 mb-1">
                <FlaskConical size={16} opacity={0.8} />
                <span className="text-sm font-medium" style={{ opacity: .8 }}>Lab Report</span>
              </div>
              <p className="font-heading font-bold text-xl leading-tight">
                {extraction.lab_name ?? 'Unknown Lab'}
              </p>
              <p className="text-sm mt-0.5" style={{ opacity: .8 }}>
                {extraction.report_date ?? '—'}
              </p>
            </div>

            {/* Alert banner */}
            {abnormal.length > 0 && (
              <div className="rounded-2xl px-4 py-3 flex items-center gap-3"
                   style={{ background: 'linear-gradient(135deg,#FF6B6B 0%,#FF8E53 100%)',
                            boxShadow: '0 4px 14px -2px rgba(255,107,107,.35)' }}>
                <AlertTriangle size={20} color="white" className="pulse-icon shrink-0" />
                <p className="text-white font-heading font-semibold text-sm">
                  {abnormal.length} marker{abnormal.length !== 1 ? 's' : ''} need{abnormal.length === 1 ? 's' : ''} attention
                </p>
              </div>
            )}

            {/* Marker categories */}
            {markers.length === 0 ? (
              <div className="rounded-2xl border border-warm-border px-4 py-8
                              text-center text-muted text-base" style={{ background: '#fff' }}>
                No markers found in this report.
              </div>
            ) : (
              Object.entries(grouped).map(([cat, mks]) => (
                <div key={cat} className="rounded-2xl overflow-hidden"
                     style={{ background: '#fff', boxShadow: 'var(--shadow-warm-md)' }}>
                  {/* Category header — teal */}
                  <div className="px-4 py-2.5 flex items-center gap-2"
                       style={{ borderBottom: '1px solid #F5EFE9',
                                borderLeft: '3px solid #2D6A6A',
                                background: 'rgba(45,106,106,.04)' }}>
                    <p className="text-xs font-heading font-bold uppercase tracking-widest"
                       style={{ color: '#2D6A6A' }}>
                      {cat}
                    </p>
                    <span className="text-xs text-muted ml-auto">{mks.length} markers</span>
                  </div>
                  <div className="divide-y" style={{ '--tw-divide-opacity': 1, borderColor: '#F5EFE9' }}>
                    {mks.map((m, i) => (
                      <div key={i} style={{ borderTop: i > 0 ? '1px solid #F5EFE9' : 'none' }}>
                        <MarkerRow marker={m} />
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}

            {/* Warnings */}
            {extraction.warnings?.length > 0 && (
              <div className="rounded-2xl px-4 py-3"
                   style={{ background: 'rgba(244,162,97,.1)', border: '1px solid rgba(244,162,97,.3)' }}>
                <p className="text-xs font-heading font-bold uppercase tracking-widest text-warm-amber mb-1">
                  Parser warnings
                </p>
                {extraction.warnings.map((w, i) => (
                  <p key={i} className="text-xs text-muted">{w}</p>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Sticky CTA */}
      {extraction && markers.length > 0 && (
        <div className="fixed bottom-[56px] left-0 right-0 p-3 z-30"
             style={{ background: 'linear-gradient(to top,#FFF9F5 70%,transparent)' }}>
          <button
            onClick={() => navigate('/goals', { state: { markers, extractionId: id } })}
            className="btn-coral"
          >
            Continue to Goals →
          </button>
        </div>
      )}
    </MobileShell>
  );
}
