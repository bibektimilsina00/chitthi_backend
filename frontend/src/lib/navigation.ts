import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";
import { ROUTES, RouteValue } from "./routes";

/**
 * Type-safe navigation utility for client-side routing
 */
export class NavigationService {
  private router: AppRouterInstance | null = null;

  setRouter(router: AppRouterInstance) {
    this.router = router;
  }

  /**
   * Navigate to a route with optional replacement
   */
  navigate(route: RouteValue, options: { replace?: boolean } = {}) {
    if (typeof window === "undefined") return;

    if (this.router) {
      if (options.replace) {
        this.router.replace(route);
      } else {
        this.router.push(route);
      }
    } else {
      // Fallback for cases where router is not available
      if (options.replace) {
        window.location.replace(route);
      } else {
        window.location.href = route;
      }
    }
  }

  /**
   * Simple push navigation (alias for navigate)
   */
  push(route: RouteValue) {
    this.navigate(route);
  }

  /**
   * Navigate to login page
   */
  navigateToLogin() {
    this.navigate(ROUTES.LOGIN, { replace: true });
  }

  /**
   * Navigate to dashboard
   */
  navigateToDashboard() {
    this.navigate(ROUTES.DASHBOARD, { replace: true });
  }

  /**
   * Navigate back in history
   */
  back() {
    if (typeof window !== "undefined" && window.history.length > 1) {
      window.history.back();
    } else {
      this.navigate(ROUTES.HOME);
    }
  }

  /**
   * Check if navigation is available
   */
  isAvailable(): boolean {
    return (
      typeof window !== "undefined" &&
      (this.router !== null || window.location !== undefined)
    );
  }
}

// Export singleton instance
export const navigationService = new NavigationService();
