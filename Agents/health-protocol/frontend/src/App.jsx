import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import UploadPage   from './pages/UploadPage';
import ReviewPage   from './pages/ReviewPage';
import GoalsPage    from './pages/GoalsPage';
import ProtocolPage from './pages/ProtocolPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"         element={<UploadPage />} />
        <Route path="/review"   element={<ReviewPage />} />
        <Route path="/goals"    element={<GoalsPage />} />
        <Route path="/protocol" element={<ProtocolPage />} />
        <Route path="*"         element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
