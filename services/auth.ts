import { apiService } from './api';
import { API_ENDPOINTS, STORAGE_KEYS } from '../utils/constants';
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '../types';

class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>(API_ENDPOINTS.LOGIN, credentials);
    this.saveAuthData(response);
    return response;
  }

  async register(userData: RegisterRequest): Promise<{ message: string; user: User }> {
    return apiService.post(API_ENDPOINTS.REGISTER, userData);
  }

  async getCurrentUser(): Promise<User> {
    return apiService.get<User>(API_ENDPOINTS.ME);
  }

  private saveAuthData(authResponse: AuthResponse): void {
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, authResponse.access_token);
    localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(authResponse.user));
  }

  getStoredUser(): User | null {
    const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    return userData ? JSON.parse(userData) : null;
  }

  getStoredToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
  }

  isAuthenticated(): boolean {
    return !!this.getStoredToken();
  }

  logout(): void {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_CONVERSATION);
  }
}

export const authService = new AuthService();