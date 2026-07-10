import { SignIn } from "@clerk/nextjs";
import Link from "next/link";

import { isClerkConfigured } from "@/lib/auth";

export default function SignInPage() {
  if (!isClerkConfigured) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-muted">
        <p className="text-muted-foreground">Clerk is not configured.</p>
        <Link href="/dashboard" className="text-accent hover:underline">
          Continue to dashboard (dev)
        </Link>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted">
      <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" />
    </div>
  );
}
