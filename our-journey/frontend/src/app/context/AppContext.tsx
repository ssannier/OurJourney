import React, { createContext, useContext, useState, ReactNode } from 'react';
import { UserInfo, Message, Language } from '../types';

interface AppContextType {
  userInfo: UserInfo | null;
  setUserInfo: (info: UserInfo | null) => void;
  messages: Message[];
  addMessage: (message: Message) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  language: Language;
  setLanguage: (lang: Language) => void;
  onboardingComplete: boolean;
  setOnboardingComplete: (complete: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [language, setLanguage] = useState<Language>('en');
  const [onboardingComplete, setOnboardingComplete] = useState(false);

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message]);
  };

  const updateMessage = (messageId: string, updates: Partial<Message>) => {
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId ? { ...msg, ...updates } : msg
      )
    );
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <AppContext.Provider
      value={{
        userInfo,
        setUserInfo,
        messages,
        addMessage,
        updateMessage,
        clearMessages,
        language,
        setLanguage,
        onboardingComplete,
        setOnboardingComplete
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};