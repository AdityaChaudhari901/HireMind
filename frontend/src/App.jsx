import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Loading } from './components/common';

// Admin Pages
import AdminLogin from './pages/admin/Login';
import AdminRegister from './pages/admin/Register';
import Dashboard from './pages/admin/Dashboard';
import Questions from './pages/admin/Questions';
import NewQuestion from './pages/admin/NewQuestion';
import QuestionVariants from './pages/admin/QuestionVariants';
import TestLinks from './pages/admin/TestLinks';
import Results from './pages/admin/Results';

// Candidate Pages
import TestLanding from './pages/candidate/TestLanding';
import TestInterface from './pages/candidate/TestInterface';
import TestComplete from './pages/candidate/TestComplete';

// Protected Route Component
function ProtectedRoute({ children }) {
  const { admin, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading message="Loading..." />
      </div>
    );
  }

  if (!admin) {
    return <Navigate to="/admin/login" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Navigate to="/admin/login" replace />} />

      {/* Admin Auth Routes */}
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin/register" element={<AdminRegister />} />

      {/* Protected Admin Routes */}
      <Route path="/admin/dashboard" element={
        <ProtectedRoute><Dashboard /></ProtectedRoute>
      } />
      <Route path="/admin/questions" element={
        <ProtectedRoute><Questions /></ProtectedRoute>
      } />
      <Route path="/admin/questions/new" element={
        <ProtectedRoute><NewQuestion /></ProtectedRoute>
      } />
      <Route path="/admin/questions/:questionId/variants" element={
        <ProtectedRoute><QuestionVariants /></ProtectedRoute>
      } />
      <Route path="/admin/test-links" element={
        <ProtectedRoute><TestLinks /></ProtectedRoute>
      } />
      <Route path="/admin/test-links/new" element={
        <ProtectedRoute><TestLinks /></ProtectedRoute>
      } />
      <Route path="/admin/results" element={
        <ProtectedRoute><Results /></ProtectedRoute>
      } />
      <Route path="/admin/pending" element={
        <ProtectedRoute><Questions /></ProtectedRoute>
      } />

      {/* Candidate Test Routes (Public) */}
      <Route path="/test/:linkId" element={<TestLanding />} />
      <Route path="/test/:linkId/take" element={<TestInterface />} />
      <Route path="/test/:linkId/complete" element={<TestComplete />} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
