
function MessageMetadata({ metadata }) {
  if (!metadata) return null;

  return (
    <div className="message-metadata">
      <div className="metadata-row">
        <span className="metadata-label">Source</span>
        <span
          className={`source-badge ${
            metadata.resolution_source === "LLM_CACHE"
              ? "cache-source"
              : "live-source"
          }`}
          data-testid="meta-source"
        >
          {metadata.resolution_source}
        </span>
      </div>

      <div className="metadata-row">
        <span className="metadata-label">Model</span>
        <span data-testid="meta-model">
          {metadata.model}
        </span>
      </div>

      <div className="metadata-row">
        <span className="metadata-label">Latency</span>
        <span data-testid="meta-latency">
          {metadata.latency_ms} ms
        </span>
      </div>

      <div className="metadata-row">
        <span className="metadata-label">Input tokens</span>
        <span data-testid="meta-input-tokens">
          {metadata.input_tokens}
        </span>
      </div>

      <div className="metadata-row">
        <span className="metadata-label">Output tokens</span>
        <span data-testid="meta-output-tokens">
          {metadata.output_tokens}
        </span>
      </div>
    </div>
  );
}

export default MessageMetadata;
