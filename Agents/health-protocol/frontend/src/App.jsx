import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import UploadPage   from './pages/UploadPage';
import ReviewPage   from './pages/ReviewPage';
import GoalsPage    from './pages/GoalsPage';
import ProtocolPage from './pages/ProtocolPage';
import HistoryPage  from './pages/HistoryPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"              element={<UploadPage />} />
        {/* /review without an ID is invalid — redirect home */}
        <Route path="/review"        element={<Navigate to="/" replace />} />
        <Route path="/review/:id"    element={<ReviewPage />} />
        <Route path="/goals"         element={<GoalsPage />} />
        <Route path="/protocol/:id"  element={<ProtocolPage />} />
        <Route path="/history"       element={<HistoryPage />} />
        <Route path="/settings"      element={<UploadPage />} />
        <Route path="*"              element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
