export interface UserInfo {
  county: string;
  releaseDate: string;
  age18Plus: boolean;
  gender: string;
  email?: string;
  phone?: string;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  quickReplies?: string[];
  resources?: Resource[];
}

export interface Resource {
  id: string;
  name: string;
  description: string;
  category: string;
  phone?: string;
  address?: string;
  website?: string;
  isOurJourney?: boolean;
}

export interface Conversation {
  id: string;
  userId: string;
  messages: Message[];
  flagged: 'none' | 'crisis' | 'followup' | 'resolved';
  createdAt: Date;
  userInfo?: UserInfo;
}

export type ResourceCategory = 
  | 'id-documents'
  | 'housing'
  | 'jobs'
  | 'legal'
  | 'health'
  | 'transportation'
  | 'benefits'
  | 'education'
  | 'family'
  | 'probation'
  | 'technology'
  | 'crisis';

export type OnboardingStep = 'location' | 'release' | 'age' | 'gender' | 'contact';

export type Language = 'en' | 'es';
