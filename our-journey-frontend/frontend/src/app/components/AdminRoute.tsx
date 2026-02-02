import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * AdminRoute component props
 */
interface AdminRouteProps {
  /** Child components to render if user is an admin */
  children: ReactNode;
  
  /** Optional: Custom redirect path for non-admins (defaults to '/chat') */
  redirectTo?: string;
  
  /** Optional: Custom redirect path for unauthenticated users (defaults to '/') */
  loginRedirectTo?: string;
  
  /** Optional: Custom loading component */
  loadingComponent?: ReactNode;
  
  /** Optional: Custom unauthorized component */
  unauthorizedComponent?: ReactNode;
}

/**
 * AdminRoute Component
 * 
 * Wraps routes that require admin privileges. Only users in the 'Admins' 
 * Cognito group can access these routes.
 * 
 * Behavior:
 * - Not authenticated → Redirect to login page (default: '/')
 * - Authenticated but not admin → Redirect to user area (default: '/chat')
 * - Authenticated admin → Render protected content
 * 
 * Features:
 * - Blocks unauthenticated users
 * - Blocks non-admin users (Users group)
 * - Shows loading state while checking authentication
 * - Customizable redirect paths and components
 * - Helpful unauthorized message
 * 
 * Usage:
 * ```tsx
 * <Route path="/admin" element={
 *   <AdminRoute>
 *     <AdminDashboard />
 *   </AdminRoute>
 * } />
 * ```
 * 
 * With custom redirects:
 * ```tsx
 * <AdminRoute 
 *   redirectTo="/home" 
 *   loginRedirectTo="/login"
 * >
 *   <AdminDashboard />
 * </AdminRoute>
 * ```
 */
export function AdminRoute({ 
  children, 
  redirectTo = '/chat',
  loginRedirectTo = '/',
  loadingComponent,
  unauthorizedComponent
}: AdminRouteProps) {
  const { isAuthenticated, isLoading, userGroup } = useAuth();
  const location = useLocation();

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

  // First check: User must be authenticated
  if (!isAuthenticated) {
    console.log(`AdminRoute: User not authenticated, redirecting to ${loginRedirectTo}`);
    return <Navigate to={loginRedirectTo} state={{ from: location }} replace />;
  }

  // Second check: User must have a group assignment
  if (!userGroup) {
    console.warn('AdminRoute: User authenticated but has no group assignment');
    
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

  // Third check: User must be in the Admins group
  if (userGroup !== 'Admins') {
    console.log(`AdminRoute: User is not an admin (group: ${userGroup}), redirecting to ${redirectTo}`);
    
    // Render custom unauthorized component or default message
    if (unauthorizedComponent) {
      return <>{unauthorizedComponent}</>;
    }
    
    // Show brief unauthorized message before redirect
    // In production, you might want to redirect immediately
    return <Navigate to={redirectTo} replace />;
  }

  // All checks passed - user is authenticated admin
  console.log('AdminRoute: Access granted for admin user');
  return <>{children}</>;
}

/**
 * UnauthorizedAccess Component
 * 
 * Default component shown when a non-admin user tries to access admin routes.
 * Can be used as a prop to AdminRoute or standalone.
 */
export function UnauthorizedAccess({ 
  message = "You don't have permission to access this page.",
  redirectPath = '/chat',
  redirectDelay = 3000 
}: {
  message?: string;
  redirectPath?: string;
  redirectDelay?: number;
}) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      padding: '20px',
      textAlign: 'center',
      gap: '20px'
    }}>
      <div style={{
        fontSize: '64px',
        color: '#e74c3c'
      }}>
        🚫
      </div>
      <h2 style={{
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#333',
        margin: 0
      }}>
        Access Denied
      </h2>
      <p style={{
        fontSize: '16px',
        color: '#666',
        maxWidth: '500px',
        margin: 0
      }}>
        {message}
      </p>
      <p style={{
        fontSize: '14px',
        color: '#999'
      }}>
        Redirecting you back in {redirectDelay / 1000} seconds...
      </p>
    </div>
  );
}

/**
 * AdminOnly Component
 * 
 * Alternative approach: Inline component that conditionally renders
 * content only for admin users.
 * 
 * Usage:
 * ```tsx
 * <AdminOnly fallback={<p>Admin only content</p>}>
 *   <AdminPanel />
 * </AdminOnly>
 * ```
 */
export function AdminOnly({ 
  children, 
  fallback 
}: { 
  children: ReactNode; 
  fallback?: ReactNode 
}) {
  const { userGroup } = useAuth();
  
  if (userGroup === 'Admins') {
    return <>{children}</>;
  }
  
  return fallback ? <>{fallback}</> : null;
}

/**
 * Helper hook to check admin status
 * 
 * Usage:
 * ```tsx
 * const isAdmin = useIsAdmin();
 * 
 * if (isAdmin) {
 *   return <AdminButton />;
 * }
 * ```
 */
export function useIsAdmin(): boolean {
  const { userGroup } = useAuth();
  return userGroup === 'Admins';
}