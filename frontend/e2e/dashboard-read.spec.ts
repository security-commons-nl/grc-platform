import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers/auth';

test.describe('Beheer-dashboard + admin-read-pagina\'s', () => {
  test('dashboard rendert KPI-tegels + score-cards (drie domeinen)', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/beheer');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Beheer — Dashboard', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    // Drie domein-titels
    await expect(page.getByText('Informatiebeveiliging')).toBeVisible();
    await expect(page.getByText('Privacy', { exact: true })).toBeVisible();
    await expect(page.getByText('Bedrijfscontinuïteit')).toBeVisible();

    // KPI-tegel-labels (in <main>; "Controls" en "Incidenten" staan ook in de
    // sidebar — beperken tot main vermijdt strict-mode-violations).
    const main = page.getByRole('main');
    await expect(main.getByText("Open risico's")).toBeVisible();
    await expect(main.getByText('Controls', { exact: true })).toBeVisible();
    await expect(main.getByText('Open bevindingen')).toBeVisible();
    await expect(main.getByText('Incidenten', { exact: true })).toBeVisible();

    // Stappenscore-card
    await expect(page.getByText('Inrichtingsvoortgang')).toBeVisible();
  });

  test('admin/gebruikers laadt + bevat seed-admin-rij', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/gebruikers');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Gebruikersbeheer', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    // Seed-admin staat in tabel
    await expect(page.locator('tbody tr').first()).toBeVisible({ timeout: 10_000 });
  });

  test('admin/tenant laadt empty-state-uitleg', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/admin/tenant');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Tenant-instellingen', exact: true }),
    ).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText('Tenant-configuratie wordt via de API beheerd')).toBeVisible();
  });
});
