import { useLocation, useNavigate } from 'react-router-dom';
import { Camera, BarChart2, Settings } from 'lucide-react';

const TABS = [
  { path: '/',        label: 'Upload',  Icon: Camera   },
  { path: '/history', label: 'History', Icon: BarChart2 },
  { path: '/settings',label: 'Settings',Icon: Settings  },
];

export default function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white safe-bottom"
         style={{ borderTop: '1px solid #E8DDD5', boxShadow: '0 -2px 12px rgba(45,52,54,.06)' }}>
      <div className="flex">
        {TABS.map(({ path, label, Icon }) => {
          const active = location.pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="flex-1 flex flex-col items-center justify-center min-h-[56px] gap-0.5
                         text-xs font-medium transition-colors duration-150"
              style={{ color: active ? '#FF6B6B' : '#8B7E74' }}
            >
              <Icon
                size={22}
                strokeWidth={active ? 2.5 : 1.8}
                fill={active ? 'rgba(255,107,107,.15)' : 'none'}
              />
              <span style={{ fontFamily: '"DM Sans", sans-serif', fontWeight: active ? 600 : 400 }}>
                {label}
              </span>
              {active && (
                <span className="absolute bottom-0 w-6 h-0.5 rounded-full"
                      style={{ background: '#FF6B6B', position: 'relative' }} />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
