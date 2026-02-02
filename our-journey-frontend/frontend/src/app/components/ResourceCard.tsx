import { Phone, MapPin, Globe, ExternalLink } from 'lucide-react';
import { Resource } from '../types';
import { useApp } from '../context/AppContext';

interface ResourceCardProps {
  resource: Resource;
}

export const ResourceCard = ({ resource }: ResourceCardProps) => {
  const { language } = useApp();

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-semibold text-gray-900">{resource.name}</h4>
        {resource.isOurJourney && (
          <span className="bg-[#E8F5E9] text-[#1B5E20] text-xs px-2 py-1 rounded-full ml-2 whitespace-nowrap">
            {language === 'en' ? 'OurJourney' : 'OurJourney'}
          </span>
        )}
      </div>
      
      <p className="text-sm text-gray-600 mb-3">{resource.description}</p>
      
      <div className="space-y-2">
        {resource.phone && (
          <a
            href={`tel:${resource.phone}`}
            className="flex items-center gap-2 text-sm text-[#388E3C] hover:text-[#1B5E20]"
          >
            <Phone className="w-4 h-4" />
            <span>{resource.phone}</span>
          </a>
        )}
        
        {resource.address && (
          <a
            href={`https://maps.google.com/?q=${encodeURIComponent(resource.address)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-[#388E3C] hover:text-[#1B5E20]"
          >
            <MapPin className="w-4 h-4" />
            <span>{resource.address}</span>
          </a>
        )}
        
        {resource.website && (
          <a
            href={resource.website}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-[#388E3C] hover:text-[#1B5E20]"
          >
            <Globe className="w-4 h-4" />
            <span className="flex-1 truncate">{language === 'en' ? 'Visit Website' : 'Visitar Sitio Web'}</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
};
