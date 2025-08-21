import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { chatService } from '../services/chat';
import { useAuth } from './AuthContext';
import type { ChatHistory, ChatMessage, ChatResponse, ChatState } from '../types';

interface ChatContextType extends ChatState {
  sendMessage: (message: string, courseId?: number) => Promise<void>;
  loadChatHistory: (courseId?: number, conversationId?: string) => Promise<void>;
  clearChat: () => void;
  setCurrentConversation: (conversationId?: string) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatHistory[]>([]);
  const [currentConversation, setCurrentConversationState] = useState<string>();
  const [isLoading, setIsLoading] = useState(false);
  const [sources, setSources] = useState<string[]>([]);

  const sendMessage = useCallback(async (message: string, courseId?: number) => {
    if (!user) throw new Error('User not authenticated');

    setIsLoading(true);
    try {
      const chatMessage: ChatMessage = {
        message,
        user_id: user.id,
        course_id: courseId,
        conversation_id: currentConversation,
      };

      const response: ChatResponse = await chatService.sendMessage(chatMessage);
      
      // Update current conversation ID if we got a new one
      if (response.conversation_id) {
        setCurrentConversationState(response.conversation_id);
      }

      // Update sources if available
      if (response.sources) {
        setSources(response.sources);
      }

      // Add the new message exchange to the messages array
      const newChatEntry: ChatHistory = {
        id: Date.now(), // Temporary ID
        user_message: message,
        ai_response: response.response,
        conversation_id: response.conversation_id || currentConversation || '',
        context_type: response.sources && response.sources.length > 0 ? 'rag' : 'general',
        created_at: new Date().toISOString(),
        response_time: new Date().toISOString(),
        course_id: courseId,
        has_rag_context: (response.sources && response.sources.length > 0) || false,
      };

      setMessages(prev => [...prev, newChatEntry]);
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user, currentConversation]);

  const loadChatHistory = useCallback(async (courseId?: number, conversationId?: string) => {
    if (!user) return;

    setIsLoading(true);
    try {
      const response = await chatService.getChatHistory(
        user.id,
        courseId,
        conversationId,
        50
      );
      
      // Reverse to show oldest first
      setMessages(response.chats.reverse());
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setSources([]);
    setCurrentConversationState(undefined);
  }, []);

  const setCurrentConversation = useCallback((conversationId?: string) => {
    setCurrentConversationState(conversationId);
  }, []);

  const value: ChatContextType = {
    messages,
    currentConversation,
    isLoading,
    sources,
    sendMessage,
    loadChatHistory,
    clearChat,
    setCurrentConversation,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};