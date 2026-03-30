import { test, expect } from '@playwright/test';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'Inloggen' }).click();
  await page.waitForURL(/\/inrichten/, { timeout: 15_000, waitUntil: 'domcontentloaded' });
  await expect(page.getByText('Fase 0')).toBeVisible({ timeout: 10_000 });
}

test.describe('Inrichtingsflow — stap 1', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('stap 1 openen en starten', async ({ page }) => {
    await page.getByText('Bestuurlijk commitment').click();
    await expect(page.getByText('Stap 1')).toBeVisible({ timeout: 5_000 });

    const startButton = page.getByRole('button', { name: 'Start deze stap' });
    if (await startButton.isVisible()) {
      await startButton.click();
      await expect(page.getByText('In uitvoering')).toBeVisible({ timeout: 5_000 });
    }
  });

  test('AI-assistent opent met greeting', async ({ page }) => {
    await page.getByText('Bestuurlijk commitment').click();
    await expect(page.getByText('Stap 1')).toBeVisible({ timeout: 5_000 });

    // Start if needed
    const startButton = page.getByRole('button', { name: 'Start deze stap' });
    if (await startButton.isVisible()) {
      await startButton.click();
      await expect(page.getByText('In uitvoering')).toBeVisible({ timeout: 5_000 });
    }

    // Open chat
    await page.getByText('AI-assistent').click();
    await expect(page.getByText('commitment-agent')).toBeVisible({ timeout: 10_000 });
    // Greeting contains "besluitmemo" — verify chat panel has agent message
    await expect(page.getByText('Welkom bij stap 1')).toBeVisible({ timeout: 5_000 });
  });

  test('bericht sturen naar agent', async ({ page }) => {
    test.setTimeout(90_000);

    await page.getByText('Bestuurlijk commitment').click();
    await expect(page.getByText('Stap 1')).toBeVisible({ timeout: 5_000 });

    const startButton = page.getByRole('button', { name: 'Start deze stap' });
    if (await startButton.isVisible()) {
      await startButton.click();
      await expect(page.getByText('In uitvoering')).toBeVisible({ timeout: 5_000 });
    }

    await page.getByText('AI-assistent').click();
    await expect(page.getByText('commitment-agent')).toBeVisible({ timeout: 10_000 });

    const chatInput = page.getByPlaceholder('Typ een bericht...');
    await chatInput.fill('We willen een IMS opzetten voor de hele gemeente.');
    await chatInput.press('Enter');

    // Wait for agent response (LLM call)
    await expect(page.getByText('Agent denkt na...')).toBeVisible({ timeout: 5_000 });
    // Wait for actual response (up to 60s)
    await expect(page.locator('[class*="bg-neutral-50"]').last()).toBeVisible({ timeout: 60_000 });
  });

  test('outputs tonen met koppel-knoppen', async ({ page }) => {
    await page.getByText('Bestuurlijk commitment').click();
    await expect(page.getByText('Stap 1')).toBeVisible({ timeout: 5_000 });

    await expect(page.getByText('Outputs')).toBeVisible();
    // Check outputs are visible (text split across elements)
    await expect(page.getByText('Besluitmemo').first()).toBeVisible();
    await expect(page.getByText('Besluitlog #001').first()).toBeVisible();
  });

  test('besluitlog pagina werkt', async ({ page }) => {
    await page.getByRole('link', { name: 'Besluiten' }).click();
    await expect(page.getByText('Besluitlog')).toBeVisible({ timeout: 5_000 });
  });
});
