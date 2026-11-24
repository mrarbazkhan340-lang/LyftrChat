
import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";

function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  return (
    <div className="chat-window">
      {messages.length === 0 && !loading && (
        <div className="welcome-message">
          <div className="welcome-icon">✦</div>
          <h2>How can I help you today?</h2>
          <p>
            Start a conversation. Your AI assistant is ready.
          </p>
        </div>
      )}

      {messages.map((message, index) => (
        <ChatMessage
          key={message.id || index}
          message={message}
        />
      ))}

      {loading && (
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
          <p>Lyftr AI is thinking...</p>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

export default ChatWindow;
