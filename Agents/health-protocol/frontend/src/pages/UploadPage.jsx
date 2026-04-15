import { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';
import { Camera, FolderOpen, Loader2, FileText } from 'lucide-react';
import { api } from '../services/api';

function formatDate(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export default function UploadPage() {
  const navigate       = useNavigate();
  const cameraInputRef = useRef(null);
  const pdfInputRef    = useRef(null);

  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const [protocols, setProtocols] = useState([]);

  // Load recent reports on mount
  useEffect(() => {
    api.getProtocols()
      .then(setProtocols)
      .catch(() => {}); // silently fail — not critical
  }, []);

  async function handleFile(e) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;

    console.log('[Upload] file selected:', file.name, file.type, file.size, 'bytes');
    setError(null);
    setLoading(true);

    try {
      const result = await api.uploadFile(file);
      console.log('[Upload] API response:', result);
      // Navigate to review with extraction data in state (avoids an extra fetch)
      navigate(`/review/${result.extraction_id}`, { state: { extraction: result } });
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

        {/* Recent reports */}
        <section className="mt-2">
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Recent Reports
          </h2>

          {protocols.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-200 px-4 py-6
              text-center text-slate-400 text-sm">
              No reports yet — upload your first blood test above.
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100">
              {protocols.slice(0, 5).map((p) => (
                <button
                  key={p.id}
                  onClick={() => navigate(`/protocol/${p.id}`, {
                    state: { extractionId: p.extraction_id, backPath: '/' },
                  })}
                  className="w-full flex items-center gap-3 px-4 min-h-[60px]
                    hover:bg-slate-50 active:bg-slate-100 transition-colors text-left"
                >
                  <FileText size={20} className="text-blue-500 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-slate-800 font-medium text-base truncate">
                      {p.lab_name || 'Unknown Lab'}
                    </p>
                    <p className="text-xs text-slate-400">
                      {p.report_date || formatDate(p.created_at)}
                      {p.marker_count > 0 && ` · ${p.marker_count} markers`}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </section>
      </div>
    </MobileShell>
  );
}
