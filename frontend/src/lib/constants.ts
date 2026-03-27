export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const ROLE_HIERARCHY: Record<string, number> = {
  admin: 6,
  sims_lid: 5,
  tims_lid: 4,
  discipline_eigenaar: 3,
  lijnmanager: 2,
  viewer: 1,
};

export function hasMinRole(userRole: string, requiredRole: string): boolean {
  return (ROLE_HIERARCHY[userRole] || 0) >= (ROLE_HIERARCHY[requiredRole] || 99);
}

export const ROLE_LABELS: Record<string, string> = {
  admin: 'Admin',
  sims_lid: 'SIMS-lid',
  tims_lid: 'TIMS-lid',
  discipline_eigenaar: 'Discipline-eigenaar',
  lijnmanager: 'Lijnmanager',
  viewer: 'Viewer',
};

export const STATUS_LABELS: Record<string, string> = {
  niet_gestart: 'Niet gestart',
  in_uitvoering: 'In uitvoering',
  concept: 'Concept',
  in_review: 'In review',
  vastgesteld: 'Vastgesteld',
};

export const STATUS_COLORS: Record<string, string> = {
  niet_gestart: 'bg-neutral-200 text-neutral-600',
  in_uitvoering: 'bg-primary-100 text-primary-700',
  concept: 'bg-yellow-100 text-yellow-800',
  in_review: 'bg-orange-100 text-orange-800',
  vastgesteld: 'bg-green-100 text-green-800',
};
