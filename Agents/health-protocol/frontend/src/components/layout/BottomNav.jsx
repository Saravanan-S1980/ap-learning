import { useLocation, useNavigate } from 'react-router-dom';
import { Camera, BarChart2, Settings } from 'lucide-react';

const TABS = [
  { path: '/',         label: 'Upload',   Icon: Camera },
  { path: '/history',  label: 'History',  Icon: BarChart2 },
  { path: '/settings', label: 'Settings', Icon: Settings },
];

export default function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 safe-bottom z-50">
      <div className="flex">
        {TABS.map(({ path, label, Icon }) => {
          const active = location.pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`flex-1 flex flex-col items-center justify-center min-h-[56px] gap-0.5 text-xs font-medium transition-colors
                ${active ? 'text-blue-600' : 'text-slate-500'}`}
            >
              <Icon size={22} strokeWidth={active ? 2.5 : 2} />
              <span>{label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
