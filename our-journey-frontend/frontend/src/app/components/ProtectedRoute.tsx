import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute component props
 */
interface ProtectedRouteProps {
  /** Child components to render if authenticated */
  children: ReactNode;
  
  /** Optional: Custom redirect path (defaults to '/') */
  redirectTo?: string;
  
  /** Optional: Custom loading component */
  loadingComponent?: ReactNode;
}

/**
 * ProtectedRoute Component
 * 
 * Wraps routes that require authentication. If the user is not authenticated,
 * they will be redirected to the welcome/login screen.
 * 
 * Features:
 * - Blocks unauthenticated users
 * - Shows loading state while checking authentication
 * - Redirects regular users to onboarding on page refresh
 * - Preserves attempted location for post-login redirect (optional enhancement)
 * - Customizable redirect path and loading component
 * 
 * Usage:
 * ```tsx
 * <Route path="/chat" element={
 *   <ProtectedRoute>
 *     <ChatScreen />
 *   </ProtectedRoute>
 * } />
 * ```
 * 
 * With custom redirect:
 * ```tsx
 * <ProtectedRoute redirectTo="/login">
 *   <ChatScreen />
 * </ProtectedRoute>
 * ```
 */
export function ProtectedRoute({ 
  children, 
  redirectTo = '/',
  loadingComponent 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, userGroup } = useAuth();
  const location = useLocation();

  // Check if user has completed onboarding in this session
  const hasCompletedOnboarding = sessionStorage.getItem('onboardingCompleted') === 'true';
  const isRegularUser = userGroup === 'Users';
  const isNotOnboarding = location.pathname !== '/onboarding';

  // Show loading state while determining authentication status
  if (isLoading) {
    return loadingComponent || (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Loading...
      </div>
    );
  }

  // Redirect to login/welcome if not authenticated
  if (!isAuthenticated) {
    console.log(`ProtectedRoute: User not authenticated, redirecting to ${redirectTo}`);
    
    // Optionally preserve the attempted location for post-login redirect
    // You can use this in your WelcomeScreen to redirect users back after login
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Check if user has a valid group assignment
  // Users without a group might have authenticated but haven't been assigned a role
  if (!userGroup) {
    console.warn('ProtectedRoute: User authenticated but has no group assignment');
    
    // You could redirect to an error page or show a message
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        padding: '20px',
        textAlign: 'center'
      }}>
        <h2>Account Setup Required</h2>
        <p>Your account has been authenticated but hasn't been assigned a role yet.</p>
        <p>Please contact an administrator to complete your account setup.</p>
      </div>
    );
  }

  // User is authenticated and has a valid group - render protected content
  console.log(`ProtectedRoute: Access granted for ${userGroup} user`);
  
  // Redirect regular users to onboarding if they haven't completed it this session
  if (isRegularUser && isNotOnboarding && !hasCompletedOnboarding) {
    console.log('ProtectedRoute: Regular user has not completed onboarding, redirecting');
    return <Navigate to="/onboarding" replace />;
  }
  
  return <>{children}</>;
}

/**
 * Default loading component
 * Can be used as a fallback or customized
 */
export function DefaultLoadingComponent() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      gap: '20px'
    }}>
      <div style={{
        width: '50px',
        height: '50px',
        border: '4px solid #f3f3f3',
        borderTop: '4px solid #3498db',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }} />
      <p style={{ fontSize: '18px', color: '#666' }}>
        Loading...
      </p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}