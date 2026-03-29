/**
 * Format API error bodies into readable Dutch error messages.
 * Handles Pydantic validation errors (array of {msg, loc, type}) and FastAPI detail strings.
 */
export function formatApiError(body: unknown): string {
  if (!body) return 'Onbekende fout';

  const obj = body as Record<string, unknown>;

  // FastAPI string detail: { "detail": "Some error message" }
  if (typeof obj.detail === 'string') return obj.detail;

  // Pydantic validation errors: { "detail": [{ "msg": "...", "loc": [...], "type": "..." }] }
  if (Array.isArray(obj.detail)) {
    return obj.detail
      .map((e: Record<string, unknown>) => {
        const field = Array.isArray(e.loc)
          ? (e.loc as string[]).filter((l) => l !== 'body').join('.')
          : '';
        const msg = (e.msg as string) || 'Ongeldig';
        return field ? `${field}: ${msg}` : msg;
      })
      .join('; ');
  }

  // Fallback
  try {
    return JSON.stringify(body);
  } catch {
    return 'Onbekende fout';
  }
}
