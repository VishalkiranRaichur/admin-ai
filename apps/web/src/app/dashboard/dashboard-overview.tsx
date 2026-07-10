import { FileText, Lightbulb, MessageSquare, Upload } from "lucide-react";
import Link from "next/link";

type DashboardOverviewProps = {
  firstName: string;
};

export function DashboardOverview({ firstName }: DashboardOverviewProps) {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Welcome back, {firstName}</h1>
        <p className="mt-1 text-muted-foreground">
          Your AI-powered company operating system
        </p>
      </div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Documents", value: "0", icon: FileText },
          { label: "Conversations", value: "0", icon: MessageSquare },
          { label: "Insights", value: "0", icon: Lightbulb },
          { label: "Action items", value: "0", icon: Upload },
        ].map(({ label, value, icon: Icon }) => (
          <div
            key={label}
            className="rounded-xl border border-border bg-white p-5"
          >
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm text-muted-foreground">{label}</span>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </div>
            <p className="text-3xl font-bold">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-white p-6">
          <h2 className="mb-2 font-semibold">Get started</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Upload your first document to begin asking questions and generating
            insights.
          </p>
          <Link
            href="/dashboard/documents"
            className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:opacity-90"
          >
            <Upload className="h-4 w-4" />
            Upload documents
          </Link>
        </div>

        <div className="rounded-xl border border-border bg-white p-6">
          <h2 className="mb-2 font-semibold">Ask a question</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Once documents are uploaded, ask business questions in natural
            language with source citations.
          </p>
          <Link
            href="/dashboard/chat"
            className="inline-flex items-center gap-2 rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
          >
            <MessageSquare className="h-4 w-4" />
            Open chat
          </Link>
        </div>
      </div>
    </div>
  );
}
