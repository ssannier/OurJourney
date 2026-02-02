import { useState } from 'react';
import { useNavigate, Link, Outlet, useLocation } from 'react-router-dom';
import { MessageSquare, Users, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';

export const AdminDashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      {/* Header */}
      <div className="bg-[#1B5E20] text-white p-4 shadow-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/chat')}
              className="text-white hover:bg-[#388E3C]"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-xl font-semibold">JoJo Admin Dashboard</h1>
          </div>
          <p className="text-sm text-green-100">OurJourney</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto">
          <nav className="flex gap-1 p-2">
            <Link
              to="/admin/conversations"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/admin/conversations')
                  ? 'bg-[#E8F5E9] text-[#1B5E20] font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              Conversations
            </Link>
            <Link
              to="/admin/followup"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/admin/followup')
                  ? 'bg-[#E8F5E9] text-[#1B5E20] font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Users className="w-4 h-4" />
              Follow-Up Queue
            </Link>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-6">
        <Outlet />
      </div>
    </div>
  );
};