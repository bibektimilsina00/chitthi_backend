import apiClient from "./api-client";
import { tokenManager } from "./token-manager";
import {
  LoginCredentials,
  RegisterData,
  Token,
  User,
  UpdateUserProfile,
  UpdatePassword,
  PasswordReset,
} from "@/types/auth";
import { ApiMessage } from "@/types/api";

export class AuthService {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<Token> {
    const token = await apiClient.postForm<Token>("/login/access-token", {
      username: credentials.username, // backend expects email as username
      password: credentials.password,
    });

    // Store the token using token manager
    tokenManager.setToken(token.access_token);

    return token;
  }

  /**
   * Register a new user
   */
  async register(userData: RegisterData): Promise<User> {
    return apiClient.post<User>("/users/signup", userData);
  }

  /**
   * Get current user profile (test token)
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.post<User>("/login/test-token");
  }

  /**
   * Update current user profile
   */
  async updateProfile(profileData: UpdateUserProfile): Promise<User> {
    return apiClient.patch<User>("/users/me", profileData);
  }

  /**
   * Update current user password
   */
  async updatePassword(passwordData: UpdatePassword): Promise<ApiMessage> {
    return apiClient.patch<ApiMessage>("/users/me/password", passwordData);
  }

  /**
   * Request password recovery
   */
  async requestPasswordReset(email: string): Promise<ApiMessage> {
    return apiClient.post<ApiMessage>(
      `/password-recovery/${encodeURIComponent(email)}`
    );
  }

  /**
   * Reset password with token
   */
  async resetPassword(resetData: PasswordReset): Promise<ApiMessage> {
    return apiClient.post<ApiMessage>("/reset-password/", resetData);
  }

  /**
   * Logout - remove token from storage
   */
  logout(): void {
    tokenManager.removeToken();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return tokenManager.isAuthenticated();
  }

  /**
   * Get stored token
   */
  getToken(): string | null {
    return tokenManager.getValidToken();
  }

  /**
   * Check if token is expiring soon
   */
  isTokenExpiringSoon(): boolean {
    return tokenManager.isTokenExpiringSoon();
  }

  /**
   * Get user ID from token payload
   */
  getUserIdFromToken(): string | null {
    const payload = tokenManager.getTokenPayload();
    return (payload?.sub as string) || null;
  }
}

// Export singleton instance
export const authService = new AuthService();
