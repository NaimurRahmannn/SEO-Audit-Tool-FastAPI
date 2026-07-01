const STACK_TRACE_PATTERNS = [
  /traceback/i,
  /\bat\s+\S+\s+\(.+:\d+:\d+\)/,
  /File ".+", line \d+/,
  /stack trace/i,
];

export function toReadableErrorMessage(
  message: unknown,
  fallback = "Something went wrong. Please try again."
): string {
  const raw =
    typeof message === "string"
      ? message
      : message instanceof Error
        ? message.message
        : "";

  const trimmed = raw.trim();
  if (!trimmed) return fallback;
  if (STACK_TRACE_PATTERNS.some((pattern) => pattern.test(trimmed))) {
    return fallback;
  }

  const firstParagraph = trimmed
    .split(/\r?\n\s*\r?\n/)
    .find((part) => part.trim());
  const compact = (firstParagraph ?? trimmed).replace(/\s+/g, " ").trim();

  if (compact.length <= 360) return compact;
  return `${compact.slice(0, 357).trimEnd()}...`;
}
