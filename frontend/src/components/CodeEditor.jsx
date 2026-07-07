import { useRef } from "react";

function replaceSelection(value, selectionStart, selectionEnd, replacement) {
  return {
    nextValue: value.slice(0, selectionStart) + replacement + value.slice(selectionEnd),
    cursor: selectionStart + replacement.length,
  };
}

export default function CodeEditor({ value, onChange, disabled }) {
  const editorRef = useRef(null);

  const updateEditor = (nextValue, cursor) => {
    onChange(nextValue);

    requestAnimationFrame(() => {
      editorRef.current?.setSelectionRange(cursor, cursor);
    });
  };

  const handleKeyDown = (event) => {
    const textarea = event.currentTarget;
    const { selectionStart, selectionEnd } = textarea;

    if (event.key === "Tab") {
      event.preventDefault();
      const { nextValue, cursor } = replaceSelection(
        value,
        selectionStart,
        selectionEnd,
        "    "
      );
      updateEditor(nextValue, cursor);
    }

    if (event.key === "Enter") {
      event.preventDefault();
      const lineStart = value.lastIndexOf("\n", selectionStart - 1) + 1;
      const currentLine = value.slice(lineStart, selectionStart);
      const indent = currentLine.match(/^\s*/)?.[0] || "";
      const extraIndent = currentLine.trim().endsWith(":") ? "    " : "";
      const replacement = `\n${indent}${extraIndent}`;
      const { nextValue, cursor } = replaceSelection(
        value,
        selectionStart,
        selectionEnd,
        replacement
      );
      updateEditor(nextValue, cursor);
    }
  };

  return (
    <div className="grid min-h-[430px] grid-cols-[3.25rem_1fr] border-y border-console-edge bg-console-bg">
      <div className="select-none border-r border-console-edge bg-console-rail py-4 text-right font-mono text-xs leading-6 text-console-muted">
        {value.split("\n").map((_, index) => (
          <div key={index} className="px-3">
            {index + 1}
          </div>
        ))}
      </div>
      <textarea
        ref={editorRef}
        className="min-h-[430px] w-full resize-none bg-console-bg px-4 py-4 font-mono text-sm leading-6 text-console-text caret-console-green outline-none selection:bg-console-green selection:text-console-bg disabled:opacity-60"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        spellCheck="false"
        disabled={disabled}
        aria-label="Source code editor"
      />
    </div>
  );
}
