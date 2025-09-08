export interface ApiConfig {
  baseURL: string;
  timeout: number;
}

export interface HttpError extends Error {
  status: number;
  statusText: string;
  data?: unknown;
}

export interface PaginatedResponse<T> {
  data: T[];
  count: number;
}

export interface ApiMessage {
  message: string;
}
