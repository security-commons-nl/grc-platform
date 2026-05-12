import { describe, expect, it } from 'vitest';
import { hasMinRole, ROLE_HIERARCHY } from './constants';

describe('hasMinRole', () => {
  it('admin haalt elke vereiste rol', () => {
    for (const role of Object.keys(ROLE_HIERARCHY)) {
      expect(hasMinRole('admin', role)).toBe(true);
    }
  });

  it('viewer haalt alleen viewer', () => {
    expect(hasMinRole('viewer', 'viewer')).toBe(true);
    expect(hasMinRole('viewer', 'lijnmanager')).toBe(false);
    expect(hasMinRole('viewer', 'admin')).toBe(false);
  });

  it('tactisch_lid haalt discipline_eigenaar, lijnmanager en viewer', () => {
    expect(hasMinRole('tactisch_lid', 'discipline_eigenaar')).toBe(true);
    expect(hasMinRole('tactisch_lid', 'lijnmanager')).toBe(true);
    expect(hasMinRole('tactisch_lid', 'viewer')).toBe(true);
  });

  it('tactisch_lid haalt strategisch_lid en admin niet', () => {
    expect(hasMinRole('tactisch_lid', 'strategisch_lid')).toBe(false);
    expect(hasMinRole('tactisch_lid', 'admin')).toBe(false);
  });

  it('onbekende rol geldt als laagst (geen rechten)', () => {
    expect(hasMinRole('foo', 'viewer')).toBe(false);
  });

  it('onbekende required-rol weigert iedereen behalve fallback', () => {
    // requiredRole onbekend → ROLE_HIERARCHY[req] = undefined → || 99
    // userRole admin = 6 → 6 >= 99 → false
    expect(hasMinRole('admin', 'nonexistent')).toBe(false);
  });
});
