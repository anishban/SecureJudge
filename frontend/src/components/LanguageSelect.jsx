export default function LanguageSelect({ value, onChange, disabled }) {
  return (
    <label className="flex items-center gap-3 text-sm text-console-muted">
      <span>language</span>
      <select
        className="border border-console-edge bg-console-bg px-3 py-2 font-mono text-console-text outline-none focus:border-console-green disabled:opacity-60"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      >
        <option value="python">python</option>
      </select>
    </label>
  );
}
