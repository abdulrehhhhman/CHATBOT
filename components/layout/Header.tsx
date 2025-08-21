import React from 'react';
import { LogOut, User, Settings, Bell, GraduationCap } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/Button';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();

  const getRoleIcon = () => {
    switch (user?.role) {
      case 'admin':
        return '⚡';
      case 'instructor':
        return '🎓';
      case 'student':
        return '📚';
      default:
        return '👤';
    }
  };

  const getRoleColor = () => {
    switch (user?.role) {
      case 'admin':
        return 'text-purple-600 bg-purple-100';
      case 'instructor':
        return 'text-blue-600 bg-blue-100';
      case 'student':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">LMS Chatbot</h1>
              <p className="text-xs text-gray-500">AI-Powered Learning</p>
            </div>
          </div>

          {/* User Section */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-100">
              <Bell className="w-5 h-5" />
            </button>

            {/* User Info */}
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user?.full_name || user?.username}
                </p>
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRoleColor()}`}>
                  <span className="mr-1">{getRoleIcon()}</span>
                  {user?.role}
                </div>
              </div>

              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>

              {/* Settings Menu */}
              <div className="flex items-center space-x-1">
                <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-100">
                  <Settings className="w-5 h-5" />
                </button>

                <Button
                  onClick={logout}
                  variant="ghost"
                  size="sm"
                  icon={<LogOut className="w-4 h-4" />}
                >
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};