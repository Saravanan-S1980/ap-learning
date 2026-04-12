import { useState } from 'react';
import { Share2, ChevronDown, ChevronRight } from 'lucide-react';
import MobileShell from '../components/layout/MobileShell';

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
      {open && (
        <div className="px-4 pb-4 border-t border-slate-100">{children}</div>
      )}
    </div>
  );
}

export default function ProtocolPage() {
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
            ⚕ This protocol is for informational purposes only and does not
            constitute medical advice. Consult your doctor before making changes.
          </p>
        </div>

        <Section title="🥗 Diet Changes" defaultOpen>
          <p className="text-slate-400 text-base pt-3">
            Run analysis to see your diet plan.
          </p>
        </Section>

        <Section title="💊 Supplements">
          <p className="text-slate-400 text-base pt-3">
            Run analysis to see supplement recommendations.
          </p>
        </Section>

        <Section title="🏃 Lifestyle">
          <p className="text-slate-400 text-base pt-3">
            Run analysis to see lifestyle changes.
          </p>
        </Section>

        <Section title="📅 Retest Schedule">
          <p className="text-slate-400 text-base pt-3">
            Run analysis to see when to retest.
          </p>
        </Section>

      </div>
    </MobileShell>
  );
}
