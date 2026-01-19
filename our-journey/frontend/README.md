# JoJo - OurJourney Reentry Resource Chatbot

A compassionate, accessible AI chatbot interface designed to help individuals returning from incarceration in North Carolina find essential resources including housing, employment, healthcare, legal aid, and more.

## Overview

Journey Jones (nickname: JoJo) is a 24/7 chatbot guide built for OurJourney, a nonprofit supporting reentry in North Carolina. The application features a warm, welcoming interface designed with accessibility and ease of use as top priorities.

## Features

### User-Facing Features
- **Multi-language Support**: English and Spanish (Español)
- **Onboarding Flow**: 5-step personalized intake to understand user needs
- **AI Chat Interface**: Natural conversation with quick-reply buttons and category browsing
- **Resource Cards**: Detailed resource information with click-to-call, maps, and website links
- **Crisis Support**: Dedicated crisis intervention screen with immediate hotline access
- **Category Browser**: 12 resource categories including Housing, Jobs, Legal, Healthcare, etc.
- **Settings & Accessibility**: Language toggle, high contrast mode, larger text options

### Admin Dashboard Features
- **Overview**: Real-time statistics on conversations, users, and engagement
- **Conversation History**: Search, filter, and review all user conversations
- **FAQ Analytics**: Auto-generated frequently asked questions from conversation patterns
- **Follow-Up Queue**: Manage users requesting personal assistance with status tracking

## Design System

### Brand Colors
- **Primary Green (Dark)**: `#1B5E20` - Headers, primary buttons
- **Primary Green (Medium)**: `#388E3C` - Interactive elements, links
- **Primary Green (Light)**: `#81C784` - Highlights, accents
- **Soft Green Tint**: `#E8F5E9` - Bot message bubbles, backgrounds
- **Black**: `#212121` - Body text
- **Off-White**: `#F5F5F5` - Page backgrounds
- **White**: `#FFFFFF` - Cards, user message bubbles

### Typography
- **Font Family**: Poppins (Google Fonts)
- **Weights**: Regular (400), Medium (500), SemiBold (600), Bold (700)
- **Minimum Size**: 16px for accessibility

## Tech Stack

- **Framework**: React 18.3.1 with TypeScript
- **Routing**: React Router DOM 7.11.0
- **Styling**: Tailwind CSS 4.1.12
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React
- **Build Tool**: Vite 6.3.5

## Project Structure

```
/src
  /app
    /components
      /admin          # Admin dashboard screens
      /ui             # Reusable UI components
      WelcomeScreen.tsx
      OnboardingFlow.tsx
      ChatScreen.tsx
      CategoriesScreen.tsx
      CrisisScreen.tsx
      SettingsScreen.tsx
      ResourceCard.tsx
    /context
      AppContext.tsx  # Global state management
    /data
      resources.ts    # Mock resource data
      nc-counties.ts  # NC counties list
    types.ts          # TypeScript types
    App.tsx           # Main app with routing
  /styles
    fonts.css         # Poppins font import
    theme.css         # Custom CSS variables
    tailwind.css      # Tailwind directives
    index.css         # Style imports
```

## Screen Flow

1. **Welcome Screen** → Language selection and introduction to JoJo
2. **Onboarding Flow** → 5-step intake (location, release date, age, gender, contact info)
3. **Chat Screen** → Main conversation interface with JoJo
4. **Categories Screen** → Browse resources by category
5. **Crisis Screen** → Emergency support and crisis hotlines
6. **Settings Screen** → Language, accessibility, privacy, app info

## Admin Access

Access the admin dashboard by:
1. Opening the menu in the chat screen
2. Clicking "Admin Dashboard"
3. Navigate to `/admin` directly

Admin sections:
- **Overview**: Key metrics and recent activity
- **Conversations**: View all user conversations with search and filters
- **FAQ**: Common questions identified from conversations
- **Follow-Up Queue**: Manage users requesting personal assistance

## Accessibility Features

- WCAG AA compliant color contrast (minimum 4.5:1 for text)
- Minimum 48x48px touch targets
- Scalable text (minimum 16px)
- Screen reader support with proper ARIA labels
- Keyboard navigation support
- Voice input option (microphone icon)
- Simple language (6th-8th grade reading level)
- High contrast mode available in settings

## Resource Categories

1. ID & Documents
2. Housing
3. Jobs & Training
4. Legal Help
5. Health & Mental Health
6. Transportation
7. Benefits & Money
8. Education
9. Family Support
10. Probation & Parole
11. Technology Help
12. Crisis & Emergency

## Development

### Prerequisites
- Node.js 18+ or 20+
- npm or pnpm

### Installation
```bash
npm install
```

### Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

## Future Enhancements

This is currently a frontend-only demonstration. For production deployment, consider:

1. **Backend Integration**: 
   - Database for storing conversations, user data, and resources
   - API for real-time chatbot responses
   - User authentication for admin dashboard

2. **Database Recommendations**:
   - Supabase for quick setup with PostgreSQL
   - Firebase for real-time capabilities
   - Custom Node.js/Express backend

3. **AI Integration**:
   - OpenAI GPT for natural language understanding
   - Custom-trained model on reentry resources
   - Intent classification for better response matching

4. **Analytics**:
   - Track most requested resources
   - User journey analytics
   - Conversion tracking for follow-up requests

5. **Notifications**:
   - Email/SMS for follow-up confirmations
   - Admin alerts for crisis flags
   - Reminder system for appointments

## Contact

For more information about OurJourney:
- Website: [https://www.ourjourney2gether.com/](https://www.ourjourney2gether.com/)
- Email: brian.scott@ourjourney2gether.com

## License

Created for OurJourney - Supporting Your Second Chance
