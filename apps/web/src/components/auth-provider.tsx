"use client";

import { ClerkProvider } from "@clerk/nextjs";

import { isClerkConfigured } from "@/lib/auth";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  if (!isClerkConfigured) {
    return <>{children}</>;
  }

  return <ClerkProvider>{children}</ClerkProvider>;
}
