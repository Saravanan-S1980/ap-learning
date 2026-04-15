/**
 * MobileShell — page wrapper with:
 *   - Safe-area-aware sticky header
 *   - Scrollable content area
 *   - Fixed bottom navigation
 *
 * Props:
 *   title       — header title
 *   backPath    — show back arrow pointing here
 *   headerRight — JSX in the right header slot
 *   brand       — true → gradient coral text + Heart icon (home screen)
 *   children    — page content
 */
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Heart } from 'lucide-react';
import BottomNav from './BottomNav';

export default function MobileShell({ title, backPath, headerRight, brand = false, children }) {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col min-h-dvh" style={{ backgroundColor: '#FFF9F5' }}>

      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 bg-white border-b border-warm-border safe-top"
              style={{ boxShadow: '0 1px 6px rgba(45,52,54,.06)' }}>
        <div className="flex items-center min-h-[56px] px-4 gap-3">

          {backPath && (
            <button
              onClick={() => navigate(backPath)}
              className="min-h-[48px] min-w-[48px] flex items-center justify-center -ml-2"
              style={{ color: '#2D6A6A' }}
              aria-label="Go back"
            >
              <ChevronLeft size={24} strokeWidth={2.5} />
            </button>
          )}

          {brand ? (
            <div className="flex items-center gap-2 flex-1">
              <div className="w-7 h-7 rounded-lg gradient-coral flex items-center justify-center shrink-0">
                <Heart size={14} fill="white" color="white" />
              </div>
              <h1 className="text-xl font-heading font-bold gradient-text-coral tracking-tight">
                {title}
              </h1>
            </div>
          ) : (
            <h1 className="flex-1 text-lg font-heading font-bold text-charcoal tracking-tight truncate">
              {title}
            </h1>
          )}

          {headerRight && (
            <div className="flex items-center">{headerRight}</div>
          )}
        </div>
      </header>

      {/* ── Scrollable content ───────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto pb-[84px]">
        {children}
      </main>

      {/* ── Bottom nav ───────────────────────────────────────────── */}
      <BottomNav />
    </div>
  );
}
