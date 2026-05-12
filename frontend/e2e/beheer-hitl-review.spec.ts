import { test, expect } from '@playwright/test';
import { loginAsSeedAdmin, TENANT_ID } from './helpers/auth';
import { queryScalar, rowExists } from './helpers/db';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const PG_USER = process.env.POSTGRES_USER ?? 'postgres';
const PG_DB = process.env.POSTGRES_DB ?? 'ims';

function psql(sql: string): string {
  return execFileSync(
    'docker',
    [
      'compose',
      'exec',
      '-T',
      'db',
      'psql',
      '-U',
      PG_USER,
      '-d',
      PG_DB,
      '-t',
      '-A',
      '-q',
      '-c',
      sql,
    ],
    { encoding: 'utf-8', cwd: path.resolve(process.cwd(), '..') },
  )
    .trim()
    .split('\n')[0] // INSERT...RETURNING geeft soms ook "INSERT 0 1"-statusregel mee
    .trim();
}

/**
 * Seed een AI-audit-log direct in DB (zonder via een agent te gaan).
 * UI-test draait dan op deze rij.
 */
function seedAuditLog(agentName: string): string {
  // De id-kolom heeft geen DB-default — ORM zet `uuid.uuid4()` toe. Bij direct SQL
  // moeten we de UUID expliciet meegeven via gen_random_uuid() (pgcrypto/PG 13+).
  return psql(
    `INSERT INTO ai_audit_logs (id, tenant_id, agent_name, model, prompt_tokens, completion_tokens) ` +
      `VALUES (gen_random_uuid(), '${TENANT_ID}', '${agentName}', 'gpt-4o', 120, 80) RETURNING id::text;`,
  );
}

test.describe('Beheer — HITL-review', () => {
  test('reviewer ziet audit-log → legt review vast → DB-rij + tellingen kloppen', async ({
    page,
  }) => {
    const agentName = `e2e-hitl-${Date.now()}`;
    const auditId = seedAuditLog(agentName);
    expect(auditId).toMatch(/[0-9a-f-]{36}/);

    await loginAsSeedAdmin(page);
    await page.goto('/beheer/hitl-checkpoints');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'HITL-review', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    const row = page.locator('tr', { hasText: agentName });
    await expect(row).toBeVisible({ timeout: 10_000 });
    await expect(row).toContainText('gpt-4o');

    // Open detailpaneel
    await row.getByRole('button', { name: 'Bekijk' }).click();
    await expect(page.getByText('Nieuwe review')).toBeVisible();

    // Beslissing + motivatie invullen. Motivatie-textarea is niet via htmlFor
    // gekoppeld — selectie via placeholder is stabieler dan via label.
    await page.getByLabel('Beslissing').selectOption('approved');
    await page
      .getByPlaceholder('Waarom neemt u deze beslissing')
      .fill('E2E: agent-output gecontroleerd en correct.');
    await page.getByRole('button', { name: 'Review vastleggen' }).click();

    // UI: historie toont 1 entry
    await expect(page.getByText('Historie (1)')).toBeVisible({ timeout: 10_000 });

    // DB: hitl-checkpoint-rij staat in juiste audit_log + tenant
    expect(
      rowExists(
        'ai_hitl_checkpoints',
        `audit_log_id = '${auditId}' AND decision = 'approved' AND tenant_id = '${TENANT_ID}'`,
      ),
    ).toBe(true);

    const reason = queryScalar<string>(
      `SELECT reason FROM ai_hitl_checkpoints WHERE audit_log_id = '${auditId}' ORDER BY created_at DESC LIMIT 1;`,
    );
    expect(reason).toContain('E2E:');
  });

  test('audit-logs filter "alleen niet-gereviewd" verbergt al-gereviewde rijen', async ({
    page,
  }) => {
    const reviewedAgent = `e2e-reviewed-${Date.now()}`;
    const auditId = seedAuditLog(reviewedAgent);
    // Direct in DB een review toevoegen (geen tussenkomst van UI). id + created_at
    // expliciet zetten omdat de DB hier geen default heeft (ORM doet uuid.uuid4()).
    // reviewer_user_id is NOT NULL → seed-admin gebruiken.
    const seedAdminId = '00000000-0000-0000-0000-000000000002';
    psql(
      `INSERT INTO ai_hitl_checkpoints (id, tenant_id, audit_log_id, reviewer_user_id, decision, reason, created_at) ` +
        `VALUES (gen_random_uuid(), '${TENANT_ID}', '${auditId}', '${seedAdminId}', 'approved', 'seed', NOW());`,
    );

    await loginAsSeedAdmin(page);
    await page.goto('/beheer/hitl-checkpoints');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('tr', { hasText: reviewedAgent })).toBeVisible({ timeout: 10_000 });

    // Filter op alleen-niet-gereviewd
    await page.getByLabel('Toon').selectOption('unreviewed');
    await page.waitForLoadState('networkidle');

    // Reviewed agent moet verdwijnen
    await expect(page.locator('tr', { hasText: reviewedAgent })).toHaveCount(0, {
      timeout: 10_000,
    });
  });
});
