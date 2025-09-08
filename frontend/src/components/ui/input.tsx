import { forwardRef, InputHTMLAttributes } from "react";
import { ExclamationCircleIcon } from "@heroicons/react/20/solid";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string | undefined;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { className = "", label, error, helperText, type = "text", ...props },
    ref
  ) => {
    const inputClasses = `
      block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset 
      placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6
      ${
        error
          ? "ring-red-300 focus:ring-red-500"
          : "ring-gray-300 focus:ring-indigo-600"
      }
      ${className}
    `.trim();

    return (
      <div>
        {label && (
          <label
            htmlFor={props.id}
            className="block text-sm font-medium leading-6 text-gray-900"
          >
            {label}
          </label>
        )}
        <div className={label ? "mt-2" : ""}>
          <input ref={ref} type={type} className={inputClasses} {...props} />
          {error && (
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
              <ExclamationCircleIcon
                className="h-5 w-5 text-red-500"
                aria-hidden="true"
              />
            </div>
          )}
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-600" id={`${props.id}-error`}>
            {error}
          </p>
        )}
        {helperText && !error && (
          <p
            className="mt-2 text-sm text-gray-500"
            id={`${props.id}-description`}
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
