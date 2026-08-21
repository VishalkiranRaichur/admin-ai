import { Sidebar } from "@/components/dashboard/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-[#09090d] text-white">
      <Sidebar />

      <main className="min-w-0 flex-1 overflow-hidden bg-[#09090d]">
        {children}
      </main>
    </div>
  );
}
