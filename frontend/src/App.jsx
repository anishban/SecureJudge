import { Play } from "lucide-react";
import { useState } from "react";
import CodeEditor from "./components/CodeEditor.jsx";
import LanguageSelect from "./components/LanguageSelect.jsx";
import ResultPanel from "./components/ResultPanel.jsx";
import StatusBar from "./components/StatusBar.jsx";
import { useJobPolling } from "./hooks/useJobPolling.js";

const STARTER_CODE = `def main():
    print("hello from SecureJudge")

if __name__ == "__main__":
    main()
`;

export default function App() {
  const [language, setLanguage] = useState("python");
  const [sourceCode, setSourceCode] = useState(STARTER_CODE);
  const { error, finalJob, isSubmitting, job, runJob } = useJobPolling();

  const handleSubmit = (event) => {
    event.preventDefault();
    runJob({ language, sourceCode });
  };

  return (
    <main className="min-h-screen bg-console-bg text-console-text">
      <form
        className="mx-auto flex min-h-screen w-full max-w-6xl flex-col border-x border-console-edge bg-console-panel"
        onSubmit={handleSubmit}
      >
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-console-edge bg-console-rail px-4 py-3">
          <div className="font-mono text-sm text-console-text">
            SecureJudge <span className="text-console-muted">:: scratch.py</span>
          </div>
          <div className="flex items-center gap-3">
            <LanguageSelect value={language} onChange={setLanguage} disabled={isSubmitting} />
            <button
              type="submit"
              className="inline-flex h-10 items-center gap-2 border border-console-green bg-console-bg px-4 font-mono text-sm text-console-green outline-none hover:bg-console-green hover:text-console-bg focus:border-console-amber disabled:cursor-not-allowed disabled:border-console-edge disabled:text-console-muted"
              disabled={isSubmitting || sourceCode.trim().length === 0}
            >
              <Play size={16} aria-hidden="true" />
              run
            </button>
          </div>
        </header>

        <CodeEditor value={sourceCode} onChange={setSourceCode} disabled={isSubmitting} />
        <StatusBar error={error} job={job} isSubmitting={isSubmitting} />
        <ResultPanel job={finalJob} />
      </form>
    </main>
  );
}
