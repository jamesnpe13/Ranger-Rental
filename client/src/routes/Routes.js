import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useContext } from 'react';
import ProtectedRoute from '../components/ProtectedRoute';

// Lazy load pages for better performance
const HomePage = lazy(() => import('../pages/Home'));
const LoginPage = lazy(() => import('../pages/LoginPage'));
const RegisterPage = lazy(() => import('../pages/RegisterPage'));
const DashboardPage = lazy(() => import('../pages/DashboardPage'));
const ProfilePage = lazy(() => import('../pages/ProfilePage'));
const AdminLoginPage = lazy(() => import('../pages/AdminLoginPage'));
const NotFoundPage = lazy(() => import('../pages/NotFoundPage'));

// Loading component for lazy loading
const Loading = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
  </div>
);

// Public route wrapper
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useContext(AuthContext);
  return !isAuthenticated ? children : <Navigate to="/dashboard" />;
};

const AppRoutes = () => {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />

        {/* Admin login route */}
        <Route
          path="/admin"
          element={
            <PublicRoute>
              <AdminLoginPage />
            </PublicRoute>
          }
        />

        {/* 404 Not Found */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
