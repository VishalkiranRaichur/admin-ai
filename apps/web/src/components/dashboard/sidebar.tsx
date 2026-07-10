"use client";

import {
  FileText,
  LayoutDashboard,
  Lightbulb,
  MessageSquare,
  Settings,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { SidebarUser } from "@/components/dashboard/sidebar-user";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/documents", label: "Documents", icon: FileText },
  { href: "/dashboard/chat", label: "Ask AI", icon: MessageSquare },
  { href: "/dashboard/insights", label: "Insights", icon: Lightbulb },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 flex-col bg-sidebar text-sidebar-foreground">
      <div className="flex items-center gap-2 border-b border-white/10 px-6 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sidebar-active text-sm font-bold text-white">
          A
        </div>
        <span className="font-semibold">Admin AI</span>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive =
            pathname === href ||
            (href !== "/dashboard" && pathname.startsWith(href));

          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-sidebar-active text-white"
                  : "text-sidebar-foreground/70 hover:bg-white/10 hover:text-sidebar-foreground"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 px-4 py-4">
        <SidebarUser />
      </div>
    </aside>
  );
}
