import { useCallback, useEffect, useRef, useState } from "react";
import { fetchJob, submitJob } from "../services/jobsApi.js";

const TERMINAL_STATUSES = new Set(["completed", "failed", "timed_out"]);
const POLL_INTERVAL_MS = 3000;

export function useJobPolling() {
  const [job, setJob] = useState(null);
  const [finalJob, setFinalJob] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const timerRef = useRef(null);

  const stopPolling = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => stopPolling, [stopPolling]);

  const pollJob = useCallback(
    async (jobId) => {
      try {
        const nextJob = await fetchJob(jobId);
        setJob(nextJob);

        if (TERMINAL_STATUSES.has(nextJob.status)) {
          stopPolling();
          setFinalJob(nextJob);
          setIsSubmitting(false);
        }
      } catch (pollError) {
        stopPolling();
        setError(pollError.message);
        setIsSubmitting(false);
      }
    },
    [stopPolling]
  );

  const runJob = useCallback(
    async ({ language, sourceCode }) => {
      stopPolling();
      setError("");
      setFinalJob(null);
      setJob(null);
      setIsSubmitting(true);

      try {
        const createdJob = await submitJob({ language, sourceCode });
        setJob(createdJob);

        timerRef.current = setInterval(() => {
          pollJob(createdJob.id);
        }, POLL_INTERVAL_MS);
      } catch (submitError) {
        setError(submitError.message);
        setIsSubmitting(false);
      }
    },
    [pollJob, stopPolling]
  );

  return {
    error,
    finalJob,
    isSubmitting,
    job,
    runJob,
  };
}
