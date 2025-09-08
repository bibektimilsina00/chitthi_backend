import useSWR from "swr";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { authService } from "@/lib/auth";
import { navigationService } from "@/lib/navigation";
import { User } from "@/types/auth";

/**
 * Hook to get current authenticated user
 */
export function useAuth() {
  const router = useRouter();

  // Set router for navigation service
  useEffect(() => {
    navigationService.setRouter(router);
  }, [router]);

  const {
    data: user,
    error,
    mutate,
    isLoading,
  } = useSWR<User>(
    authService.isAuthenticated() ? "/auth/me" : null,
    () => authService.getCurrentUser(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      shouldRetryOnError: false,
      onError: (error) => {
        // If there's an auth error, logout
        if (error?.status === 401) {
          authService.logout();
        }
      },
    }
  );

  return {
    user,
    isLoading,
    isAuthenticated: !!user && !error,
    error,
    mutate,
  };
}

/**
 * Hook for authentication actions
 */
export function useAuthActions() {
  const { mutate } = useAuth();

  const login = async (credentials: { username: string; password: string }) => {
    const token = await authService.login(credentials);
    // Trigger a re-fetch of user data
    await mutate();
    return token;
  };

  const logout = () => {
    authService.logout();
    // Clear the SWR cache for user data
    mutate(undefined, false);
    // Navigate to login page using navigation service
    navigationService.navigateToLogin();
  };

  const register = async (userData: {
    username: string;
    email?: string;
    password: string;
    display_name?: string;
  }) => {
    return authService.register(userData);
  };

  return {
    login,
    logout,
    register,
  };
}
