import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID } from './helpers/auth';
import { rowExists, queryScalar } from './helpers/db';

test.describe('Admin — Custom velden (form-builder)', () => {
  test('UI definieert string-veld → DB rij + json_schema correct', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/velden');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Custom velden', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    await page.getByRole('button', { name: 'Nieuw veld' }).click();
    await expect(page.getByRole('heading', { name: 'Nieuw custom-veld' })).toBeVisible();

    const stamp = Date.now();
    const fieldName = `e2e_string_${stamp}`;

    await page.getByLabel('Op entiteit *').selectOption('risk');
    await page.getByLabel('Type *', { exact: true }).selectOption('string');
    await page.getByLabel('Veldnaam (snake_case) *').fill(fieldName);
    await page.getByLabel('Label (zichtbaar) *').fill('E2E veld string');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    const row = page.locator('tr', { hasText: fieldName });
    await expect(row).toBeVisible({ timeout: 10_000 });
    await expect(row).toContainText('Tekst');

    expect(
      rowExists(
        'ims_custom_field_definitions',
        `field_name = '${fieldName}' AND entity_type = 'risk' AND tenant_id = '${TENANT_ID}'`,
      ),
    ).toBe(true);

    // json_schema bevat 'type' = 'string'
    const schemaType = queryScalar<string>(
      `SELECT json_schema->>'type' FROM ims_custom_field_definitions WHERE field_name = '${fieldName}';`,
    );
    expect(schemaType).toBe('string');
  });

  test('UI definieert enum-veld → json_schema bevat enum-array', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/velden');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Nieuw veld' }).click();

    const stamp = Date.now();
    const fieldName = `e2e_enum_${stamp}`;

    await page.getByLabel('Op entiteit *').selectOption('control');
    await page.getByLabel('Type *', { exact: true }).selectOption('enum');
    await page.getByLabel('Veldnaam (snake_case) *').fill(fieldName);
    await page.getByLabel('Label (zichtbaar) *').fill('E2E enum');
    await page.getByLabel('Keuze-waarden (komma-gescheiden) *').fill('Alpha, Beta, Gamma');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    await expect(page.locator('tr', { hasText: fieldName })).toBeVisible({ timeout: 10_000 });

    const enumStr = queryScalar<string>(
      `SELECT json_schema->'enum' FROM ims_custom_field_definitions WHERE field_name = '${fieldName}';`,
    );
    expect(enumStr).toBeTruthy();
    expect(JSON.parse(enumStr as string)).toEqual(['Alpha', 'Beta', 'Gamma']);
  });

  test('UI verwijdert veld → DB-rij weg', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/velden');
    await page.waitForLoadState('networkidle');

    // Setup
    await page.getByRole('button', { name: 'Nieuw veld' }).click();
    const stamp = Date.now();
    const fieldName = `e2e_del_${stamp}`;
    await page.getByLabel('Veldnaam (snake_case) *').fill(fieldName);
    await page.getByLabel('Label (zichtbaar) *').fill('E2E delete');
    await page.getByRole('button', { name: 'Opslaan' }).click();
    await expect(page.locator('tr', { hasText: fieldName })).toBeVisible({ timeout: 10_000 });
    expect(rowExists('ims_custom_field_definitions', `field_name = '${fieldName}'`)).toBe(true);

    // Delete via UI (confirm-dialog accepteren)
    page.once('dialog', (d) => d.accept());
    await page
      .locator('tr', { hasText: fieldName })
      .getByRole('button', { name: 'Verwijderen' })
      .click();

    await expect(page.locator('tr', { hasText: fieldName })).toHaveCount(0, { timeout: 10_000 });
    expect(rowExists('ims_custom_field_definitions', `field_name = '${fieldName}'`)).toBe(false);
  });
});
