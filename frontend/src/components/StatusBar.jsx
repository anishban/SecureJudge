const STATUS_LABELS = {
  idle: "idle",
  queued: "queued",
  running: "running",
  completed: "completed",
  failed: "failed",
  timed_out: "timed out",
};

export default function StatusBar({ error, job, isSubmitting }) {
  const status = error ? "error" : job?.status || (isSubmitting ? "queued" : "idle");
  const jobLabel = job?.id ? `job #${job.id}` : "no job";

  return (
    <div className="flex min-h-10 flex-wrap items-center justify-between gap-3 border-t border-console-edge bg-console-rail px-4 py-2 font-mono text-xs">
      <div className="flex items-center gap-3 text-console-muted">
        <span>{jobLabel}</span>
        <span className="text-console-edge">|</span>
        <span className={error ? "text-console-red" : "text-console-green"}>
          {error || STATUS_LABELS[status] || status}
        </span>
      </div>
      <div className="text-console-muted">poll: 3s</div>
    </div>
  );
}
