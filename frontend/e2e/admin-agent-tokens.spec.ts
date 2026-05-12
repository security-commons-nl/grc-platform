import { test, expect } from '@playwright/test';
import { loginAsAdmin, API_BASE } from './helpers/auth';

test.describe('Admin — Agent-tokens (NHI-uitgifte)', () => {
  test('two-step uitgifte → JWT met scope-claim → token werkt op gescopeerde endpoint', async ({
    page,
    request,
  }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/agent-tokens');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Agent-tokens', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    const stamp = Date.now();
    const agentName = `e2e-agent-${stamp}`;

    await page.getByLabel('Naam van de agent *').fill(agentName);
    await page.getByLabel('Geldigheid').selectOption(String(15)); // 15 minuten

    // Default-scope 'risks:read' is al aangevinkt. Voeg 'controls:read' toe.
    await page.getByLabel("Controls lezen").check();

    // Stap 1 → confirm-stap
    await page.getByRole('button', { name: 'Token uitgeven...' }).click();
    await expect(page.getByText('Weet u zeker dat u deze token wilt uitgeven?')).toBeVisible();

    // Stap 2 → bevestigen
    await page.getByRole('button', { name: 'Ja, uitgeven' }).click();

    // Success-card verschijnt
    await expect(
      page.getByRole('heading', { name: 'Token uitgegeven — kopieer nu' }),
    ).toBeVisible({ timeout: 10_000 });

    // De JWT wordt eenmalig getoond als <code> — uitlezen voor verdere checks
    const jwt = (await page.locator('code.block.break-all').textContent())?.trim() ?? '';
    expect(jwt.split('.').length).toBe(3); // header.payload.signature

    // Decode JWT-payload (base64url) en check claims
    const payloadB64 = jwt.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(Buffer.from(payloadB64, 'base64').toString('utf-8'));
    expect(payload.scope).toContain('risks:read');
    expect(payload.scope).toContain('controls:read');
    expect(payload.agent_name).toBe(agentName);

    // TTL 15 min → exp ≈ now+15m
    const ttlSec = payload.exp - payload.iat;
    expect(ttlSec).toBeGreaterThanOrEqual(14 * 60);
    expect(ttlSec).toBeLessThanOrEqual(16 * 60);

    // End-to-end: token kan met scope een endpoint hitten
    const inScope = await request.get(`${API_BASE}/api/v1/risks/`, {
      headers: { Authorization: `Bearer ${jwt}` },
    });
    expect(inScope.status()).toBe(200);
  });

  test('zonder scope → form-validatie blokkeert uitgifte', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/agent-tokens');
    await page.waitForLoadState('networkidle');

    await page.getByLabel('Naam van de agent *').fill('mag-niet');
    // Default 'risks:read' uitvinken — geen scope over
    await page.getByLabel("Risico's lezen").uncheck();

    await page.getByRole('button', { name: 'Token uitgeven...' }).click();
    await expect(
      page.getByText('Vul naam en minstens één scope in.'),
    ).toBeVisible();
  });
});
