import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Globe, RotateCcw, Lock, Eye, Share2, Phone } from 'lucide-react';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { useApp } from '../context/AppContext';

export const SettingsScreen = () => {
  const navigate = useNavigate();
  const { language, setLanguage } = useApp();
  const [highContrast, setHighContrast] = useState(false);
  const [largeText, setLargeText] = useState(false);

  const handleStartOver = () => {
    if (confirm(language === 'en' 
      ? 'Are you sure you want to start over? This will clear your current conversation.'
      : '¿Estás seguro de que quieres empezar de nuevo? Esto borrará tu conversación actual.')) {
      navigate('/');
      window.location.reload();
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'JoJo - OurJourney Chatbot',
        text: language === 'en' 
          ? 'Check out JoJo, a helpful chatbot for reentry resources in North Carolina!'
          : '¡Mira JoJo, un chatbot útil para recursos de reingreso en Carolina del Norte!',
        url: window.location.origin
      });
    } else {
      alert(language === 'en' 
        ? 'Share this link: ' + window.location.origin
        : 'Comparte este enlace: ' + window.location.origin);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      {/* Header */}
      <div className="bg-white shadow-sm p-4">
        <div className="max-w-md mx-auto flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/chat')}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h2 className="font-semibold text-[#212121]">
              {language === 'en' ? 'Settings' : 'Configuración'}
            </h2>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="max-w-md mx-auto space-y-4">
          {/* Language */}
          <div className="bg-white rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <Globe className="w-5 h-5 text-[#388E3C]" />
              <h3 className="font-semibold text-gray-900">
                {language === 'en' ? 'Language' : 'Idioma'}
              </h3>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setLanguage('en')}
                className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                  language === 'en'
                    ? 'bg-[#1B5E20] text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage('es')}
                className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                  language === 'es'
                    ? 'bg-[#1B5E20] text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Español
              </button>
            </div>
          </div>

          {/* Accessibility */}
          <div className="bg-white rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Eye className="w-5 h-5 text-[#388E3C]" />
              <h3 className="font-semibold text-gray-900">
                {language === 'en' ? 'Accessibility' : 'Accesibilidad'}
              </h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="high-contrast" className="cursor-pointer">
                  {language === 'en' ? 'High Contrast Mode' : 'Modo de Alto Contraste'}
                </Label>
                <Switch
                  id="high-contrast"
                  checked={highContrast}
                  onCheckedChange={setHighContrast}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="large-text" className="cursor-pointer">
                  {language === 'en' ? 'Larger Text' : 'Texto Más Grande'}
                </Label>
                <Switch
                  id="large-text"
                  checked={largeText}
                  onCheckedChange={setLargeText}
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-xl p-4 space-y-3">
            {/* Start Over */}
            <button
              onClick={handleStartOver}
              className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left"
            >
              <RotateCcw className="w-5 h-5 text-[#388E3C]" />
              <div>
                <p className="font-medium text-gray-900">
                  {language === 'en' ? 'Start Over' : 'Empezar de Nuevo'}
                </p>
                <p className="text-sm text-gray-500">
                  {language === 'en' ? 'Begin a new conversation' : 'Comenzar una nueva conversación'}
                </p>
              </div>
            </button>

            {/* Share JoJo */}
            <button
              onClick={handleShare}
              className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left"
            >
              <Share2 className="w-5 h-5 text-[#388E3C]" />
              <div>
                <p className="font-medium text-gray-900">
                  {language === 'en' ? 'Share JoJo' : 'Compartir JoJo'}
                </p>
                <p className="text-sm text-gray-500">
                  {language === 'en' ? 'Tell a friend about this resource' : 'Cuéntale a un amigo sobre este recurso'}
                </p>
              </div>
            </button>

            {/* Contact OurJourney */}
            <a
              href="mailto:brian.scott@ourjourney2gether.com"
              className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left"
            >
              <Phone className="w-5 h-5 text-[#388E3C]" />
              <div>
                <p className="font-medium text-gray-900">
                  {language === 'en' ? 'Contact OurJourney' : 'Contactar a OurJourney'}
                </p>
                <p className="text-sm text-gray-500">
                  {language === 'en' ? 'Get in touch with our team' : 'Ponte en contacto con nuestro equipo'}
                </p>
              </div>
            </a>

            {/* Privacy Policy */}
            <a
              href="https://www.ourjourney2gether.com/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left"
            >
              <Lock className="w-5 h-5 text-[#388E3C]" />
              <div>
                <p className="font-medium text-gray-900">
                  {language === 'en' ? 'Privacy Policy' : 'Política de Privacidad'}
                </p>
                <p className="text-sm text-gray-500">
                  {language === 'en' ? 'How we protect your information' : 'Cómo protegemos tu información'}
                </p>
              </div>
            </a>
          </div>

          {/* About */}
          <div className="bg-white rounded-xl p-4 text-center">
            <p className="text-xs text-gray-400">Version 1.0.0</p>
          </div>
        </div>
      </div>
    </div>
  );
};