import React, { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { DashboardContent } from '../dashboard/DashboardContent';
import { ChatInterface } from '../chat/ChatInterface';
import { DocumentsPage } from '../documents/DocumentsPage';
import { UploadPage } from '../documents/UploadPage';

export const Layout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardContent />;
      case 'chat':
        return <ChatInterface />;
      case 'documents':
        return <DocumentsPage />;
      case 'upload':
        return <UploadPage onUploadSuccess={() => setActiveTab('documents')} />;
      case 'courses':
        return <div className="p-6"><h2 className="text-2xl font-bold">Courses</h2><p className="text-gray-600">Courses management coming soon...</p></div>;
      case 'students':
        return <div className="p-6"><h2 className="text-2xl font-bold">Students</h2><p className="text-gray-600">Student management coming soon...</p></div>;
      case 'users':
        return <div className="p-6"><h2 className="text-2xl font-bold">Users</h2><p className="text-gray-600">User management coming soon...</p></div>;
      case 'analytics':
        return <div className="p-6"><h2 className="text-2xl font-bold">Analytics</h2><p className="text-gray-600">Analytics dashboard coming soon...</p></div>;
      case 'settings':
        return <div className="p-6"><h2 className="text-2xl font-bold">Settings</h2><p className="text-gray-600">Settings page coming soon...</p></div>;
      default:
        return <DashboardContent />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <Header />
      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <main className="flex-1 overflow-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};