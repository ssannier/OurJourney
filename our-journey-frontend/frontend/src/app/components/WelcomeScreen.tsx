import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { useApp } from '../context/AppContext';

export const WelcomeScreen = () => {
  const navigate = useNavigate();
  const { language, setLanguage } = useApp();

  const handleStartChat = () => {
    navigate('/onboarding');
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] flex flex-col items-center justify-center p-6">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center">
        {/* Language Toggle */}
        <div className="flex justify-center gap-2 mb-8">
          <button
            onClick={() => setLanguage('en')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              language === 'en'
                ? 'bg-[#1B5E20] text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            English
          </button>
          <button
            onClick={() => setLanguage('es')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              language === 'es'
                ? 'bg-[#1B5E20] text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Español
          </button>
        </div>

        {/* JoJo Avatar */}
        <div className="mb-6">
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-[#388E3C] to-[#81C784] rounded-full flex items-center justify-center shadow-md">
            <div className="text-white text-4xl">🤖</div>
          </div>
        </div>

        {/* Welcome Message */}
        <h1 className="text-2xl font-semibold text-[#212121] mb-4">
          {language === 'en' ? "Hi, I'm JoJo!" : "¡Hola, soy JoJo!"}
        </h1>
        
        <p className="text-gray-700 mb-6 leading-relaxed">
          {language === 'en'
            ? "I'm your guide to reentry resources in North Carolina. I'm here to help you find housing, jobs, healthcare, and more. Let's get started!"
            : "Soy tu guía de recursos de reingreso en Carolina del Norte. Estoy aquí para ayudarte a encontrar vivienda, empleo, atención médica y más. ¡Empecemos!"}
        </p>

        {/* Start Chat Button */}
        <Button
          onClick={handleStartChat}
          className="w-full bg-[#1B5E20] hover:bg-[#388E3C] text-white py-6 rounded-xl mb-6"
        >
          {language === 'en' ? 'Start Chat' : 'Iniciar Chat'}
        </Button>

        {/* Privacy Note */}
        <p className="text-sm text-gray-500">
          {language === 'en'
            ? 'Your information is confidential and used only to help you.'
            : 'Tu información es confidencial y se usa solo para ayudarte.'}
        </p>
      </div>
    </div>
  );
};