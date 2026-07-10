import { MessageSquare } from "lucide-react";

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh)] flex-col p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Ask AI</h1>
        <p className="mt-1 text-muted-foreground">
          Ask business questions in natural language
        </p>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-border bg-white">
        <MessageSquare className="mb-4 h-10 w-10 text-muted-foreground" />
        <p className="mb-1 font-medium">Chat coming in Phase 2</p>
        <p className="max-w-md text-center text-sm text-muted-foreground">
          Upload documents first, then ask questions like &ldquo;What are our top
          customer complaints this month?&rdquo; with cited sources.
        </p>
      </div>
    </div>
  );
}
