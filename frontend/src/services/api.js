
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

export async function sendMessage({
  sessionId,
  message,
  systemPrompt,
}) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      ...(systemPrompt ? { system_prompt: systemPrompt } : {}),
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || "Unable to get a response. Please try again."
    );
  }

  return data;
}

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Backend is unavailable.");
  }

  return data;
}

export async function getSessionMessages(sessionId) {
  const response = await fetch(
    `${API_BASE_URL}/sessions/${encodeURIComponent(sessionId)}/messages`
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Unable to load session history.");
  }

  return data;
}
