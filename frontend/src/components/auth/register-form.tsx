"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";

import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import Alert from "@/components/ui/alert";
import { useAuthActions } from "@/hooks/use-auth";
import { registerSchema, type RegisterFormData } from "@/lib/validations";
import { HttpError } from "@/types/api";

export default function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const router = useRouter();
  const { register: registerUser } = useAuthActions();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsLoading(true);
      setError("");
      setSuccess("");

      // Remove confirmPassword from the data sent to API
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { confirmPassword, ...registerData } = data;

      // Convert empty strings to undefined for optional fields
      const cleanedData: {
        username: string;
        password: string;
        email?: string;
        display_name?: string;
      } = {
        username: registerData.username,
        password: registerData.password,
      };

      if (registerData.email) {
        cleanedData.email = registerData.email;
      }

      if (registerData.display_name) {
        cleanedData.display_name = registerData.display_name;
      }

      await registerUser(cleanedData);

      setSuccess("Account created successfully! You can now sign in.");
      reset();

      // Redirect to login after a short delay
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err) {
      const httpError = err as HttpError;

      if (httpError.status === 400) {
        setError(
          "A user with this email already exists. Please try a different email or sign in instead."
        );
      } else if (httpError.status === 422) {
        setError("Please check your input and try again.");
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
          Create your account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Join Chitthi for secure messaging
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
              id="username"
              label="Username"
              type="text"
              autoComplete="username"
              required
              placeholder="Choose a username"
              error={errors.username?.message}
              helperText="Only letters, numbers, and underscores allowed"
              {...register("username")}
            />
          </div>

          <div>
            <Input
              id="email"
              label="Email address (optional)"
              type="email"
              autoComplete="email"
              placeholder="Enter your email"
              error={errors.email?.message}
              {...register("email")}
            />
          </div>

          <div>
            <Input
              id="display_name"
              label="Display name (optional)"
              type="text"
              placeholder="How others will see your name"
              error={errors.display_name?.message}
              {...register("display_name")}
            />
          </div>

          <div>
            <div className="relative">
              <Input
                id="password"
                label="Password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                placeholder="Create a password"
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
                label="Confirm password"
                type={showConfirmPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                placeholder="Confirm your password"
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
              Create account
            </Button>
          </div>
        </form>

        <p className="mt-10 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500"
          >
            Sign in here
          </Link>
        </p>
      </div>
    </div>
  );
}
