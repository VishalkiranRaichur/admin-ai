"use client";

import { UserButton } from "@clerk/nextjs";

import { isClerkConfigured } from "@/lib/auth";

export function SidebarUser() {
  if (!isClerkConfigured) {
    return (
      <div className="flex items-center gap-2 text-sm text-sidebar-foreground/70">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-xs font-medium">
          D
        </div>
        Dev user
      </div>
    );
  }

  return (
    <UserButton
      afterSignOutUrl="/"
      appearance={{
        elements: {
          avatarBox: "h-8 w-8",
        },
      }}
    />
  );
}
