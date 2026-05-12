import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID } from './helpers/auth';
import { queryScalar, rowExists } from './helpers/db';

test.describe('Beheer — Incidenten', () => {
  test('UI meldt incident → DB-rij met status open + reported_at', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/beheer/incidenten');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Incidenten', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    await page.getByRole('button', { name: 'Nieuw incident', exact: true }).click();

    const stamp = Date.now();
    const title = `E2E-datalek-${stamp}`;
    await page.getByLabel('Titel *').fill(title);
    await page.getByLabel('Type *', { exact: true }).selectOption('datalek');
    await page.getByLabel('Ernst *').selectOption('hoog');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    const row = page.locator('tr', { hasText: title });
    await expect(row).toBeVisible({ timeout: 10_000 });
    await expect(row).toContainText('datalek');

    expect(
      rowExists(
        'ims_incidents',
        `title = '${title}' AND incident_type = 'datalek' AND severity = 'hoog' AND status = 'open' AND tenant_id = '${TENANT_ID}'`,
      ),
    ).toBe(true);

    const reportedAt = queryScalar<string>(
      `SELECT reported_at FROM ims_incidents WHERE title = '${title}';`,
    );
    expect(reportedAt).toBeTruthy();
  });
});
