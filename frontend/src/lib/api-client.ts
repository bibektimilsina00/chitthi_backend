import axios, { AxiosInstance, AxiosError } from "axios";
import { ApiConfig, HttpError } from "@/types/api";

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

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const httpError: HttpError = new Error(error.message) as HttpError;
        httpError.status = error.response?.status || 0;
        httpError.statusText = error.response?.statusText || "";
        httpError.data = error.response?.data;

        // Handle 401 errors by removing token and redirecting to login
        if (httpError.status === 401) {
          this.removeToken();
          window.location.href = "/login";
        }

        return Promise.reject(httpError);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  }

  public setToken(token: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
    }
  }

  public removeToken(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
  }

  public get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    return this.client.get(url, { params }).then((response) => response.data);
  }

  public post<T>(url: string, data?: unknown): Promise<T> {
    return this.client.post(url, data).then((response) => response.data);
  }

  public patch<T>(url: string, data?: unknown): Promise<T> {
    return this.client.patch(url, data).then((response) => response.data);
  }

  public delete<T>(url: string): Promise<T> {
    return this.client.delete(url).then((response) => response.data);
  }

  // Special method for form data (login endpoint)
  public postForm<T>(url: string, data: Record<string, string>): Promise<T> {
    const formData = new URLSearchParams();
    Object.entries(data).forEach(([key, value]) => {
      formData.append(key, value);
    });

    return this.client
      .post(url, formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      })
      .then((response) => response.data);
  }
}

// Create and export a singleton instance
const apiClient = new ApiClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000/api/v1",
  timeout: 10000,
});

export default apiClient;
