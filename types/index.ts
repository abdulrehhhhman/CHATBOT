// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: 'student' | 'instructor' | 'admin';
  created_at?: string;
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Chat Types
export interface ChatMessage {
  message: string;
  user_id: number;
  course_id?: number;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id?: string;
  sources?: string[];
}

export interface ChatHistory {
  id: number;
  user_message: string;
  ai_response: string;
  conversation_id: string;
  context_type: string;
  created_at: string;
  response_time: string;
  course_id?: number;
  rating?: number;
  has_rag_context: boolean;
}

// Course Types
export interface Course {
  id: number;
  title: string;
  description?: string;
  course_code: string;
  instructor_id: number;
  semester?: string;
  credits: number;
  is_active: boolean;
  enrollment_open: boolean;
  created_at: string;
}

export interface CourseMaterial {
  id: number;
  filename: string;
  upload_date: string;
  file_size: number;
  is_processed: boolean;
  description?: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  success?: boolean;
  message?: string;
  data?: T;
  error?: string;
}

// Chat Context Types
export interface ChatState {
  messages: ChatHistory[];
  currentConversation?: string;
  isLoading: boolean;
  sources: string[];
}

export interface DocumentUploadResponse {
  success: boolean;
  message: string;
  course_id?: number;
  chunks_created?: number;
  text_length?: number;
}