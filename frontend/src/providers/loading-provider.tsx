"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface LoadingState {
  [key: string]: boolean;
}

interface LoadingContextType {
  loadingStates: LoadingState;
  setLoading: (key: string, isLoading: boolean) => void;
  isLoading: (key?: string) => boolean;
  isAnyLoading: () => boolean;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export function LoadingProvider({ children }: { children: ReactNode }) {
  const [loadingStates, setLoadingStates] = useState<LoadingState>({});

  const setLoading = (key: string, isLoading: boolean) => {
    setLoadingStates((prev) => ({
      ...prev,
      [key]: isLoading,
    }));
  };

  const isLoading = (key?: string) => {
    if (!key) return false;
    return Boolean(loadingStates[key]);
  };

  const isAnyLoading = () => {
    return Object.values(loadingStates).some(Boolean);
  };

  return (
    <LoadingContext.Provider
      value={{
        loadingStates,
        setLoading,
        isLoading,
        isAnyLoading,
      }}
    >
      {children}
    </LoadingContext.Provider>
  );
}

export function useLoading() {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error("useLoading must be used within a LoadingProvider");
  }
  return context;
}

/**
 * Hook to manage loading state for async operations
 */
export function useAsyncOperation() {
  const { setLoading, isLoading } = useLoading();

  const executeAsync = async function <T>(
    key: string,
    asyncFn: () => Promise<T>
  ): Promise<T> {
    try {
      setLoading(key, true);
      const result = await asyncFn();
      return result;
    } finally {
      setLoading(key, false);
    }
  };

  return {
    executeAsync,
    isLoading,
  };
}
