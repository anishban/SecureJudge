function OutputBlock({ title, value }) {
  return (
    <section className="border-t border-console-edge">
      <div className="bg-console-rail px-4 py-2 font-mono text-xs uppercase text-console-muted">
        {title}
      </div>
      <pre className="min-h-24 overflow-auto whitespace-pre-wrap bg-console-bg px-4 py-3 font-mono text-sm leading-6 text-console-text">
        {value || "<empty>"}
      </pre>
    </section>
  );
}

export default function ResultPanel({ job }) {
  if (!job) {
    return (
      <div className="border-t border-console-edge bg-console-bg px-4 py-5 font-mono text-sm text-console-muted">
        result buffer hidden until execution reaches a terminal state
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-1 border-t border-console-edge bg-console-rail font-mono text-xs text-console-muted sm:grid-cols-3">
        <div className="px-4 py-2">status: {job.status}</div>
        <div className="px-4 py-2">exit: {job.exit_code ?? "none"}</div>
        <div className="px-4 py-2">time: {job.execution_time_ms ?? 0}ms</div>
      </div>
      <OutputBlock title="stdout" value={job.stdout} />
      <OutputBlock title="stderr" value={job.stderr} />
    </div>
  );
}
