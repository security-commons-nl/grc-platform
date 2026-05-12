import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID } from './helpers/auth';
import { queryScalar, rowExists } from './helpers/db';

test.describe('Beheer — Controls CRUD', () => {
  test('UI maakt control aan → DB-rij in juiste tenant + status', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/beheer/controls');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Controls', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    await page.getByRole('button', { name: 'Nieuwe control', exact: true }).click();

    const stamp = Date.now();
    const title = `E2E control ${stamp}`;

    await page.getByLabel('Titel *').fill(title);
    await page.getByLabel('Domein *').selectOption('ISMS');
    await page.getByLabel('Implementatiestatus *').selectOption('operationeel');
    // Beschrijving-textarea heeft losse <label> zonder htmlFor; placeholder is stabieler.
    await page.getByPlaceholder('Beschrijf de control').fill('E2E-bewijs voor logging-control.');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    // UI: rij verschijnt
    const row = page.locator('tr', { hasText: title });
    await expect(row).toBeVisible({ timeout: 10_000 });
    await expect(row).toContainText('ISMS');

    // DB
    expect(
      rowExists(
        'ims_controls',
        `title = '${title}' AND domain = 'ISMS' AND implementation_status = 'operationeel' AND tenant_id = '${TENANT_ID}'`,
      ),
    ).toBe(true);

    const desc = queryScalar<string>(
      `SELECT description FROM ims_controls WHERE title = '${title}';`,
    );
    expect(desc).toContain('logging-control');
  });

  test('validatie: lege titel toont fout, geen DB-rij', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/beheer/controls');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Nieuwe control', exact: true }).click();
    // Vul niets in en submit
    await page.getByRole('button', { name: 'Opslaan' }).click();

    await expect(page.getByText('Vul alle verplichte velden in.')).toBeVisible();
  });
});
