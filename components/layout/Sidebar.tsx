import React from 'react';
import { 
  MessageSquare, 
  Upload, 
  FileText, 
  BookOpen, 
  Users, 
  BarChart3,
  Home,
  Settings
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const { user } = useAuth();

  const getMenuItems = () => {
    const baseItems = [
      { id: 'dashboard', label: 'Dashboard', icon: Home },
      { id: 'chat', label: 'AI Chat', icon: MessageSquare },
      { id: 'documents', label: 'Documents', icon: FileText },
    ];

    if (user?.role === 'instructor') {
      baseItems.push(
        { id: 'courses', label: 'My Courses', icon: BookOpen },
        { id: 'students', label: 'Students', icon: Users }
      );
    }

    if (user?.role === 'admin') {
      baseItems.push(
        { id: 'courses', label: 'All Courses', icon: BookOpen },
        { id: 'users', label: 'Users', icon: Users },
        { id: 'analytics', label: 'Analytics', icon: BarChart3 }
      );
    }

    baseItems.push({ id: 'settings', label: 'Settings', icon: Settings });

    return baseItems;
  };

  const menuItems = getMenuItems();

  return (
    <aside className="w-64 bg-white/80 backdrop-blur-sm border-r border-gray-200 h-full">
      <div className="p-6">
        <nav className="space-y-2">
          {menuItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onTabChange(id)}
              className={`w-full flex items-center px-4 py-3 text-left rounded-xl transition-all duration-200 ${
                activeTab === id
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              <span className="font-medium">{label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Upload Section */}
      <div className="p-6 border-t border-gray-200">
        <button
          onClick={() => onTabChange('upload')}
          className="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-200 shadow-lg"
        >
          <Upload className="w-5 h-5 mr-2" />
          <span className="font-medium">Upload Document</span>
        </button>
      </div>
    </aside>
  );
};