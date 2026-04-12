import MobileShell from '../components/layout/MobileShell';
import { Camera, FolderOpen } from 'lucide-react';

export default function UploadPage() {
  return (
    <MobileShell title="Health Protocol">
      <div className="flex flex-col gap-4 p-4">

        {/* Primary CTA: camera */}
        <button className="w-full min-h-[120px] bg-blue-600 hover:bg-blue-700 active:bg-blue-800
          text-white rounded-2xl flex flex-col items-center justify-center gap-2
          transition-colors shadow-md">
          <Camera size={40} />
          <span className="text-lg font-semibold">Take Photo of Report</span>
          <span className="text-sm text-blue-200">Point camera at your blood test</span>
        </button>

        {/* Secondary CTA: file upload */}
        <button className="w-full min-h-[56px] bg-white border-2 border-slate-300
          text-slate-700 rounded-2xl flex items-center justify-center gap-3
          hover:border-blue-400 active:bg-slate-50 transition-colors">
          <FolderOpen size={22} />
          <span className="font-medium">Upload PDF</span>
        </button>

        {/* Recent reports placeholder */}
        <section className="mt-2">
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Recent Reports
          </h2>
          <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100">
            {['Mar 15 — Apollo', 'Jan 8 — Thyrocare'].map((label) => (
              <div key={label} className="flex items-center gap-3 px-4 min-h-[56px]">
                <span className="text-xl">📋</span>
                <span className="text-slate-700 text-base">{label}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </MobileShell>
  );
}
