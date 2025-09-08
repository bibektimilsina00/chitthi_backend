import { ReactNode } from "react";
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XMarkIcon,
} from "@heroicons/react/20/solid";

export interface AlertProps {
  type?: "success" | "error" | "warning" | "info";
  title?: string;
  children: ReactNode;
  onClose?: () => void;
  className?: string;
}

const alertStyles = {
  success: {
    container: "bg-green-50 border-green-200",
    icon: "text-green-400",
    title: "text-green-800",
    content: "text-green-700",
  },
  error: {
    container: "bg-red-50 border-red-200",
    icon: "text-red-400",
    title: "text-red-800",
    content: "text-red-700",
  },
  warning: {
    container: "bg-yellow-50 border-yellow-200",
    icon: "text-yellow-400",
    title: "text-yellow-800",
    content: "text-yellow-700",
  },
  info: {
    container: "bg-blue-50 border-blue-200",
    icon: "text-blue-400",
    title: "text-blue-800",
    content: "text-blue-700",
  },
};

const iconComponents = {
  success: CheckCircleIcon,
  error: ExclamationCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
};

export default function Alert({
  type = "info",
  title,
  children,
  onClose,
  className = "",
}: AlertProps) {
  const styles = alertStyles[type];
  const IconComponent = iconComponents[type];

  return (
    <div className={`rounded-md border p-4 ${styles.container} ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <IconComponent
            className={`h-5 w-5 ${styles.icon}`}
            aria-hidden="true"
          />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={`text-sm font-medium ${styles.title}`}>{title}</h3>
          )}
          <div className={`text-sm ${title ? "mt-2" : ""} ${styles.content}`}>
            {children}
          </div>
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                className={`inline-flex rounded-md p-1.5 hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 ${styles.icon} hover:bg-current focus:ring-current`}
                onClick={onClose}
              >
                <span className="sr-only">Dismiss</span>
                <XMarkIcon className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
