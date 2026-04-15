const BASE_URL = '/api'; // Vite proxy forwards to http://localhost:8001

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== undefined) {
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`${BASE_URL}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  /** POST /api/upload — multipart form with 'file' field */
  async uploadFile(file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  /** GET /api/extraction/{id} */
  getExtraction: (id) => request('GET', `/extraction/${id}`),

  /** PUT /api/markers/{id} */
  updateMarkers: (id, markers) => request('PUT', `/markers/${id}`, { markers }),

  /** POST /api/analyze */
  analyze: (markers, goals, extractionId = '') =>
    request('POST', '/analyze', { markers, goals, extraction_id: extractionId }),

  /** GET /api/protocol/{id} */
  getProtocol: (id) => request('GET', `/protocol/${id}`),

  /** GET /api/protocols — all past protocols, newest first */
  getProtocols: () => request('GET', '/protocols'),

  /** GET /health */
  health: () => request('GET', '/health').catch(() => null),
};
