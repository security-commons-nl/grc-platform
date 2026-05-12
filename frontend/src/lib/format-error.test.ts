import { describe, expect, it } from 'vitest';
import { formatApiError } from './format-error';

describe('formatApiError', () => {
  it('returnt "Onbekende fout" bij falsy input', () => {
    expect(formatApiError(null)).toBe('Onbekende fout');
    expect(formatApiError(undefined)).toBe('Onbekende fout');
    expect(formatApiError('')).toBe('Onbekende fout');
  });

  it('returnt FastAPI-detail-string ongewijzigd', () => {
    expect(formatApiError({ detail: 'Risico niet gevonden' })).toBe(
      'Risico niet gevonden',
    );
  });

  it('formatteert Pydantic validation errors met loc-pad', () => {
    const body = {
      detail: [
        { loc: ['body', 'title'], msg: 'field required', type: 'value_error.missing' },
        { loc: ['body', 'likelihood'], msg: 'ensure this value is >= 1', type: 'value_error' },
      ],
    };
    expect(formatApiError(body)).toBe(
      'title: field required; likelihood: ensure this value is >= 1',
    );
  });

  it('strijkt "body" weg uit loc-pad', () => {
    const body = {
      detail: [{ loc: ['body'], msg: 'value is not a valid dict', type: 'type_error' }],
    };
    // Zonder body in loc levert het lege field-string op → alleen msg
    expect(formatApiError(body)).toBe('value is not a valid dict');
  });

  it('valt terug op JSON-stringify bij onbekende vorm', () => {
    const result = formatApiError({ foo: 'bar', n: 42 });
    expect(result).toContain('foo');
    expect(result).toContain('bar');
  });
});
