import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from "axios";
import { ApiConfig, HttpError } from "@/types/api";
import { tokenManager } from "./token-manager";
import { navigationService } from "./navigation";

/**
 * Enhanced API client with better error handling and token management
 */
class ApiClient {
  private client: AxiosInstance;

  constructor(config: ApiConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = tokenManager.getValidToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(this.createHttpError(error))
    );

    // Response interceptor for error handling and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & {
          _retry?: boolean;
        };

        // Handle 401 errors
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          // Remove invalid token
          tokenManager.removeToken();

          // Redirect to login if navigation is available
          if (navigationService.isAvailable()) {
            navigationService.navigateToLogin();
          }

          return Promise.reject(this.createHttpError(error));
        }

        return Promise.reject(this.createHttpError(error));
      }
    );
  }

  private createHttpError(error: AxiosError): HttpError {
    const httpError = new Error(error.message) as HttpError;
    httpError.status = error.response?.status || 0;
    httpError.statusText = error.response?.statusText || "";
    httpError.data = error.response?.data;
    return httpError;
  }

  // HTTP Methods
  public async get<T>(
    url: string,
    params?: Record<string, unknown>
  ): Promise<T> {
    const response = await this.client.get(url, { params });
    return response.data;
  }

  public async post<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }

  public async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.patch(url, data);
    return response.data;
  }

  public async put<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.put(url, data);
    return response.data;
  }

  public async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete(url);
    return response.data;
  }

  // Special method for form data (OAuth2 endpoints)
  public async postForm<T>(
    url: string,
    data: Record<string, string>
  ): Promise<T> {
    const formData = new URLSearchParams();
    Object.entries(data).forEach(([key, value]) => {
      formData.append(key, value);
    });

    const response = await this.client.post(url, formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    return response.data;
  }

  // Method for file uploads
  public async postFile<T>(url: string, formData: FormData): Promise<T> {
    const response = await this.client.post(url, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  }

  // Get the base URL for external use
  public getBaseURL(): string {
    return this.client.defaults.baseURL || "";
  }

  // Method to update configuration
  public updateConfig(config: Partial<ApiConfig>): void {
    if (config.baseURL) {
      this.client.defaults.baseURL = config.baseURL;
    }
    if (config.timeout) {
      this.client.defaults.timeout = config.timeout;
    }
  }
}

// Create and export singleton instance
const apiClient = new ApiClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000/api/v1",
  timeout: 30000, // Increased timeout for better UX
});

export default apiClient;
