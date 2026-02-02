import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  getCurrentUser, 
  signInWithRedirect, 
  signOut, 
  fetchAuthSession,
  AuthUser
} from 'aws-amplify/auth';

/**
 * User group types matching Cognito User Pool Groups
 */
type UserGroup = 'Users' | 'Admins';

/**
 * Authentication context interface
 */
interface AuthContextType {
  /** Current authenticated user object from Cognito */
  user: AuthUser | null;
  
  /** User's group (Users or Admins) from Cognito */
  userGroup: UserGroup | null;
  
  /** Whether authentication state is being determined */
  isLoading: boolean;
  
  /** Whether user is authenticated */
  isAuthenticated: boolean;
  
  /** Initiate Cognito Hosted UI login flow */
  login: () => Promise<void>;
  
  /** Sign out and clear session */
  logout: () => Promise<void>;
  
  /** Manually refresh user session */
  refreshUser: () => Promise<void>;
}

/**
 * Authentication context
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider
 * 
 * Provides authentication state and methods throughout the application.
 * Automatically checks for authenticated user on mount and after OAuth redirects.
 * 
 * Features:
 * - Automatic user session detection
 * - User group extraction from JWT tokens
 * - Cognito Hosted UI integration
 * - Session management (login/logout)
 * 
 * Usage:
 * ```tsx
 * function App() {
 *   return (
 *     <AuthProvider>
 *       <YourApp />
 *     </AuthProvider>
 *   );
 * }
 * ```
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [userGroup, setUserGroup] = useState<UserGroup | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Check current authentication status and load user data
   */
  useEffect(() => {
    checkUser();
  }, []);

  /**
   * Check if user is authenticated and extract their group membership
   */
  async function checkUser() {
    try {
      console.log('Checking authentication status...');
      
      // Get current authenticated user
      const currentUser = await getCurrentUser();
      console.log('User authenticated:', currentUser.username);
      
      // Fetch user session to get JWT tokens
      const session = await fetchAuthSession();
      
      // Extract Cognito groups from access token
      // Groups are stored in the 'cognito:groups' claim
      const groups = (session.tokens?.accessToken?.payload['cognito:groups'] as string[]) || [];
      console.log('User groups:', groups);
      
      // Set user state
      setUser(currentUser);
      
      // Determine user role (Admins takes precedence over Users)
      if (groups.includes('Admins')) {
        console.log('User is an Admin');
        setUserGroup('Admins');
      } else if (groups.includes('Users')) {
        console.log('User is a regular User');
        setUserGroup('Users');
      } else {
        console.warn('User has no assigned group');
        setUserGroup(null);
      }
      
    } catch (error) {
      // User is not authenticated or session expired
      console.log('No authenticated user found');
      setUser(null);
      setUserGroup(null);
    } finally {
      setIsLoading(false);
    }
  }

  /**
   * Initiate login flow using Cognito Hosted UI
   * 
   * This redirects the user to the Cognito Hosted UI login page.
   * After successful authentication, Cognito redirects back to the app.
   */
  async function login() {
    try {
      console.log('Initiating login with Cognito Hosted UI...');
      await signInWithRedirect();
    } catch (error) {
      console.error('Error initiating login:', error);
      throw error;
    }
  }

  /**
   * Sign out current user and clear session
   * 
   * This signs the user out from Cognito and clears local session data.
   * The user will be redirected to the logout URL configured in Cognito.
   */
  async function logout() {
    try {
      console.log('Signing out user...');
      await signOut();
      
      // Clear local state
      setUser(null);
      setUserGroup(null);
      
      console.log('User signed out successfully');
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    }
  }

  /**
   * Manually refresh user session
   * 
   * Useful for checking updated group memberships or refreshing
   * expired tokens without requiring a full re-authentication.
   */
  async function refreshUser() {
    setIsLoading(true);
    await checkUser();
  }

  // Context value
  const value: AuthContextType = {
    user,
    userGroup,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * useAuth Hook
 * 
 * Custom hook to access authentication context.
 * Must be used within an AuthProvider.
 * 
 * Usage:
 * ```tsx
 * function MyComponent() {
 *   const { user, isAuthenticated, login, logout } = useAuth();
 *   
 *   if (!isAuthenticated) {
 *     return <button onClick={login}>Sign In</button>;
 *   }
 *   
 *   return (
 *     <div>
 *       <p>Welcome, {user?.username}!</p>
 *       <button onClick={logout}>Sign Out</button>
 *     </div>
 *   );
 * }
 * ```
 * 
 * @returns AuthContextType Authentication state and methods
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

/**
 * Helper function to check if user is an admin
 * 
 * @param userGroup The user's group from auth context
 * @returns boolean True if user is an admin
 */
export function isAdmin(userGroup: UserGroup | null): boolean {
  return userGroup === 'Admins';
}

/**
 * Helper function to check if user is a regular user
 * 
 * @param userGroup The user's group from auth context
 * @returns boolean True if user is a regular user
 */
export function isRegularUser(userGroup: UserGroup | null): boolean {
  return userGroup === 'Users';
}

/**
 * Helper function to check if user has any valid group
 * 
 * @param userGroup The user's group from auth context
 * @returns boolean True if user has a valid group assignment
 */
export function hasValidGroup(userGroup: UserGroup | null): boolean {
  return userGroup === 'Users' || userGroup === 'Admins';
}