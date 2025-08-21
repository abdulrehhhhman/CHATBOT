import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, History, Trash2, Bot, Sparkles } from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';
import { useAuth } from '../../contexts/AuthContext';
import { MessageBubble } from './MessageBubble';
import { DocumentSources } from './DocumentSources';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

export const ChatInterface: React.FC = () => {
  const { user } = useAuth();
  const { 
    messages, 
    sources, 
    isLoading, 
    sendMessage, 
    loadChatHistory, 
    clearChat,
    currentConversation 
  } = useChat();

  const [inputMessage, setInputMessage] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (user) {
      loadChatHistory();
    }
  }, [user, loadChatHistory]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');

    try {
      await sendMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Could show error toast here
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="flex items-center justify-between p-6 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">AI Learning Assistant</h2>
            <p className="text-sm text-gray-600 flex items-center">
              <Sparkles className="w-4 h-4 mr-1 text-yellow-500" />
              Enhanced with RAG technology
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            onClick={() => setShowHistory(!showHistory)}
            variant="outline"
            size="sm"
            icon={<History className="w-4 h-4" />}
          >
            History
          </Button>
          
          <Button
            onClick={clearChat}
            variant="outline"
            size="sm"
            icon={<Trash2 className="w-4 h-4" />}
          >
            Clear
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Bot className="w-10 h-10 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Welcome to your AI Learning Assistant!
            </h3>
            <p className="text-gray-600 max-w-md mx-auto">
              I'm here to help you learn and understand your course materials. 
              Ask me anything or upload documents for personalized assistance.
            </p>
            
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              <div className="p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white/20">
                <h4 className="font-medium text-gray-900 mb-2">🤖 General Questions</h4>
                <p className="text-sm text-gray-600">Ask about any topic and I'll provide detailed explanations</p>
              </div>
              <div className="p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white/20">
                <h4 className="font-medium text-gray-900 mb-2">📚 Document-Based</h4>
                <p className="text-sm text-gray-600">Upload PDFs and ask specific questions about your materials</p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((chat) => (
              <MessageBubble key={chat.id} chat={chat} />
            ))}
            
            {sources.length > 0 && (
              <DocumentSources sources={sources} />
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2 p-4 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg">
                  <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white/80 backdrop-blur-sm border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex items-end space-x-4">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your studies or course materials..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors resize-none"
              rows={1}
              style={{ 
                minHeight: '44px',
                maxHeight: '120px',
                overflow: 'auto'
              }}
            />
          </div>
          
          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={!inputMessage.trim() || isLoading}
            isLoading={isLoading}
            icon={<Send className="w-5 h-5" />}
            className="h-11"
          >
            Send
          </Button>
        </form>

        {/* Quick Actions */}
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            onClick={() => setInputMessage("Explain the concept of...")}
            className="px-3 py-1.5 bg-blue-100 hover:bg-blue-200 text-blue-700 text-sm rounded-full transition-colors"
          >
            💡 Explain concept
          </button>
          <button
            onClick={() => setInputMessage("Can you help me understand...")}
            className="px-3 py-1.5 bg-green-100 hover:bg-green-200 text-green-700 text-sm rounded-full transition-colors"
          >
            ❓ Help understand
          </button>
          <button
            onClick={() => setInputMessage("What are the key points about...")}
            className="px-3 py-1.5 bg-purple-100 hover:bg-purple-200 text-purple-700 text-sm rounded-full transition-colors"
          >
            📝 Key points
          </button>
          <button
            onClick={() => setInputMessage("Give me examples of...")}
            className="px-3 py-1.5 bg-orange-100 hover:bg-orange-200 text-orange-700 text-sm rounded-full transition-colors"
          >
            🌟 Examples
          </button>
        </div>
      </div>
    </div>
  );
};