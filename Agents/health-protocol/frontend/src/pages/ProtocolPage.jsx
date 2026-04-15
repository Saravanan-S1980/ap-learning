import { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { Share2, ChevronDown, ChevronRight, Loader2,
         Check, Clock, Info, Activity, Leaf, Download } from 'lucide-react';
import MobileShell from '../components/layout/MobileShell';
import { api } from '../services/api';

/* ── Collapsible section card ──────────────────────────────────────────────── */
function Section({ title, topColor, defaultOpen = false, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-2xl overflow-hidden"
         style={{ background: '#fff', boxShadow: 'var(--shadow-warm-md)' }}>
      {/* Gradient top accent bar */}
      <div style={{ height: 3, background: topColor }} />
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 min-h-[56px] text-left
                   transition-colors duration-150"
        style={{ background: open ? 'rgba(0,0,0,.015)' : 'transparent' }}
      >
        <span className="font-heading font-bold text-charcoal text-base">{title}</span>
        {open
          ? <ChevronDown  size={18} style={{ color: '#8B7E74' }} />
          : <ChevronRight size={18} style={{ color: '#8B7E74' }} />}
      </button>
      {open && (
        <div className="px-4 pb-4" style={{ borderTop: '1px solid #F5EFE9' }}>
          {children}
        </div>
      )}
    </div>
  );
}

/* ── Diet section ──────────────────────────────────────────────────────────── */
function DietItem({ item }) {
  const [expanded, setExpanded] = useState(false);
  const isNow = item.phase === 'immediate';
  return (
    <div className="rounded-xl mb-2 overflow-hidden"
         style={{
           borderLeft: `3px solid ${isNow ? '#6BBF7B' : '#F4A261'}`,
           background: isNow ? 'rgba(107,191,123,.06)' : 'rgba(244,162,97,.06)',
         }}>
      <div className="flex items-start gap-2 p-3 cursor-pointer"
           onClick={() => item.rationale && setExpanded(v => !v)}>
        {isNow
          ? <Check size={15} className="mt-0.5 shrink-0" style={{ color: '#6BBF7B' }} />
          : <Clock size={15} className="mt-0.5 shrink-0" style={{ color: '#F4A261' }} />}
        <p className="flex-1 font-semibold text-charcoal text-sm leading-snug">{item.action}</p>
        {item.rationale && (
          <Info size={13} className="mt-0.5 shrink-0" style={{ color: '#8B7E74' }} />
        )}
      </div>
      {expanded && item.rationale && (
        <p className="text-xs text-muted px-3 pb-3 leading-relaxed" style={{ paddingLeft: 32 }}>
          {item.rationale}
        </p>
      )}
    </div>
  );
}

function DietSection({ items }) {
  const now     = items.filter(d => d.phase === 'immediate');
  const phaseIn = items.filter(d => d.phase !== 'immediate');
  return (
    <div className="pt-3 flex flex-col gap-0">
      {now.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-heading font-bold uppercase tracking-widest mb-2"
             style={{ color: '#6BBF7B' }}>
            Start Now
          </p>
          {now.map((d, i) => <DietItem key={i} item={d} />)}
        </div>
      )}
      {phaseIn.length > 0 && (
        <div>
          <p className="text-xs font-heading font-bold uppercase tracking-widest mb-2"
             style={{ color: '#F4A261' }}>
            Phase In (2–4 weeks)
          </p>
          {phaseIn.map((d, i) => <DietItem key={i} item={d} />)}
        </div>
      )}
    </div>
  );
}

/* ── Supplements section ───────────────────────────────────────────────────── */
function Pill({ label, color }) {
  return (
    <span className="text-xs font-semibold px-2.5 py-1 rounded-full"
          style={{ background: `${color}18`, color }}>
      {label}
    </span>
  );
}

function SupplementCard({ supp, idx }) {
  return (
    <div className="rounded-xl p-3.5 mb-2"
         style={{
           background: idx % 2 === 0 ? '#fff' : '#FFF9F5',
           border: '1px solid #F0E8E0',
         }}>
      <div className="flex justify-between items-start mb-2">
        <p className="font-heading font-bold text-charcoal text-base">{supp.name}</p>
      </div>
      <div className="flex flex-wrap gap-1.5 mb-2">
        <Pill label={supp.dose}                        color="#FF6B6B" />
        <Pill label={supp.timing}                      color="#6BBF7B" />
        <Pill label={`${supp.duration_weeks} weeks`}   color="#F4A261" />
      </div>
      {supp.targets?.length > 0 && (
        <p className="text-xs font-medium" style={{ color: '#2D6A6A' }}>
          Targets: {supp.targets.join(', ')}
        </p>
      )}
      {supp.notes && (
        <p className="text-xs text-muted mt-1 leading-relaxed">{supp.notes}</p>
      )}
    </div>
  );
}

/* ── Lifestyle section ─────────────────────────────────────────────────────── */
function LifestyleSection({ items }) {
  return (
    <div className="pt-3 flex flex-col gap-2">
      {items.map((lc, i) => (
        <div key={i} className="flex items-start gap-3 rounded-xl p-3"
             style={{ background: 'rgba(45,106,106,.05)', borderLeft: '3px solid #2D6A6A' }}>
          <Leaf size={15} className="mt-0.5 shrink-0" style={{ color: '#2D6A6A' }} />
          <div className="flex-1">
            <p className="font-semibold text-charcoal text-sm leading-snug">
              {lc.action}
              {lc.frequency && (
                <span className="font-normal text-muted"> [{lc.frequency}]</span>
              )}
            </p>
            {lc.rationale && (
              <p className="text-xs text-muted mt-1 leading-relaxed">{lc.rationale}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ── Retest timeline ───────────────────────────────────────────────────────── */
function RetestSection({ items }) {
  return (
    <div className="pt-3 relative">
      {/* Vertical connector line */}
      <div className="absolute rounded-full"
           style={{ left: 19, top: 24, bottom: 8, width: 2, background: 'rgba(244,162,97,.3)' }} />
      {items.map((r, i) => (
        <div key={i} className="relative flex gap-4 pb-5" style={{ paddingLeft: 44 }}>
          {/* Timeline dot */}
          <div className="absolute rounded-full border-2 border-white"
               style={{
                 left: 12, top: 4,
                 width: 14, height: 14,
                 background: '#F4A261',
                 boxShadow: '0 0 0 3px rgba(244,162,97,.2)',
               }} />
          <div className="flex-1">
            <p className="text-xs font-heading font-bold uppercase tracking-wide"
               style={{ color: '#E9A23B' }}>
              Week {r.weeks_from_now}
            </p>
            <p className="font-semibold text-charcoal text-sm mt-0.5">{r.marker}</p>
            <p className="text-xs text-muted mt-0.5 leading-relaxed">{r.reason}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ── Main page ─────────────────────────────────────────────────────────────── */
export default function ProtocolPage() {
  const { id }    = useParams();
  const { state } = useLocation();

  const backPath = state?.backPath
    ?? (state?.extractionId ? `/review/${state.extractionId}` : '/');

  const [protocol, setProtocol] = useState(state?.protocol ?? null);
  const [loading,  setLoading]  = useState(!state?.protocol);
  const [error,    setError]    = useState(null);
  const [disclaimerOpen, setDisclaimerOpen] = useState(false);

  useEffect(() => {
    if (protocol || !id) return;
    setLoading(true);
    api.getProtocol(id)
      .then(p => { setProtocol(p); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [id]); // eslint-disable-line

  const shareBtn = (
    <button className="flex items-center gap-1.5 rounded-xl px-3 min-h-[44px] text-sm font-semibold
                       transition-colors duration-150"
            style={{ border: '1.5px solid #2D6A6A', color: '#2D6A6A', background: 'transparent' }}>
      <Share2 size={15} />
      Share
    </button>
  );

  return (
    <MobileShell title="Your Protocol" backPath={backPath} headerRight={shareBtn}>
      <div className="flex flex-col gap-3 p-4 page-enter">

        {/* Disclaimer — collapsible */}
        <div className="rounded-2xl overflow-hidden"
             style={{ background: 'rgba(233,162,59,.1)', border: '1px solid rgba(233,162,59,.3)' }}>
          <button
            onClick={() => setDisclaimerOpen(v => !v)}
            className="w-full flex items-center justify-between px-4 min-h-[44px] text-left"
          >
            <span className="text-xs font-heading font-bold uppercase tracking-widest"
                  style={{ color: '#E9A23B' }}>
              ⚕ Medical Disclaimer
            </span>
            {disclaimerOpen
              ? <ChevronDown  size={14} style={{ color: '#E9A23B' }} />
              : <ChevronRight size={14} style={{ color: '#E9A23B' }} />}
          </button>
          {disclaimerOpen && (
            <p className="text-xs text-muted px-4 pb-3 leading-relaxed">
              {protocol?.disclaimer ??
                'This protocol is for informational purposes only and does not constitute medical advice. Always consult your doctor before making changes to your diet, supplements, or lifestyle.'}
            </p>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 gap-3 text-muted">
            <Activity size={36} className="animate-spin" style={{ color: '#FF6B6B' }} />
            <p className="text-base font-medium">Loading your protocol…</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-2xl px-4 py-3 text-sm"
               style={{ background: 'rgba(231,76,111,.1)', color: '#C0334E',
                        border: '1px solid rgba(231,76,111,.25)' }}>
            {error}
          </div>
        )}

        {/* Protocol sections */}
        {protocol && (
          <>
            <Section
              title="🥗 Diet Changes"
              topColor="linear-gradient(90deg,#6BBF7B,#52A863)"
              defaultOpen
            >
              {protocol.diet_changes?.length > 0
                ? <DietSection items={protocol.diet_changes} />
                : <p className="text-sm text-muted pt-3">No diet changes recommended.</p>}
            </Section>

            <Section
              title="💊 Supplements"
              topColor="linear-gradient(90deg,#FF6B6B,#FF8E53)"
            >
              {protocol.supplements?.length > 0
                ? (
                  <div className="pt-3">
                    {protocol.supplements.map((s, i) => (
                      <SupplementCard key={i} supp={s} idx={i} />
                    ))}
                  </div>
                )
                : <p className="text-sm text-muted pt-3">No supplements recommended.</p>}
            </Section>

            <Section
              title="🏃 Lifestyle"
              topColor="linear-gradient(90deg,#2D6A6A,#3D8A8A)"
            >
              {protocol.lifestyle_changes?.length > 0
                ? <LifestyleSection items={protocol.lifestyle_changes} />
                : <p className="text-sm text-muted pt-3">No lifestyle changes recommended.</p>}
            </Section>

            <Section
              title="📅 Retest Schedule"
              topColor="linear-gradient(90deg,#F4A261,#E9A23B)"
            >
              {protocol.retest_schedule?.length > 0
                ? <RetestSection items={protocol.retest_schedule} />
                : <p className="text-sm text-muted pt-3">No retest schedule provided.</p>}
            </Section>

            {/* Backend warnings */}
            {protocol.warnings?.length > 0 && (
              <div className="rounded-2xl px-4 py-3"
                   style={{ background: '#F5EFE9', border: '1px solid #E8DDD5' }}>
                <p className="text-xs font-heading font-bold uppercase tracking-widest text-muted mb-1">
                  Warnings
                </p>
                {protocol.warnings.map((w, i) => (
                  <p key={i} className="text-xs text-muted">{w}</p>
                ))}
              </div>
            )}

            {/* Bottom actions */}
            <div className="flex gap-3 pt-1 pb-2">
              <button className="btn-outline flex-1"
                      style={{ minHeight: 48, fontSize: '0.875rem' }}>
                <Download size={16} />
                Save as PDF
              </button>
              <button className="btn-outline flex-1"
                      style={{ minHeight: 48, fontSize: '0.875rem' }}>
                <Share2 size={16} />
                Share with Doctor
              </button>
            </div>
          </>
        )}
      </div>
    </MobileShell>
  );
}
