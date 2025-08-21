import { apiService } from './api';
import { API_ENDPOINTS } from '../utils/constants';
import type { ChatMessage, ChatResponse, ChatHistory } from '../types';

class ChatService {
  async sendMessage(message: ChatMessage): Promise<ChatResponse> {
    return apiService.post<ChatResponse>(API_ENDPOINTS.CHAT_MESSAGE, message);
  }

  async getChatHistory(
    userId: number,
    courseId?: number,
    conversationId?: string,
    limit: number = 50
  ): Promise<{ chats: ChatHistory[] }> {
    let endpoint = `${API_ENDPOINTS.CHAT_HISTORY}/${userId}?limit=${limit}`;
    
    if (courseId) {
      endpoint += `&course_id=${courseId}`;
    }
    
    if (conversationId) {
      endpoint += `&conversation_id=${conversationId}`;
    }

    return apiService.get<{ chats: ChatHistory[] }>(endpoint);
  }

  async testChatService(): Promise<any> {
    return apiService.get(API_ENDPOINTS.CHAT_TEST);
  }
}

export const chatService = new ChatService();