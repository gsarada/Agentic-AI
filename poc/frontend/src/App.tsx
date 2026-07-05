import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import HistoryPage from './pages/HistoryPage';
import LoginPage from './pages/LoginPage';
import ProductPage from './pages/ProductPage';
import ProfilePage from './pages/ProfilePage';
import RegisterPage from './pages/RegisterPage';
import UploadPage from './pages/UploadPage';
import { getToken } from './api';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  return getToken() ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
  <Routes>
    <Route element={<Layout />}>
      <Route path="/" element={<Navigate to="/profile" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/profile" element={<PrivateRoute><ProfilePage /></PrivateRoute>} />
      <Route path="/upload" element={<PrivateRoute><UploadPage /></PrivateRoute>} />
      <Route path="/product" element={<PrivateRoute><ProductPage /></PrivateRoute>} />
      <Route path="/chat" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
      <Route path="/history" element={<PrivateRoute><HistoryPage /></PrivateRoute>} />
    </Route>
  </Routes>
  );
}
