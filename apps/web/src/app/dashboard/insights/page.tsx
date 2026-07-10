import { Lightbulb } from "lucide-react";

export default function InsightsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Insights</h1>
        <p className="mt-1 text-muted-foreground">
          Executive summaries, action items, and business risks
        </p>
      </div>

      <div className="flex flex-col items-center justify-center rounded-xl border border-border bg-white py-20">
        <Lightbulb className="mb-4 h-10 w-10 text-muted-foreground" />
        <p className="mb-1 font-medium">No insights yet</p>
        <p className="max-w-md text-center text-sm text-muted-foreground">
          Insights will be generated automatically from your uploaded documents.
          Coming in Phase 3.
        </p>
      </div>
    </div>
  );
}
