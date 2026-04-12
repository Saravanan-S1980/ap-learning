import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';
import { Camera, FolderOpen, Loader2 } from 'lucide-react';
import { api } from '../services/api';

export default function UploadPage() {
  const navigate      = useNavigate();
  const cameraInputRef = useRef(null);
  const pdfInputRef    = useRef(null);

  const [loading, setLoading]   = useState(false);
  const [error,   setError]     = useState(null);

  async function handleFile(e) {
    const file = e.target.files?.[0];
    e.target.value = ''; // reset so same file can be re-selected
    if (!file) return;

    console.log('[Upload] file selected:', file.name, file.type, file.size, 'bytes');
    setError(null);
    setLoading(true);

    try {
      const result = await api.uploadFile(file);
      console.log('[Upload] API response:', result);
      // Pass extraction data to ReviewPage via router state
      navigate('/review', { state: { extraction: result } });
    } catch (err) {
      console.error('[Upload] API error:', err);
      setError(err.message || 'Upload failed. Check the console for details.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <MobileShell title="Health Protocol">
      {/* Hidden file inputs */}
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*,application/pdf"
        capture="environment"
        className="hidden"
        onChange={handleFile}
      />
      <input
        ref={pdfInputRef}
        type="file"
        accept="application/pdf,image/*"
        className="hidden"
        onChange={handleFile}
      />

      <div className="flex flex-col gap-4 p-4">

        {/* Error banner */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-2xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {/* Primary CTA: camera */}
        <button
          disabled={loading}
          onClick={() => cameraInputRef.current?.click()}
          className="w-full min-h-[120px] bg-blue-600 hover:bg-blue-700 active:bg-blue-800
            disabled:opacity-60 text-white rounded-2xl flex flex-col items-center
            justify-center gap-2 transition-colors shadow-md"
        >
          {loading ? <Loader2 size={40} className="animate-spin" /> : <Camera size={40} />}
          <span className="text-lg font-semibold">Take Photo of Report</span>
          <span className="text-sm text-blue-200">
            {loading ? 'Extracting markers…' : 'Point camera at your blood test'}
          </span>
        </button>

        {/* Secondary CTA: PDF upload */}
        <button
          disabled={loading}
          onClick={() => pdfInputRef.current?.click()}
          className="w-full min-h-[56px] bg-white border-2 border-slate-300
            text-slate-700 rounded-2xl flex items-center justify-center gap-3
            hover:border-blue-400 active:bg-slate-50 disabled:opacity-60 transition-colors"
        >
          {loading
            ? <Loader2 size={22} className="animate-spin" />
            : <FolderOpen size={22} />}
          <span className="font-medium">{loading ? 'Analysing…' : 'Upload PDF'}</span>
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
