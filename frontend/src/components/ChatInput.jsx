
function ChatInput({
  message,
  setMessage,
  systemPrompt,
  setSystemPrompt,
  onSend,
  loading,
}) {
  function handleSubmit(event) {
    event.preventDefault();

    if (!message.trim() || loading) return;

    onSend();
  }

  return (
    <div className="input-section">
      <details className="system-prompt-section">
        <summary>Customize system prompt (optional)</summary>

        <textarea
          data-testid="system-prompt-input"
          value={systemPrompt}
          onChange={(event) => setSystemPrompt(event.target.value)}
          placeholder="Enter a custom system prompt..."
          rows={3}
          maxLength={2000}
          disabled={loading}
        />
      </details>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          data-testid="chat-input"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Message Lyftr AI..."
          rows={1}
          maxLength={4000}
          disabled={loading}
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey
            ) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
        />

        <button
          type="submit"
          data-testid="send-button"
          disabled={loading || !message.trim()}
        >
          {loading ? "Sending..." : "Send ↑"}
        </button>
      </form>

      <p className="input-disclaimer">
        AI responses may occasionally contain mistakes.
      </p>
    </div>
  );
}

export default ChatInput;
