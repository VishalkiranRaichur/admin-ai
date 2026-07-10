import { Upload } from "lucide-react";

export default function DocumentsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Documents</h1>
        <p className="mt-1 text-muted-foreground">
          Upload meeting notes, contracts, reports, and more
        </p>
      </div>

      <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-border bg-white py-20">
        <Upload className="mb-4 h-10 w-10 text-muted-foreground" />
        <p className="mb-1 font-medium">No documents yet</p>
        <p className="mb-6 text-sm text-muted-foreground">
          Drag and drop files here, or click to browse. Coming in Phase 1.
        </p>
        <button
          disabled
          className="cursor-not-allowed rounded-md bg-muted px-4 py-2 text-sm font-medium text-muted-foreground"
        >
          Upload documents
        </button>
      </div>
    </div>
  );
}
