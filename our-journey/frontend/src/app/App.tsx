import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { WelcomeScreen } from './components/WelcomeScreen';
import { OnboardingFlow } from './components/OnboardingFlow';
import { ChatScreen } from './components/ChatScreen';
import { CategoriesScreen } from './components/CategoriesScreen';
import { CrisisScreen } from './components/CrisisScreen';
import { SettingsScreen } from './components/SettingsScreen';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { AdminOverview } from './components/admin/AdminOverview';
import { ConversationsView } from './components/admin/ConversationsView';
import { FAQView } from './components/admin/FAQView';
import { FollowUpQueue } from './components/admin/FollowUpQueue';

export default function App() {
  return (
    <AppProvider>
      <Router>
        <Routes>
          <Route path="/" element={<WelcomeScreen />} />
          <Route path="/onboarding" element={<OnboardingFlow />} />
          <Route path="/chat" element={<ChatScreen />} />
          <Route path="/categories" element={<CategoriesScreen />} />
          <Route path="/crisis" element={<CrisisScreen />} />
          <Route path="/settings" element={<SettingsScreen />} />
          
          {/* Admin Dashboard Routes */}
          <Route path="/admin" element={<AdminDashboard />}>
            <Route index element={<AdminOverview />} />
            <Route path="conversations" element={<ConversationsView />} />
            <Route path="faq" element={<FAQView />} />
            <Route path="followup" element={<FollowUpQueue />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AppProvider>
  );
}