import { isClerkConfigured } from "@/lib/auth";
import { DashboardOverview } from "./dashboard-overview";

export default async function DashboardPage() {
  let firstName = "there";

  if (isClerkConfigured) {
    const { currentUser } = await import("@clerk/nextjs/server");
    const user = await currentUser();
    firstName = user?.firstName ?? "there";
  }

  return <DashboardOverview firstName={firstName} />;
}
