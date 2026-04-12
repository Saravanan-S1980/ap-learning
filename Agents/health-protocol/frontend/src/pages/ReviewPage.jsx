import { useNavigate } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';

export default function ReviewPage() {
  const navigate = useNavigate();

  return (
    <MobileShell title="Review Report" backPath="/">
      <div className="flex flex-col gap-4 p-4">

        {/* Report meta */}
        <div className="bg-white rounded-2xl border border-slate-200 px-4 py-3">
          <p className="text-sm text-slate-500">Lab</p>
          <p className="font-semibold text-slate-900">—</p>
          <p className="text-sm text-slate-500 mt-1">Date</p>
          <p className="font-semibold text-slate-900">—</p>
        </div>

        {/* Placeholder marker list */}
        <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100">
          <div className="px-4 py-3 text-slate-400 text-base text-center min-h-[56px] flex items-center justify-center">
            Upload a report to see markers
          </div>
        </div>

        {/* Sticky CTA */}
        <button
          onClick={() => navigate('/goals')}
          className="w-full min-h-[52px] bg-blue-600 text-white rounded-2xl
            font-semibold text-base hover:bg-blue-700 active:bg-blue-800 transition-colors shadow"
        >
          Continue to Goals →
        </button>
      </div>
    </MobileShell>
  );
}
