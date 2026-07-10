export default function SettingsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="mt-1 text-muted-foreground">
          Manage your organization and integrations
        </p>
      </div>

      <div className="max-w-2xl space-y-6">
        <section className="rounded-xl border border-border bg-white p-6">
          <h2 className="mb-1 font-semibold">Organization</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Organization settings will be available in a future phase.
          </p>
        </section>

        <section className="rounded-xl border border-border bg-white p-6">
          <h2 className="mb-1 font-semibold">Integrations</h2>
          <p className="text-sm text-muted-foreground">
            Connect Gmail, Slack, Google Drive, and Calendar in Phase 5.
          </p>
        </section>
      </div>
    </div>
  );
}
