import React from 'react';
import { User, Bot, Clock, BookOpen } from 'lucide-react';
import type { ChatHistory } from '../../types';

interface MessageBubbleProps {
  chat: ChatHistory;
  isLatest?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ chat, isLatest }) => {
  return (
    <div className="space-y-4">
      {/* User Message */}
      <div className="flex justify-end">
        <div className="flex items-end space-x-2 max-w-3xl">
          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4 rounded-2xl rounded-br-md shadow-lg">
            <p className="text-sm leading-relaxed">{chat.user_message}</p>
          </div>
          <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
            <User className="w-4 h-4 text-white" />
          </div>
        </div>
      </div>

      {/* AI Response */}
      <div className="flex justify-start">
        <div className="flex items-end space-x-2 max-w-3xl">
          <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div className="bg-white/80 backdrop-blur-sm p-4 rounded-2xl rounded-bl-md shadow-lg border border-gray-200">
            <div className="flex items-center space-x-2 mb-2">
              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                chat.has_rag_context 
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {chat.has_rag_context ? (
                  <>
                    <BookOpen className="w-3 h-3 mr-1" />
                    Document-based
                  </>
                ) : (
                  <>
                    <Bot className="w-3 h-3 mr-1" />
                    AI Knowledge
                  </>
                )}
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <Clock className="w-3 h-3 mr-1" />
                {new Date(chat.created_at).toLocaleTimeString()}
              </div>
            </div>
            
            <p className="text-sm leading-relaxed text-gray-800 whitespace-pre-wrap">
              {chat.ai_response}
            </p>

            {/* Rating (if available) */}
            {chat.rating && (
              <div className="mt-3 flex items-center space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <span
                    key={star}
                    className={`text-sm ${
                      star <= chat.rating! ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                  >
                    ★
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};