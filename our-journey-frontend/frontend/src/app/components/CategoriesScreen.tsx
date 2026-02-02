import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Home, Briefcase, Scale, Heart, Bus, DollarSign, GraduationCap, Users, ClipboardList, Smartphone, AlertCircle, CreditCard, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import { useApp } from '../context/AppContext';
import { RESOURCE_CATEGORIES } from '../data/resources';
import { signOut } from 'aws-amplify/auth';

const iconMap: Record<string, any> = {
  'CreditCard': CreditCard,
  'Home': Home,
  'Briefcase': Briefcase,
  'Scale': Scale,
  'Heart': Heart,
  'Bus': Bus,
  'DollarSign': DollarSign,
  'GraduationCap': GraduationCap,
  'Users': Users,
  'ClipboardList': ClipboardList,
  'Smartphone': Smartphone,
  'AlertCircle': AlertCircle
};

export const CategoriesScreen = () => {
  const navigate = useNavigate();
  const { language } = useApp();

  const handleCategoryClick = (categoryId: string, categoryName: string) => {
    if (categoryId === 'crisis') {
      navigate('/crisis');
    } else {
      navigate(`/chat?category=${categoryId}`);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/login'); // Adjust to your login route
    } catch (error) {
      console.error('Error signing out:', error);
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
          <div className="flex-1">
            <h2 className="font-semibold text-[#212121]">
              {language === 'en' ? 'Browse Categories' : 'Explorar Categorías'}
            </h2>
            <p className="text-sm text-gray-500">
              {language === 'en' ? 'Find resources by topic' : 'Encuentra recursos por tema'}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleSignOut}
            title={language === 'en' ? 'Sign Out' : 'Cerrar Sesión'}
          >
            <LogOut className="w-5 h-5 text-gray-600" />
          </Button>
        </div>
      </div>

      {/* Categories Grid */}
      <div className="p-6">
        <div className="max-w-md mx-auto">
          <p className="text-sm text-gray-600 mb-4">
            {language === 'en' 
              ? 'Select a category to see available resources:'
              : 'Selecciona una categoría para ver los recursos disponibles:'}
          </p>
          <div className="grid grid-cols-2 gap-3">
            {RESOURCE_CATEGORIES.map((category) => {
              const Icon = iconMap[category.icon];
              return (
                <button
                  key={category.id}
                  onClick={() => handleCategoryClick(category.id, category.name)}
                  className="bg-white rounded-xl p-4 border-2 border-gray-200 hover:border-[#388E3C] hover:bg-[#E8F5E9] transition-all text-left min-h-[120px] flex flex-col items-start justify-between"
                >
                  <div className="w-12 h-12 bg-[#E8F5E9] rounded-full flex items-center justify-center mb-3">
                    {Icon && <Icon className="w-6 h-6 text-[#1B5E20]" />}
                  </div>
                  <span className="font-medium text-gray-800 text-sm">{category.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};