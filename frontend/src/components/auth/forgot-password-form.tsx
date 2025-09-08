"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import Alert from "@/components/ui/alert";
import { authService } from "@/lib/auth";
import {
  forgotPasswordSchema,
  type ForgotPasswordFormData,
} from "@/lib/validations";
import { HttpError } from "@/types/api";

export default function ForgotPasswordForm() {
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      setIsLoading(true);
      setError("");
      setSuccess("");

      await authService.requestPasswordReset(data.email);

      setSuccess(
        "Password recovery email sent! Please check your inbox for further instructions."
      );
    } catch (err) {
      const httpError = err as HttpError;

      if (httpError.status === 404) {
        setError("No account found with this email address.");
      } else if (httpError.status === 422) {
        setError("Please enter a valid email address.");
      } else {
        setError("Something went wrong. Please try again later.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
          Forgot your password?
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your email and we&apos;ll send you a link to reset your password
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

        <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <Input
              id="email"
              label="Email address"
              type="email"
              autoComplete="email"
              required
              placeholder="Enter your email address"
              error={errors.email?.message}
              {...register("email")}
            />
          </div>

          <div>
            <Button
              type="submit"
              loading={isLoading}
              className="flex w-full justify-center"
            >
              Send recovery email
            </Button>
          </div>
        </form>

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
