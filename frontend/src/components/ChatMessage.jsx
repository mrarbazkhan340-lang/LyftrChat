
import MessageMetadata from "./MessageMetadata";

function ChatMessage({ message }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`message-row ${isAssistant ? "assistant-row" : "user-row"}`}>
      <div className={`message-avatar ${isAssistant ? "ai-avatar" : "user-avatar"}`}>
        {isAssistant ? "AI" : "You"}
      </div>

      <div
        className={`message-content ${
          isAssistant ? "assistant-content" : "user-content"
        }`}
      >
        <div className="message-sender">
          {isAssistant ? "Lyftr AI" : "You"}
        </div>

        <div
          className={isAssistant ? "assistant-bubble" : "user-bubble"}
          {...(isAssistant ? { "data-testid": "assistant-message" } : {})}
        >
          <p>{message.content}</p>

          {isAssistant && (
            <MessageMetadata metadata={message.metadata} />
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;
