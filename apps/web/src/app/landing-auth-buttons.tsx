"use client";

import { SignInButton, SignUpButton, SignedIn, SignedOut } from "@clerk/nextjs";
import Link from "next/link";

import { isClerkConfigured } from "@/lib/auth";

type LandingAuthButtonsProps = {
  variant?: "header" | "hero";
};

export function LandingAuthButtons({ variant = "header" }: LandingAuthButtonsProps) {
  if (!isClerkConfigured) {
    if (variant === "hero") {
      return (
        <Link
          href="/dashboard"
          className="inline-block rounded-lg bg-accent px-8 py-3 text-base font-medium text-accent-foreground hover:opacity-90"
        >
          Open dashboard (dev)
        </Link>
      );
    }

    return (
      <Link
        href="/dashboard"
        className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:opacity-90"
      >
        Open dashboard
      </Link>
    );
  }

  if (variant === "hero") {
    return (
      <>
        <SignedOut>
          <SignUpButton mode="modal">
            <button className="rounded-lg bg-accent px-8 py-3 text-base font-medium text-accent-foreground hover:opacity-90">
              Start free trial
            </button>
          </SignUpButton>
        </SignedOut>
        <SignedIn>
          <Link
            href="/dashboard"
            className="inline-block rounded-lg bg-accent px-8 py-3 text-base font-medium text-accent-foreground hover:opacity-90"
          >
            Go to dashboard
          </Link>
        </SignedIn>
      </>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <SignedOut>
        <SignInButton mode="modal">
          <button className="rounded-md px-4 py-2 text-sm font-medium text-foreground hover:bg-muted">
            Sign in
          </button>
        </SignInButton>
        <SignUpButton mode="modal">
          <button className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:opacity-90">
            Get started
          </button>
        </SignUpButton>
      </SignedOut>
      <SignedIn>
        <Link
          href="/dashboard"
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:opacity-90"
        >
          Open dashboard
        </Link>
      </SignedIn>
    </div>
  );
}
