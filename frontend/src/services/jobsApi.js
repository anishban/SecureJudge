const API_BASE_URL = "/api";

async function readJson(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }

  return data;
}

export async function submitJob({ language, sourceCode }) {
  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      language,
      source_code: sourceCode,
    }),
  });

  return readJson(response);
}

export async function fetchJob(jobId) {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
  return readJson(response);
}
