import { useState } from "react";
import {
  useForm,
  UseFormProps,
  FieldValues,
  SubmitHandler,
} from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ZodType } from "zod";
import { HttpError } from "@/types/api";

interface UseAuthFormOptions<T extends FieldValues> extends UseFormProps<T> {
  schema: ZodType<T>;
  onSubmit: SubmitHandler<T>;
  onSuccess?: (data: T) => void;
  onError?: (error: HttpError) => void;
  resetOnSuccess?: boolean;
}

/**
 * Reusable hook for auth forms with error handling and loading states
 */
export function useAuthForm<T extends FieldValues>({
  schema,
  onSubmit,
  onSuccess,
  onError,
  resetOnSuccess = false,
  ...formOptions
}: UseAuthFormOptions<T>) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");

  const form = useForm<T>({
    // @ts-expect-error - zodResolver type compatibility issue, works at runtime
    resolver: zodResolver(schema),
    ...formOptions,
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      setIsLoading(true);
      setError("");
      setSuccess("");

      await onSubmit(data as unknown as T);

      onSuccess?.(data as unknown as T);

      if (resetOnSuccess) {
        form.reset();
      }
    } catch (err) {
      const httpError = err as HttpError;

      let errorMessage = "Something went wrong. Please try again later.";

      if (httpError.status === 400) {
        errorMessage =
          "Invalid input. Please check your information and try again.";
      } else if (httpError.status === 401) {
        errorMessage = "Authentication failed. Please check your credentials.";
      } else if (httpError.status === 403) {
        errorMessage = "You do not have permission to perform this action.";
      } else if (httpError.status === 409) {
        errorMessage =
          "This information is already in use. Please try different values.";
      } else if (httpError.status === 422) {
        errorMessage = "Please check your input and try again.";
      } else if (httpError.status >= 500) {
        errorMessage = "Server error. Please try again later.";
      }

      setError(errorMessage);
      onError?.(httpError);
    } finally {
      setIsLoading(false);
    }
  });

  const clearError = () => setError("");
  const clearSuccess = () => setSuccess("");
  const setSuccessMessage = (message: string) => setSuccess(message);

  return {
    ...form,
    handleSubmit,
    isLoading,
    error,
    success,
    clearError,
    clearSuccess,
    setSuccessMessage,
  };
}

/**
 * Hook for password visibility toggle
 */
export function usePasswordVisibility() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const togglePassword = () => setShowPassword(!showPassword);
  const toggleConfirmPassword = () =>
    setShowConfirmPassword(!showConfirmPassword);

  return {
    showPassword,
    showConfirmPassword,
    togglePassword,
    toggleConfirmPassword,
  };
}
