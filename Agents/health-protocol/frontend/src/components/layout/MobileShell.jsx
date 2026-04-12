/**
 * MobileShell — wraps every page with:
 *  - Safe-area top header (title bar)
 *  - Scrollable content area
 *  - Fixed bottom navigation
 *
 * Props:
 *   title      — page title shown in header bar
 *   backPath   — if provided, shows a back arrow navigating to this path
 *   headerRight — optional JSX to render in the header's right slot
 *   children   — page content
 */
import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import BottomNav from './BottomNav';

export default function MobileShell({ title, backPath, headerRight, children }) {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col min-h-dvh bg-slate-100">
      {/* ── Header ───────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 safe-top">
        <div className="flex items-center min-h-[56px] px-4 gap-3">
          {backPath && (
            <button
              onClick={() => navigate(backPath)}
              className="min-h-[44px] min-w-[44px] flex items-center justify-center -ml-2 text-slate-600"
              aria-label="Go back"
            >
              <ChevronLeft size={24} />
            </button>
          )}
          <h1 className="flex-1 text-lg font-semibold text-slate-900 truncate">
            {title}
          </h1>
          {headerRight && (
            <div className="flex items-center">{headerRight}</div>
          )}
        </div>
      </header>

      {/* ── Scrollable content ───────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto pb-[72px]">
        {/* pb-[72px] reserves space below the fixed bottom nav */}
        {children}
      </main>

      {/* ── Bottom nav ───────────────────────────────────────────── */}
      <BottomNav />
    </div>
  );
}
