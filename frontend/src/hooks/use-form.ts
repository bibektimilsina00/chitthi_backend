import { useForm, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ZodSchema, ZodError, ZodIssue } from "zod";
import { useState } from "react";

// Simple API error type
type ApiErrorType = {
  message: string;
  details?: Record<string, string[]>;
};

interface UseFormWithValidationProps<T extends Record<string, unknown>> {
  schema: ZodSchema<T>;
  onSubmit: (data: T) => Promise<void>;
  resetOnSuccess?: boolean;
}

export function useFormWithValidation<T extends Record<string, unknown>>({
  schema,
  onSubmit,
  resetOnSuccess = false,
}: UseFormWithValidationProps<T>) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm({
    // @ts-expect-error - zodResolver type compatibility issue, works at runtime
    resolver: zodResolver(schema),
    mode: "onBlur" as const,
  });

  const handleFormSubmit: SubmitHandler<Record<string, unknown>> = async (
    data
  ) => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit(data as T);
      if (resetOnSuccess) {
        form.reset();
      }
    } catch (error: unknown) {
      console.error("Form submission error:", error);

      // Check if it's an API error
      if (error && typeof error === "object" && "message" in error) {
        const apiError = error as ApiErrorType;
        // Handle API validation errors
        if (apiError.details && typeof apiError.details === "object") {
          // Set field-specific errors
          Object.entries(apiError.details).forEach(([field, messages]) => {
            if (Array.isArray(messages) && messages.length > 0 && messages[0]) {
              form.setError(field as never, {
                type: "server",
                message: messages[0],
              });
            }
          });
        } else {
          setSubmitError(apiError.message);
        }
      } else if (error instanceof ZodError) {
        // Handle client-side validation errors
        error.issues.forEach((issue: ZodIssue) => {
          const field = issue.path.join(".");
          form.setError(field as never, {
            type: "validation",
            message: issue.message,
          });
        });
      } else {
        // Handle unknown errors
        setSubmitError(
          error instanceof Error
            ? error.message
            : "An unexpected error occurred"
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const setFieldError = (field: string, message: string) => {
    form.setError(field as never, {
      type: "manual",
      message,
    });
  };

  const clearAllErrors = () => {
    form.clearErrors();
    setSubmitError(null);
  };

  return {
    ...form,
    isSubmitting,
    submitError,
    onSubmit: form.handleSubmit(handleFormSubmit),
    setFieldError,
    clearAllErrors,
  };
}

// Specialized hook for auth forms
export function useAuthForm<T extends Record<string, unknown>>(
  props: UseFormWithValidationProps<T>
) {
  return useFormWithValidation(props);
}
