import { expect, type APIRequestContext, type Page } from '@playwright/test';

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export const TENANT_ID = '00000000-0000-0000-0000-000000000001';
export const SEED_ADMIN_USER_ID = '00000000-0000-0000-0000-000000000002';

/**
 * Cache van dev-tokens per rol. Voorkomt dat we de RATE_LIMIT_AUTH (10/min)
 * verbranden door iedere test opnieuw een token op te halen. Token's TTL is
 * 60 min — meer dan voldoende voor een Playwright-run.
 */
const _devTokenCache: Record<string, string> = {};

export async function getDevToken(
  request: APIRequestContext,
  role: 'admin' | 'strategisch_lid' | 'tactisch_lid' | 'viewer' = 'admin',
): Promise<string> {
  if (_devTokenCache[role]) return _devTokenCache[role];
  const r = await request.post(`${API_BASE}/api/v1/auth/dev-token`, {
    data: {
      user_id: SEED_ADMIN_USER_ID,
      tenant_id: TENANT_ID,
      role,
    },
  });
  expect(r.ok(), `dev-token (${role}) faalt: ${await r.text()}`).toBeTruthy();
  _devTokenCache[role] = (await r.json()).access_token;
  return _devTokenCache[role];
}

/**
 * Cache van een dev-token JWT op module-niveau. Playwright draait met 1 worker
 * dus dit wordt tussen tests in dezelfde run hergebruikt — vermijdt
 * RATE_LIMIT_AUTH (10/minuut) bij veel sequentiële logins.
 */
let _cachedAdminToken: string | null = null;

async function fetchAdminToken(page: Page): Promise<string> {
  if (_cachedAdminToken) return _cachedAdminToken;
  const r = await page.request.post(`${API_BASE}/api/v1/auth/dev-token`, {
    data: {
      user_id: SEED_ADMIN_USER_ID,
      tenant_id: TENANT_ID,
      role: 'admin',
    },
  });
  expect(r.ok(), `dev-token bootstrap faalt: ${await r.text()}`).toBeTruthy();
  const token = (await r.json()).access_token as string;
  _cachedAdminToken = token;
  return token;
}

/**
 * Login zonder de UI-form. Schrijft een JWT van seed-admin (een bestaande
 * `users.id` zodat endpoints met `current_user.id`-FK werken) rechtstreeks
 * naar localStorage. Bedoeld voor de meeste e2e-tests omdat de UI-login een
 * random user-UUID genereert.
 */
export async function loginAsAdmin(page: Page) {
  const token = await fetchAdminToken(page);
  await page.goto('/login');
  await page.evaluate((t) => localStorage.setItem('ims_token', t), token);
}

/** Alias — semantisch duidelijk wanneer een test specifiek de seed-user vereist. */
export const loginAsSeedAdmin = loginAsAdmin;
