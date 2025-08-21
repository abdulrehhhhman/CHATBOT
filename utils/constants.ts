export const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  ME: '/auth/me',
  
  // Chat
  CHAT_MESSAGE: '/chat/message',
  CHAT_HISTORY: '/chat/history',
  CHAT_TEST: '/chat/test',
  
  // Courses/Documents
  UPLOAD_DOCUMENT: '/chat/upload-document',
  USER_DOCUMENTS: '/chat/user-documents',
  
  // Test endpoints
  TEST_DATABASE: '/test-database',
  TEST_GEMINI: '/test-gemini',
  TEST_PINECONE: '/test-pinecone',
} as const;

export const USER_ROLES = {
  STUDENT: 'student',
  INSTRUCTOR: 'instructor',
  ADMIN: 'admin',
} as const;

export const CHAT_CONTEXT_TYPES = {
  GENERAL: 'general',
  RAG: 'rag',
  COURSE_SPECIFIC: 'course_specific',
} as const;

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  CURRENT_CONVERSATION: 'current_conversation',
} as const;

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const ALLOWED_FILE_TYPES = ['application/pdf'];

export const COLORS = {
  primary: {
    50: '#eff6ff',
    100: '#dbeafe', 
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },
  secondary: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0', 
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  }
};