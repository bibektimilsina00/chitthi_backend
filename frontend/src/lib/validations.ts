import { z } from "zod";

// Login form validation
export const loginSchema = z.object({
  username: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  password: z
    .string()
    .min(1, "Password is required")
    .min(8, "Password must be at least 8 characters"),
});

// Registration form validation
export const registerSchema = z
  .object({
    username: z
      .string()
      .min(1, "Username is required")
      .max(64, "Username must be at most 64 characters")
      .regex(
        /^[a-zA-Z0-9_]+$/,
        "Username can only contain letters, numbers, and underscores"
      ),
    email: z
      .string()
      .email("Please enter a valid email address")
      .max(255, "Email must be at most 255 characters")
      .optional()
      .or(z.literal("")),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(128, "Password must be at most 128 characters"),
    confirmPassword: z.string().min(1, "Please confirm your password"),
    display_name: z
      .string()
      .max(128, "Display name must be at most 128 characters")
      .optional()
      .or(z.literal("")),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

// Forgot password form validation
export const forgotPasswordSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
});

// Reset password form validation
export const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(128, "Password must be at most 128 characters"),
    confirmPassword: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

// Update password form validation
export const updatePasswordSchema = z
  .object({
    current_password: z.string().min(1, "Current password is required"),
    new_password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(128, "Password must be at most 128 characters"),
    confirmPassword: z.string().min(1, "Please confirm your new password"),
  })
  .refine((data) => data.new_password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })
  .refine((data) => data.current_password !== data.new_password, {
    message: "New password must be different from current password",
    path: ["new_password"],
  });

// Update profile form validation
export const updateProfileSchema = z.object({
  display_name: z
    .string()
    .max(128, "Display name must be at most 128 characters")
    .optional()
    .or(z.literal("")),
  about: z.string().optional().or(z.literal("")),
  avatar_url: z
    .string()
    .url("Please enter a valid URL")
    .optional()
    .or(z.literal("")),
  locale: z
    .string()
    .max(16, "Locale must be at most 16 characters")
    .optional()
    .or(z.literal("")),
  timezone: z
    .string()
    .max(64, "Timezone must be at most 64 characters")
    .optional()
    .or(z.literal("")),
});

// Type inference from schemas
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
export type UpdatePasswordFormData = z.infer<typeof updatePasswordSchema>;
export type UpdateProfileFormData = z.infer<typeof updateProfileSchema>;
