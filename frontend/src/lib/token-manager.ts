/**
 * Secure token management service with proper abstraction
 */

// Storage interface for dependency injection
interface TokenStorage {
  getToken(): string | null;
  setToken(token: string): void;
  removeToken(): void;
}

// Browser localStorage implementation
class BrowserTokenStorage implements TokenStorage {
  private readonly TOKEN_KEY = "auth_token";

  getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(this.TOKEN_KEY);
  }

  setToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  removeToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem(this.TOKEN_KEY);
  }
}

export class TokenManager {
  private storage: TokenStorage;

  constructor(storage: TokenStorage = new BrowserTokenStorage()) {
    this.storage = storage;
  }

  /**
   * Store token securely
   */
  setToken(token: string): void {
    if (!token || typeof token !== "string") {
      throw new Error("Invalid token provided");
    }
    this.storage.setToken(token);
  }

  /**
   * Get stored token
   */
  getStoredToken(): string | null {
    return this.storage.getToken();
  }

  /**
   * Get valid token (non-expired)
   */
  getValidToken(): string | null {
    const token = this.getStoredToken();
    if (!token || this.isTokenExpired(token)) {
      return null;
    }
    return token;
  }

  /**
   * Remove token from storage
   */
  removeToken(): void {
    this.storage.removeToken();
  }

  /**
   * Check if user is authenticated (has valid token)
   */
  isAuthenticated(): boolean {
    return this.getValidToken() !== null;
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(token: string): boolean {
    try {
      const parts = token.split(".");
      if (parts.length !== 3 || !parts[1]) {
        return true;
      }
      const payload = JSON.parse(atob(parts[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch {
      return true;
    }
  }

  /**
   * Check if token is expiring soon (within 5 minutes)
   */
  isTokenExpiringSoon(): boolean {
    const token = this.getStoredToken();
    if (!token) return false;

    try {
      const parts = token.split(".");
      if (parts.length !== 3 || !parts[1]) {
        return true;
      }
      const payload = JSON.parse(atob(parts[1]));
      const currentTime = Date.now() / 1000;
      const expiryTime = payload.exp;
      const timeUntilExpiry = expiryTime - currentTime;

      return timeUntilExpiry < 300; // 5 minutes
    } catch {
      return true;
    }
  }

  /**
   * Get token payload (decoded JWT payload)
   */
  getTokenPayload(): Record<string, unknown> | null {
    const token = this.getStoredToken();
    if (!token) return null;

    try {
      const parts = token.split(".");
      if (parts.length !== 3 || !parts[1]) {
        return null;
      }
      return JSON.parse(atob(parts[1]));
    } catch {
      return null;
    }
  }

  /**
   * Clear all authentication data
   */
  clearAuthData(): void {
    this.removeToken();
  }
}

// Export singleton instance
export const tokenManager = new TokenManager();
