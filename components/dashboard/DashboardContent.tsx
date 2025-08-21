import React, { useEffect, useState } from 'react';
import { 
  MessageSquare, 
  FileText, 
  Upload, 
  Brain, 
  TrendingUp,
  Clock,
  CheckCircle,
  Users
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../contexts/ChatContext';
import { documentService } from '../../services/documents';
import { chatService } from '../../services/chat';
import type { CourseMaterial } from '../../types';

export const DashboardContent: React.FC = () => {
  const { user } = useAuth();
  const { messages } = useChat();
  const [documents, setDocuments] = useState<CourseMaterial[]>([]);
  const [stats, setStats] = useState({
    totalChats: 0,
    documentsUploaded: 0,
    ragQueries: 0,
    systemStatus: 'checking...'
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [user]);

  const loadDashboardData = async () => {
    if (!user) return;

    try {
      setIsLoading(true);

      // Load user documents
      const docsResponse = await documentService.getUserDocuments(user.id);
      setDocuments(docsResponse.documents);

      // Load chat history for stats
      const chatHistory = await chatService.testChatService();
      
      // Test system status
      const systemTest = await chatService.testChatService();

      setStats({
        totalChats: messages.length,
        documentsUploaded: docsResponse.documents.length,
        ragQueries: messages.filter(m => m.has_rag_context).length,
        systemStatus: systemTest.status === 'success' ? 'operational' : 'issues'
      });

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getWelcomeMessage = () => {
    switch (user?.role) {
      case 'admin':
        return 'Welcome to your admin dashboard. Monitor system performance and manage users.';
      case 'instructor':
        return 'Welcome to your instructor dashboard. Manage your courses and students.';
      case 'student':
        return 'Welcome to your learning dashboard. Start chatting with AI or upload study materials.';
      default:
        return 'Welcome to your LMS dashboard.';
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    description?: string;
  }> = ({ title, value, icon, color, description }) => (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-3xl font-bold ${color} mt-2`}>{value}</p>
          {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
        </div>
        <div className={`p-3 rounded-xl ${color.replace('text-', 'bg-').replace('-600', '-100')}`}>
          {icon}
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-2xl"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Welcome Section */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-2 h-8 bg-gradient-to-b from-blue-500 to-indigo-600 rounded-full"></div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name || user?.username}!
          </h1>
        </div>
        <p className="text-gray-600 ml-5">{getWelcomeMessage()}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Conversations"
          value={stats.totalChats}
          icon={<MessageSquare className="w-6 h-6" />}
          color="text-blue-600"
          description="AI chat sessions"
        />
        
        <StatCard
          title="Documents Uploaded"
          value={stats.documentsUploaded}
          icon={<FileText className="w-6 h-6" />}
          color="text-green-600"
          description="PDFs ready for RAG"
        />
        
        <StatCard
          title="RAG Queries"
          value={stats.ragQueries}
          icon={<Brain className="w-6 h-6" />}
          color="text-purple-600"
          description="Document-based answers"
        />
        
        <StatCard
          title="System Status"
          value={stats.systemStatus === 'operational' ? 'Online' : 'Issues'}
          icon={<CheckCircle className="w-6 h-6" />}
          color={stats.systemStatus === 'operational' ? 'text-green-600' : 'text-red-600'}
          description="AI services"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Recent Activity */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-blue-600" />
            Recent Activity
          </h3>
          
          {messages.length > 0 ? (
            <div className="space-y-3">
              {messages.slice(-3).map((chat, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <MessageSquare className="w-4 h-4 text-gray-400 mt-1 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 truncate">
                      {chat.user_message}
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        chat.has_rag_context ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {chat.has_rag_context ? '📚 RAG' : '🤖 AI'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(chat.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No chat history yet</p>
              <p className="text-sm text-gray-400">Start a conversation to see activity here</p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            Quick Actions
          </h3>
          
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-xl transition-all duration-200 group">
              <div className="flex items-center">
                <MessageSquare className="w-5 h-5 text-blue-600 mr-3" />
                <span className="font-medium text-gray-900">Start AI Chat</span>
              </div>
              <span className="text-blue-600 group-hover:translate-x-1 transition-transform">→</span>
            </button>
            
            <button className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 rounded-xl transition-all duration-200 group">
              <div className="flex items-center">
                <Upload className="w-5 h-5 text-green-600 mr-3" />
                <span className="font-medium text-gray-900">Upload Document</span>
              </div>
              <span className="text-green-600 group-hover:translate-x-1 transition-transform">→</span>
            </button>
            
            <button className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 rounded-xl transition-all duration-200 group">
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-purple-600 mr-3" />
                <span className="font-medium text-gray-900">View Documents</span>
              </div>
              <span className="text-purple-600 group-hover:translate-x-1 transition-transform">→</span>
            </button>

            {user?.role === 'instructor' && (
              <button className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-red-50 hover:from-orange-100 hover:to-red-100 rounded-xl transition-all duration-200 group">
                <div className="flex items-center">
                  <Users className="w-5 h-5 text-orange-600 mr-3" />
                  <span className="font-medium text-gray-900">Manage Students</span>
                </div>
                <span className="text-orange-600 group-hover:translate-x-1 transition-transform">→</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Recent Documents */}
      {documents.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-gray-600" />
            Recent Documents
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.slice(0, 6).map((doc) => (
              <div key={doc.id} className="flex items-center space-x-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {doc.filename}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      doc.is_processed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {doc.is_processed ? '✓ Processed' : '⏳ Processing'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};