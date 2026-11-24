
export function createSessionId() {
  if (crypto.randomUUID) {
    return `session-${crypto.randomUUID()}`;
  }

  return `session-${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`;
}
