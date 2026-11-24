
import { useState } from "react";

import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";

import { sendMessage } from "./services/api";
import { createSessionId } from "./utils/session";

function App() {
  const [sessionId] = useState(() => createSessionId());

  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSend() {
    const userMessage = message.trim();

    if (!userMessage || loading) return;

    setMessage("");
    setError("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: userMessage,
      },
    ]);

    try {
      const data = await sendMessage({
        sessionId,
        message: userMessage,
        systemPrompt: systemPrompt.trim(),
      });

      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.reply,
          metadata: data.metadata,
        },
      ]);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">L</div>

          <div>
            <h1>LyftrChat</h1>
            <span>AI Conversation Assistant</span>
          </div>
        </div>

        <div className="connection-status">
          <span className="status-dot"></span>
          AI Chat
        </div>
      </header>

      <main className="main-container">
        <div className="chat-heading">
          <div>
            <h2>New Conversation</h2>
            <p>Ask anything and explore with AI.</p>
          </div>

          <span className="session-label">
            Session Active
          </span>
        </div>

        <ChatWindow
          messages={messages}
          loading={loading}
        />

        {error && (
          <div className="error-message" role="alert">
            <span>{error}</span>

            <button
              type="button"
              onClick={() => setError("")}
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        )}

        <ChatInput
          message={message}
          setMessage={setMessage}
          systemPrompt={systemPrompt}
          setSystemPrompt={setSystemPrompt}
          onSend={handleSend}
          loading={loading}
        />
      </main>

      <footer className="app-footer">
        LyftrChat · Powered by LiteLLM
      </footer>
    </div>
  );
}

export default App;
