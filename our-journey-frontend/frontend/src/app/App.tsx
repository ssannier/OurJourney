import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { AuthProvider } from './context/AuthContext';
import { WelcomeScreen } from './components/WelcomeScreen';
import { OnboardingFlow } from './components/OnboardingFlow';
import { ChatScreen } from './components/ChatScreen';
import { CategoriesScreen } from './components/CategoriesScreen';
import { CrisisScreen } from './components/CrisisScreen';
import { SettingsScreen } from './components/SettingsScreen';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { ConversationsView } from './components/admin/ConversationsView';
import { FollowUpQueue } from './components/admin/FollowUpQueue';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AdminRoute } from './components/AdminRoute';

/**
 * Main Application Component
 * 
 * Provides application-wide context and routing with authentication protection.
 * 
 * Structure:
 * - AuthProvider: Manages Cognito authentication state
 * - AppProvider: Manages application-specific state
 * - Router: Handles client-side routing with protected routes
 * 
 * Route Protection:
 * - Public routes: / (WelcomeScreen with login)
 * - Protected routes: /onboarding, /chat, /categories, /crisis, /settings
 *   → Require authentication (Users or Admins group)
 * - Admin routes: /admin/*
 *   → Require authentication AND Admins group membership
 */
export default function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <Router>
          <Routes>
            {/* Public Route - Welcome/Login Screen */}
            <Route path="/" element={<WelcomeScreen />} />

            {/* Protected User Routes - Require Authentication */}
            <Route 
              path="/onboarding" 
              element={
                <ProtectedRoute>
                  <OnboardingFlow />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/chat" 
              element={
                <ProtectedRoute>
                  <ChatScreen />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/categories" 
              element={
                <ProtectedRoute>
                  <CategoriesScreen />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/crisis" 
              element={
                <ProtectedRoute>
                  <CrisisScreen />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <SettingsScreen />
                </ProtectedRoute>
              } 
            />

            {/* Admin-Only Routes - Require Admin Group Membership */}
            <Route 
              path="/admin" 
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              }
            >
              {/* Nested Admin Routes */}
              <Route index element={<Navigate to="/admin/conversations" replace />} />
              <Route path="conversations" element={<ConversationsView />} />
              <Route path="followup" element={<FollowUpQueue />} />
            </Route>

            {/* Catch-All Route - Redirect to Welcome */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AppProvider>
    </AuthProvider>
  );
}