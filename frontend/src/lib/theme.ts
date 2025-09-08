/**
 * Centralized design system and theme configuration
 */

// Color palette
export const colors = {
  // Primary colors
  primary: {
    50: "#eef2ff",
    100: "#e0e7ff",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
  },

  // Semantic colors
  success: {
    50: "#f0fdf4",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
  },

  error: {
    50: "#fef2f2",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
  },

  warning: {
    50: "#fffbeb",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
  },

  // Neutral colors
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
  },
} as const;

// Typography scale
export const typography = {
  fontFamily: {
    sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
    mono: ["var(--font-geist-mono)", "monospace"],
  },

  fontSize: {
    xs: ["0.75rem", { lineHeight: "1rem" }],
    sm: ["0.875rem", { lineHeight: "1.25rem" }],
    base: ["1rem", { lineHeight: "1.5rem" }],
    lg: ["1.125rem", { lineHeight: "1.75rem" }],
    xl: ["1.25rem", { lineHeight: "1.75rem" }],
    "2xl": ["1.5rem", { lineHeight: "2rem" }],
    "3xl": ["1.875rem", { lineHeight: "2.25rem" }],
  },

  fontWeight: {
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },
} as const;

// Spacing scale
export const spacing = {
  0: "0px",
  1: "0.25rem",
  2: "0.5rem",
  3: "0.75rem",
  4: "1rem",
  5: "1.25rem",
  6: "1.5rem",
  8: "2rem",
  10: "2.5rem",
  12: "3rem",
  16: "4rem",
  20: "5rem",
  24: "6rem",
} as const;

// Border radius
export const borderRadius = {
  none: "0px",
  sm: "0.125rem",
  DEFAULT: "0.25rem",
  md: "0.375rem",
  lg: "0.5rem",
  xl: "0.75rem",
  "2xl": "1rem",
  full: "9999px",
} as const;

// Shadows
export const boxShadow = {
  sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
  DEFAULT: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
  md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  xl: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
} as const;

// Animation durations
export const animation = {
  duration: {
    fast: "150ms",
    normal: "250ms",
    slow: "350ms",
  },

  easing: {
    ease: "cubic-bezier(0.4, 0, 0.2, 1)",
    "ease-in": "cubic-bezier(0.4, 0, 1, 1)",
    "ease-out": "cubic-bezier(0, 0, 0.2, 1)",
    "ease-in-out": "cubic-bezier(0.4, 0, 0.2, 1)",
  },
} as const;

// Component variants
export const variants = {
  button: {
    sizes: {
      sm: "h-9 px-3 text-sm",
      md: "h-10 px-4 text-sm",
      lg: "h-11 px-8 text-base",
    },

    colors: {
      primary: {
        solid: `bg-primary-600 text-white hover:bg-primary-500 focus-visible:ring-primary-600`,
        outline: `border border-primary-300 bg-white text-primary-700 hover:bg-primary-50 focus-visible:ring-primary-600`,
        ghost: `text-primary-700 hover:bg-primary-100 focus-visible:ring-primary-600`,
      },
      success: {
        solid: `bg-success-600 text-white hover:bg-success-500 focus-visible:ring-success-600`,
        outline: `border border-success-300 bg-white text-success-700 hover:bg-success-50 focus-visible:ring-success-600`,
        ghost: `text-success-700 hover:bg-success-100 focus-visible:ring-success-600`,
      },
      error: {
        solid: `bg-error-600 text-white hover:bg-error-500 focus-visible:ring-error-600`,
        outline: `border border-error-300 bg-white text-error-700 hover:bg-error-50 focus-visible:ring-error-600`,
        ghost: `text-error-700 hover:bg-error-100 focus-visible:ring-error-600`,
      },
      neutral: {
        solid: `bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-600`,
        outline: `border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-600`,
        ghost: `text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-600`,
      },
    },
  },

  input: {
    sizes: {
      sm: "h-9 px-3 text-sm",
      md: "h-10 px-3 text-sm",
      lg: "h-11 px-4 text-base",
    },

    states: {
      default: "ring-gray-300 focus:ring-primary-600",
      error: "ring-error-300 focus:ring-error-500",
      success: "ring-success-300 focus:ring-success-500",
    },
  },
} as const;

// Utility function to get theme values
export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  boxShadow,
  animation,
  variants,
} as const;

export type Theme = typeof theme;
export type ColorPalette = typeof colors;
export type Typography = typeof typography;
export type Spacing = typeof spacing;
