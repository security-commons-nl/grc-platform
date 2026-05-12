import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID } from './helpers/auth';
import { countRows, rowExists } from './helpers/db';

test.describe('Admin — Organisatie (boom-editor)', () => {
  test('UI maakt unit aan → API list bevat hem → DB rij staat in juiste tenant', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/organisatie');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Organisatie', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    const before = countRows('ims_organizational_units', `tenant_id = '${TENANT_ID}'`);

    await page.getByRole('button', { name: 'Nieuwe eenheid' }).click();
    await expect(
      page.getByRole('heading', { name: 'Nieuwe organisatie-eenheid' }),
    ).toBeVisible();

    const stamp = Date.now();
    const unitName = `E2E-Cluster-${stamp}`;
    const unitCode = `E2E${stamp.toString().slice(-5)}`;

    await page.getByLabel('Naam *').fill(unitName);
    await page.getByLabel('Code').fill(unitCode);
    await page.getByLabel('Type *').selectOption('cluster');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    // UI: rij verschijnt in boom
    await expect(
      page.locator('button', { hasText: unitName }),
    ).toBeVisible({ timeout: 10_000 });

    // DB: 1 nieuwe rij in juiste tenant
    expect(countRows('ims_organizational_units', `tenant_id = '${TENANT_ID}'`)).toBe(before + 1);
    expect(
      rowExists(
        'ims_organizational_units',
        `name = '${unitName}' AND code = '${unitCode}' AND unit_type = 'cluster' AND parent_id IS NULL AND tenant_id = '${TENANT_ID}'`,
      ),
    ).toBe(true);
  });

  test('UI verwijdert unit → DB-rij verdwijnt', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/organisatie');
    await page.waitForLoadState('networkidle');

    // Eerst aanmaken zodat we iets te wissen hebben
    await page.getByRole('button', { name: 'Nieuwe eenheid' }).click();
    const stamp = Date.now();
    const unitName = `E2E-Delete-${stamp}`;
    await page.getByLabel('Naam *').fill(unitName);
    await page.getByLabel('Type *').selectOption('team');
    await page.getByRole('button', { name: 'Opslaan' }).click();
    await expect(page.locator('button', { hasText: unitName })).toBeVisible({ timeout: 10_000 });

    expect(rowExists('ims_organizational_units', `name = '${unitName}'`)).toBe(true);

    // Selecteren in boom
    await page.locator('button', { hasText: unitName }).click();
    await expect(page.getByRole('heading', { name: unitName })).toBeVisible();

    // confirm()-dialog accepteren
    page.once('dialog', (d) => d.accept());
    await page.getByRole('button', { name: 'Verwijderen' }).click();

    // UI: rij weg uit boom
    await expect(page.locator('button', { hasText: unitName })).toHaveCount(0, {
      timeout: 10_000,
    });

    // DB: rij weg
    expect(rowExists('ims_organizational_units', `name = '${unitName}'`)).toBe(false);
  });
});
