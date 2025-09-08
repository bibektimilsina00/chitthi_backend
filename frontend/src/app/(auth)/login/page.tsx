"use client";

import Link from "next/link";
import Button from "@/components/ui/button";
import Input from "@/components/ui/input";
import Alert from "@/components/ui/alert";
import { useAuthForm } from "@/hooks/use-form";
import { loginSchema, type LoginFormData } from "@/lib/validations/auth";
import { authService } from "@/lib/auth";
import { navigationService } from "@/lib/navigation";
import { ROUTES } from "@/lib/routes";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const {
    register,
    formState: { errors },
    isSubmitting,
    submitError,
    onSubmit,
  } = useAuthForm<LoginFormData>({
    schema: loginSchema,
    onSubmit: async (data) => {
      await authService.login({
        username: data.email, // Map email to username for backend
        password: data.password,
      });
      navigationService.navigate(ROUTES.DASHBOARD);
    },
  });

  return (
    <div
      className={cn(
        "w-full max-w-md space-y-8 p-8",
        "bg-white rounded-lg shadow-md",
        "border border-gray-200"
      )}
    >
      <div className="text-center">
        <h1 className={cn("text-3xl font-bold", "text-gray-900")}>Sign In</h1>
        <p className={cn("mt-2 text-sm", "text-gray-600")}>
          Welcome back to Chitthi
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-6">
        {submitError && <Alert variant="error">{submitError}</Alert>}

        <div className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className={cn("block text-sm font-medium mb-2", "text-gray-700")}
            >
              Email Address
            </label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="Enter your email"
              error={errors.email?.message as string | undefined}
              {...register("email")}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className={cn("block text-sm font-medium mb-2", "text-gray-700")}
            >
              Password
            </label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              error={errors.password?.message as string | undefined}
              {...register("password")}
            />
          </div>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          className="w-full"
          loading={isSubmitting}
          disabled={isSubmitting}
        >
          {isSubmitting ? "Signing In..." : "Sign In"}
        </Button>

        <div className={cn("text-center space-y-2 text-sm", "text-gray-600")}>
          <Link
            href={ROUTES.FORGOT_PASSWORD}
            className={cn(
              "text-blue-600 hover:text-blue-700",
              "font-medium transition-colors"
            )}
          >
            Forgot your password?
          </Link>

          <div>
            Don&apos;t have an account?{" "}
            <Link
              href={ROUTES.REGISTER}
              className={cn(
                "text-blue-600 hover:text-blue-700",
                "font-medium transition-colors"
              )}
            >
              Sign up
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}
