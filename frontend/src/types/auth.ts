export interface LoginCredentials {
  username: string; // email in the backend
  password: string;
}

export interface RegisterData {
  username: string;
  email?: string;
  password: string;
  display_name?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  username: string;
  email?: string;
  phone?: string;
  display_name?: string;
  about?: string;
  avatar_url?: string;
  locale?: string;
  timezone?: string;
  is_active: boolean;
  is_bot: boolean;
  is_superuser: boolean;
  normalized_username: string;
  created_at: string;
  updated_at?: string;
}

export interface UpdateUserProfile {
  display_name?: string;
  about?: string;
  avatar_url?: string;
  locale?: string;
  timezone?: string;
}

export interface UpdatePassword {
  current_password: string;
  new_password: string;
}

export interface PasswordReset {
  token: string;
  new_password: string;
}

export interface ApiError {
  detail:
    | string
    | { type: string; loc: string[]; msg: string; input: unknown }[];
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}
