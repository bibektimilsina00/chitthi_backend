/**
 * Centralized routing constants for type-safe navigation
 */
export const ROUTES = {
  // Public routes
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",

  // Protected routes
  DASHBOARD: "/dashboard",
  PROFILE: "/profile",
  SETTINGS: "/settings",

  // Future routes
  CHATS: "/chats",
  CONTACTS: "/contacts",
  CALLS: "/calls",
} as const;

export type RouteKey = keyof typeof ROUTES;
export type RouteValue = (typeof ROUTES)[RouteKey];

/**
 * Helper function to build routes with parameters
 */
export const buildRoute = (
  route: RouteValue,
  params?: Record<string, string>
): string => {
  if (!params) return route;

  let path: string = route;
  Object.entries(params).forEach(([key, value]) => {
    path = path.replace(`[${key}]`, value);
  });

  return path;
};

/**
 * Auth-related route checks
 */
export const isAuthRoute = (pathname: string): boolean => {
  const authRoutes = [
    ROUTES.LOGIN,
    ROUTES.REGISTER,
    ROUTES.FORGOT_PASSWORD,
    ROUTES.RESET_PASSWORD,
  ];
  return authRoutes.includes(
    pathname as
      | typeof ROUTES.LOGIN
      | typeof ROUTES.REGISTER
      | typeof ROUTES.FORGOT_PASSWORD
      | typeof ROUTES.RESET_PASSWORD
  );
};

export const isProtectedRoute = (pathname: string): boolean => {
  const protectedRoutes = [
    ROUTES.DASHBOARD,
    ROUTES.PROFILE,
    ROUTES.SETTINGS,
    ROUTES.CHATS,
    ROUTES.CONTACTS,
    ROUTES.CALLS,
  ];
  return protectedRoutes.some((route) => pathname.startsWith(route));
};
