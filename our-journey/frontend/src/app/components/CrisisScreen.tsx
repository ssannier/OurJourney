import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Phone, ArrowLeft, Heart } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { useApp } from '../context/AppContext';

export const CrisisScreen = () => {
  const navigate = useNavigate();
  const { language } = useApp();
  const [showFollowUp, setShowFollowUp] = useState(false);
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmitFollowUp = () => {
    // In a real app, this would send the data to a backend
    console.log('Follow-up requested:', { email, phone });
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#E8F5E9] to-[#F5F5F5]">
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
              {language === 'en' ? 'Crisis Support' : 'Apoyo en Crisis'}
            </h2>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="max-w-md mx-auto">
          {/* Supportive Message */}
          <div className="bg-white rounded-2xl p-6 shadow-sm mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-[#E8F5E9] rounded-full flex items-center justify-center">
                <Heart className="w-6 h-6 text-[#1B5E20]" />
              </div>
              <h3 className="font-semibold text-gray-900">
                {language === 'en' ? "You're Not Alone" : 'No Estás Solo/a'}
              </h3>
            </div>
            <p className="text-gray-700 mb-4">
              {language === 'en'
                ? "I hear you, and I want to make sure you're safe. You're not alone in this. There are people who care and want to help."
                : 'Te escucho y quiero asegurarme de que estés a salvo. No estás solo/a en esto. Hay personas que se preocupan y quieren ayudar.'}
            </p>
          </div>

          {/* Crisis Resources */}
          <div className="space-y-3 mb-6">
            <h4 className="font-semibold text-gray-900 mb-3">
              {language === 'en' ? 'Immediate Help Available 24/7:' : 'Ayuda Inmediata Disponible 24/7:'}
            </h4>

            {/* 988 Suicide & Crisis Lifeline */}
            <a
              href="tel:988"
              className="block bg-white rounded-xl p-4 border-2 border-[#388E3C] hover:bg-[#E8F5E9] transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-[#1B5E20] rounded-full flex items-center justify-center">
                  <Phone className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h5 className="font-semibold text-gray-900">988</h5>
                  <p className="text-sm text-gray-600">
                    {language === 'en' 
                      ? 'Suicide & Crisis Lifeline (call or text)'
                      : 'Línea de Prevención del Suicidio (llamar o enviar mensaje)'}
                  </p>
                </div>
              </div>
            </a>

            {/* Crisis Text Line */}
            <a
              href="sms:741741"
              className="block bg-white rounded-xl p-4 border-2 border-[#388E3C] hover:bg-[#E8F5E9] transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-[#388E3C] rounded-full flex items-center justify-center">
                  <Phone className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h5 className="font-semibold text-gray-900">
                    {language === 'en' ? 'Text HELLO to 741741' : 'Envía HELLO al 741741'}
                  </h5>
                  <p className="text-sm text-gray-600">
                    {language === 'en' ? 'Crisis Text Line' : 'Línea de Texto de Crisis'}
                  </p>
                </div>
              </div>
            </a>

            {/* Domestic Violence Hotline */}
            <a
              href="tel:18007997233"
              className="block bg-white rounded-xl p-4 border-2 border-[#388E3C] hover:bg-[#E8F5E9] transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-[#81C784] rounded-full flex items-center justify-center">
                  <Phone className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h5 className="font-semibold text-gray-900">1-800-799-7233</h5>
                  <p className="text-sm text-gray-600">
                    {language === 'en' 
                      ? 'National Domestic Violence Hotline'
                      : 'Línea Nacional de Violencia Doméstica'}
                  </p>
                </div>
              </div>
            </a>

            {/* 911 */}
            <a
              href="tel:911"
              className="block bg-white rounded-xl p-4 border-2 border-red-300 hover:bg-red-50 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
                  <Phone className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h5 className="font-semibold text-gray-900">911</h5>
                  <p className="text-sm text-gray-600">
                    {language === 'en' ? 'Emergency Services' : 'Servicios de Emergencia'}
                  </p>
                </div>
              </div>
            </a>
          </div>

          {/* Follow-Up Option */}
          {!showFollowUp && !submitted && (
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <p className="text-gray-700 mb-4">
                {language === 'en'
                  ? 'Would you like someone from OurJourney to reach out to you?'
                  : '¿Te gustaría que alguien de OurJourney se comunique contigo?'}
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setShowFollowUp(true)}
                  className="flex-1 bg-[#1B5E20] hover:bg-[#388E3C] text-white"
                >
                  {language === 'en' ? 'Yes, please contact me' : 'Sí, por favor contáctame'}
                </Button>
                <Button
                  onClick={() => navigate('/chat')}
                  variant="outline"
                  className="flex-1"
                >
                  {language === 'en' ? "I'm okay" : 'Estoy bien'}
                </Button>
              </div>
            </div>
          )}

          {/* Follow-Up Form */}
          {showFollowUp && !submitted && (
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h4 className="font-semibold text-gray-900 mb-4">
                {language === 'en' ? 'Contact Information' : 'Información de Contacto'}
              </h4>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="crisis-email">
                    {language === 'en' ? 'Email' : 'Correo Electrónico'}
                  </Label>
                  <Input
                    id="crisis-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={language === 'en' ? 'your@email.com' : 'tu@correo.com'}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="crisis-phone">
                    {language === 'en' ? 'Phone' : 'Teléfono'}
                  </Label>
                  <Input
                    id="crisis-phone"
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="(555) 123-4567"
                    className="mt-2"
                  />
                </div>
                <Button
                  onClick={handleSubmitFollowUp}
                  disabled={!email && !phone}
                  className="w-full bg-[#1B5E20] hover:bg-[#388E3C] text-white"
                >
                  {language === 'en' ? 'Submit' : 'Enviar'}
                </Button>
              </div>
            </div>
          )}

          {/* Confirmation */}
          {submitted && (
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="text-center">
                <div className="w-16 h-16 bg-[#E8F5E9] rounded-full flex items-center justify-center mx-auto mb-4">
                  <Heart className="w-8 h-8 text-[#1B5E20]" />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">
                  {language === 'en' ? 'Thank You' : 'Gracias'}
                </h4>
                <p className="text-gray-700 mb-4">
                  {language === 'en'
                    ? "We'll have someone contact you within 24 hours. Stay safe."
                    : 'Alguien se comunicará contigo dentro de 24 horas. Mantente a salvo.'}
                </p>
                <Button
                  onClick={() => navigate('/chat')}
                  className="w-full bg-[#1B5E20] hover:bg-[#388E3C] text-white"
                >
                  {language === 'en' ? 'Back to Chat' : 'Volver al Chat'}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
