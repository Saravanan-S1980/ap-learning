import { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { Share2, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';
import MobileShell from '../components/layout/MobileShell';
import { api } from '../services/api';

// ── Collapsible section ──────────────────────────────────────────────────────
function Section({ title, defaultOpen = false, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 min-h-[56px] text-left"
      >
        <span className="font-semibold text-slate-900">{title}</span>
        {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
      </button>
      {open && <div className="px-4 pb-4 border-t border-slate-100">{children}</div>}
    </div>
  );
}

// ── Sub-components for each section ─────────────────────────────────────────
function DietSection({ items }) {
  const immediate = items.filter((d) => d.phase === 'immediate');
  const phaseIn   = items.filter((d) => d.phase !== 'immediate');
  return (
    <div className="pt-3 flex flex-col gap-4">
      {immediate.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            Start Now
          </p>
          {immediate.map((d, i) => (
            <div key={i} className="mb-3">
              <p className="text-slate-800 font-medium">• {d.action}</p>
              {d.rationale && <p className="text-sm text-slate-500 ml-3">↳ {d.rationale}</p>}
            </div>
          ))}
        </div>
      )}
      {phaseIn.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            Phase In (2–4 weeks)
          </p>
          {phaseIn.map((d, i) => (
            <div key={i} className="mb-3">
              <p className="text-slate-800 font-medium">• {d.action}</p>
              {d.rationale && <p className="text-sm text-slate-500 ml-3">↳ {d.rationale}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SupplementSection({ items }) {
  return (
    <div className="pt-3 flex flex-col gap-3">
      {items.map((s, i) => (
        <div key={i} className="border border-slate-100 rounded-xl p-3">
          <p className="font-semibold text-slate-900">{s.name}</p>
          <p className="text-sm text-slate-600">{s.dose} · {s.timing} · {s.duration_weeks}w</p>
          {s.targets?.length > 0 && (
            <p className="text-xs text-blue-600 mt-1">Targets: {s.targets.join(', ')}</p>
          )}
          {s.notes && <p className="text-xs text-slate-500 mt-1">{s.notes}</p>}
        </div>
      ))}
    </div>
  );
}

function LifestyleSection({ items }) {
  return (
    <div className="pt-3 flex flex-col gap-3">
      {items.map((lc, i) => (
        <div key={i} className="mb-2">
          <p className="text-slate-800 font-medium">• {lc.action}
            <span className="text-slate-400 font-normal"> [{lc.frequency}]</span>
          </p>
          {lc.rationale && <p className="text-sm text-slate-500 ml-3">↳ {lc.rationale}</p>}
        </div>
      ))}
    </div>
  );
}

function RetestSection({ items }) {
  return (
    <div className="pt-3 flex flex-col gap-2">
      {items.map((r, i) => (
        <div key={i} className="flex justify-between items-baseline border-b border-slate-50 pb-2">
          <span className="text-slate-800 text-sm">{r.marker}</span>
          <span className="text-slate-500 text-xs shrink-0 ml-2">in {r.weeks_from_now}w — {r.reason}</span>
        </div>
      ))}
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function ProtocolPage() {
  const { id }       = useParams();
  const { state }    = useLocation();

  // Use protocol passed via navigation state first (avoids a round-trip),
  // then fall back to fetching from the API if page is loaded directly by URL.
  const [protocol, setProtocol] = useState(state?.protocol ?? null);
  const [loading,  setLoading]  = useState(!state?.protocol);
  const [error,    setError]    = useState(null);

  useEffect(() => {
    if (protocol || !id) return; // already have data
    setLoading(true);
    console.log('[ProtocolPage] fetching protocol', id);
    api.getProtocol(id)
      .then((p) => { setProtocol(p); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, [id]);

  const shareBtn = (
    <button className="min-h-[44px] px-4 bg-slate-100 rounded-xl flex items-center gap-2
      text-slate-700 font-medium text-sm">
      <Share2 size={16} />
      Share
    </button>
  );

  return (
    <MobileShell title="Your Protocol" backPath="/goals" headerRight={shareBtn}>
      <div className="flex flex-col gap-4 p-4">

        {/* Disclaimer */}
        <div className="bg-amber-50 border border-amber-200 rounded-2xl px-4 py-3">
          <p className="text-sm text-amber-800">
            {protocol?.disclaimer ??
              '⚕ This protocol is for informational purposes only and does not constitute medical advice. Consult your doctor before making changes.'}
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-500">
            <Loader2 size={36} className="animate-spin text-blue-500" />
            <p className="text-base">Loading your protocol…</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-2xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {/* Protocol sections */}
        {protocol && (
          <>
            <Section title="🥗 Diet Changes" defaultOpen>
              {protocol.diet_changes?.length > 0
                ? <DietSection items={protocol.diet_changes} />
                : <p className="text-slate-400 text-sm pt-3">No diet changes recommended.</p>}
            </Section>

            <Section title="💊 Supplements">
              {protocol.supplements?.length > 0
                ? <SupplementSection items={protocol.supplements} />
                : <p className="text-slate-400 text-sm pt-3">No supplements recommended.</p>}
            </Section>

            <Section title="🏃 Lifestyle">
              {protocol.lifestyle_changes?.length > 0
                ? <LifestyleSection items={protocol.lifestyle_changes} />
                : <p className="text-slate-400 text-sm pt-3">No lifestyle changes recommended.</p>}
            </Section>

            <Section title="📅 Retest Schedule">
              {protocol.retest_schedule?.length > 0
                ? <RetestSection items={protocol.retest_schedule} />
                : <p className="text-slate-400 text-sm pt-3">No retest schedule provided.</p>}
            </Section>

            {/* Backend warnings */}
            {protocol.warnings?.length > 0 && (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                  Warnings
                </p>
                {protocol.warnings.map((w, i) => (
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
