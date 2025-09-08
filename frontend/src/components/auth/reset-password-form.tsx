"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";

import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import Alert from "@/components/ui/alert";
import { authService } from "@/lib/auth";
import {
  resetPasswordSchema,
  type ResetPasswordFormData,
} from "@/lib/validations";
import { HttpError } from "@/types/api";

export default function ResetPasswordForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [token, setToken] = useState<string>("");

  const router = useRouter();
  const searchParams = useSearchParams();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  useEffect(() => {
    const tokenParam = searchParams.get("token");
    if (tokenParam) {
      setToken(tokenParam);
    } else {
      setError(
        "Invalid or missing reset token. Please request a new password reset."
      );
    }
  }, [searchParams]);

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      setError("Invalid or missing reset token.");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      setSuccess("");

      await authService.resetPassword({
        token,
        new_password: data.password,
      });

      setSuccess(
        "Password reset successfully! You can now sign in with your new password."
      );

      // Redirect to login after a delay
      setTimeout(() => {
        router.push("/login");
      }, 3000);
    } catch (err) {
      const httpError = err as HttpError;

      if (httpError.status === 400) {
        setError(
          "Invalid or expired reset token. Please request a new password reset."
        );
      } else if (httpError.status === 404) {
        setError("User not found. Please request a new password reset.");
      } else if (httpError.status === 422) {
        setError("Please check your input and try again.");
      } else {
        setError("Something went wrong. Please try again later.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (!token && !error) {
    return (
      <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-sm">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
          Reset your password
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your new password below
        </p>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        {error && (
          <div className="mb-4">
            <Alert type="error" onClose={() => setError("")}>
              {error}
            </Alert>
          </div>
        )}

        {success && (
          <div className="mb-4">
            <Alert type="success">{success}</Alert>
          </div>
        )}

        {token && !success && (
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <div className="relative">
                <Input
                  id="password"
                  label="New password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  required
                  placeholder="Enter your new password"
                  error={errors.password?.message}
                  helperText="At least 8 characters"
                  {...register("password")}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 flex items-center pr-3 pt-7"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeSlashIcon
                      className="h-5 w-5 text-gray-400"
                      aria-hidden="true"
                    />
                  ) : (
                    <EyeIcon
                      className="h-5 w-5 text-gray-400"
                      aria-hidden="true"
                    />
                  )}
                </button>
              </div>
            </div>

            <div>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  label="Confirm new password"
                  type={showConfirmPassword ? "text" : "password"}
                  autoComplete="new-password"
                  required
                  placeholder="Confirm your new password"
                  error={errors.confirmPassword?.message}
                  {...register("confirmPassword")}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 flex items-center pr-3 pt-7"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon
                      className="h-5 w-5 text-gray-400"
                      aria-hidden="true"
                    />
                  ) : (
                    <EyeIcon
                      className="h-5 w-5 text-gray-400"
                      aria-hidden="true"
                    />
                  )}
                </button>
              </div>
            </div>

            <div>
              <Button
                type="submit"
                loading={isLoading}
                className="flex w-full justify-center"
              >
                Reset password
              </Button>
            </div>
          </form>
        )}

        <div className="mt-6 text-center text-sm">
          <Link
            href="/login"
            className="font-semibold text-indigo-600 hover:text-indigo-500"
          >
            Back to sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
