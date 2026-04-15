import { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MobileShell from '../components/layout/MobileShell';
import { Camera, FolderOpen, Loader2, FileText, ChevronRight } from 'lucide-react';
import { api } from '../services/api';

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export default function UploadPage() {
  const navigate       = useNavigate();
  const cameraInputRef = useRef(null);
  const pdfInputRef    = useRef(null);

  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const [protocols, setProtocols] = useState(null); // null = loading, [] = empty

  useEffect(() => {
    api.getProtocols()
      .then(setProtocols)
      .catch(() => setProtocols([]));
  }, []);

  async function handleFile(e) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;

    setError(null);
    setLoading(true);
    try {
      const result = await api.uploadFile(file);
      navigate(`/review/${result.extraction_id}`, { state: { extraction: result } });
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <MobileShell title="Health Protocol" brand>
      {/* Hidden file inputs */}
      <input ref={cameraInputRef} type="file" accept="image/*,application/pdf"
             capture="environment" className="hidden" onChange={handleFile} />
      <input ref={pdfInputRef}    type="file" accept="application/pdf,image/*"
             className="hidden" onChange={handleFile} />

      <div className="flex flex-col gap-4 p-4 page-enter">

        {/* Error banner */}
        {error && (
          <div className="rounded-2xl px-4 py-3 text-sm font-medium"
               style={{ background: 'rgba(231,76,111,.1)', color: '#C0334E', border: '1px solid rgba(231,76,111,.25)' }}>
            {error}
          </div>
        )}

        {/* Onboarding tagline */}
        <div className="rounded-2xl px-4 py-3 text-sm"
             style={{ background: 'linear-gradient(135deg,rgba(45,106,106,.07),rgba(244,162,97,.07))',
                      border: '1px solid rgba(45,106,106,.12)' }}>
          <p className="font-heading font-semibold text-charcoal mb-0.5">
            Your personalised health protocol
          </p>
          <p className="text-muted leading-relaxed">
            Upload your blood test → get evidence-based diet, supplements &amp; lifestyle recommendations in 60 seconds.
          </p>
        </div>

        {/* Primary CTA — camera */}
        <button
          disabled={loading}
          onClick={() => cameraInputRef.current?.click()}
          className="w-full rounded-2xl flex flex-col items-center justify-center gap-2
                     transition-all duration-200 active:scale-[.98] disabled:opacity-60"
          style={{
            background: 'linear-gradient(135deg,#FF6B6B 0%,#FF8E53 100%)',
            minHeight: 128,
            boxShadow: '0 6px 20px -4px rgba(255,107,107,.5)',
          }}
        >
          {loading
            ? <Loader2 size={44} color="white" className="animate-spin" />
            : <Camera  size={44} color="white" />}
          <span className="text-lg font-heading font-bold text-white">
            {loading ? 'Extracting markers…' : 'Scan Your Report'}
          </span>
          <span className="text-sm text-white" style={{ opacity: .8 }}>
            {loading ? 'AI is reading your blood test' : 'Take a photo of your blood test'}
          </span>
        </button>

        {/* Secondary CTA — PDF upload */}
        <button
          disabled={loading}
          onClick={() => pdfInputRef.current?.click()}
          className="btn-outline"
          style={{ borderStyle: 'dashed', borderColor: '#C8BDB5' }}
        >
          {loading ? <Loader2 size={20} className="animate-spin" /> : <FolderOpen size={20} />}
          <span>{loading ? 'Analysing…' : 'Upload PDF Report'}</span>
        </button>

        {/* Recent Reports */}
        <section className="mt-1">
          <h2 className="text-xs font-heading font-bold text-muted uppercase tracking-widest mb-3 px-1">
            Recent Reports
          </h2>

          {protocols === null ? (
            /* skeleton */
            <div className="flex flex-col gap-2">
              {[1, 2].map((k) => (
                <div key={k} className="skeleton rounded-2xl" style={{ height: 68 }} />
              ))}
            </div>
          ) : protocols.length === 0 ? (
            <div className="rounded-2xl border border-warm-border px-4 py-8
                            text-center text-muted text-sm" style={{ background: '#fff' }}>
              No reports yet — upload your first blood test above.
            </div>
          ) : (
            <div className="rounded-2xl overflow-hidden" style={{ background: '#fff', boxShadow: 'var(--shadow-warm-md)' }}>
              {protocols.slice(0, 5).map((p, i) => (
                <button
                  key={p.id}
                  onClick={() => navigate(`/protocol/${p.id}`, {
                    state: { extractionId: p.extraction_id, backPath: '/' },
                  })}
                  className="w-full flex items-center gap-3 px-4 min-h-[68px]
                             transition-colors duration-150 text-left"
                  style={{
                    borderTop: i > 0 ? '1px solid #F5EFE9' : 'none',
                    background: 'transparent',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = '#FFF9F5'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  {/* Teal left accent bar */}
                  <div className="w-1 self-stretch rounded-full shrink-0"
                       style={{ background: 'linear-gradient(180deg,#2D6A6A,#3D8A8A)', minHeight: 40 }} />
                  <FileText size={18} style={{ color: '#2D6A6A' }} className="shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-heading font-semibold text-charcoal text-base truncate">
                      {p.lab_name || 'Unknown Lab'}
                    </p>
                    <p className="text-xs text-muted mt-0.5">
                      {p.report_date || formatDate(p.created_at)}
                      {p.marker_count > 0 && ` · ${p.marker_count} markers`}
                    </p>
                  </div>
                  <ChevronRight size={16} style={{ color: '#C8BDB5' }} className="shrink-0" />
                </button>
              ))}
            </div>
          )}
        </section>
      </div>
    </MobileShell>
  );
}
