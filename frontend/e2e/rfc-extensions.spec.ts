import { test, expect, type APIRequestContext } from '@playwright/test';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

async function getDevToken(request: APIRequestContext): Promise<string> {
  const r = await request.post(`${API_BASE}/api/v1/auth/dev-token`, {
    data: {
      user_id: '00000000-0000-0000-0000-000000000001',
      tenant_id: '00000000-0000-0000-0000-000000000001',
      role: 'admin',
    },
  });
  expect(r.ok()).toBeTruthy();
  return (await r.json()).access_token;
}

test.describe('RFC 0001 + 0002 — API-flow voor extensions', () => {
  test('custom-fields lifecycle: create → list → use op risico → delete', async ({ request }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();
    const fieldName = `e2e_field_${stamp}`;

    // 1. Definitie aanmaken
    const createDef = await request.post(`${API_BASE}/api/v1/custom-fields/`, {
      data: {
        entity_type: 'risk',
        field_name: fieldName,
        display_label: 'E2E veld',
        json_schema: { type: 'string', maxLength: 100 },
        is_required: false,
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(createDef.status(), await createDef.text()).toBe(201);
    const def = await createDef.json();

    // 2. Definitie verschijnt in list (gefilterd op risk)
    const listDef = await request.get(
      `${API_BASE}/api/v1/custom-fields/?entity_type=risk`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    expect(listDef.status()).toBe(200);
    const defs = (await listDef.json()) as Array<{ field_name: string }>;
    expect(defs.some((d) => d.field_name === fieldName)).toBe(true);

    // 3. Reserved-namespace blokkeert botsing
    const reserved = await request.post(`${API_BASE}/api/v1/custom-fields/`, {
      data: {
        entity_type: 'risk',
        field_name: 'tenant_id',
        display_label: 'Bots',
        json_schema: { type: 'string' },
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(reserved.status()).toBe(409);

    // 4. Opruimen
    const del = await request.delete(`${API_BASE}/api/v1/custom-fields/${def.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(del.status()).toBe(204);
  });

  test('org-units: boom + cycle-prevention + risk-filter', async ({ request }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();

    async function mkUnit(name: string, parentId: string | null = null) {
      const r = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
        data: {
          name: `${name}-${stamp}`,
          unit_type: 'cluster',
          parent_id: parentId,
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(r.status(), await r.text()).toBe(201);
      return await r.json();
    }

    // Boom: cluster → team
    const cluster = await mkUnit('Cluster');
    const team = await mkUnit('Team', cluster.id);

    // Cycle-prevention: cluster.parent = team → 422
    const cycle = await request.patch(
      `${API_BASE}/api/v1/organizational-units/${cluster.id}`,
      {
        data: { parent_id: team.id },
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    expect(cycle.status()).toBe(422);

    // Descendants endpoint geeft beide IDs terug
    const desc = await request.get(
      `${API_BASE}/api/v1/organizational-units/${cluster.id}/descendants`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    expect(desc.status()).toBe(200);
    const ids = new Set((await desc.json()) as string[]);
    expect(ids.has(cluster.id)).toBe(true);
    expect(ids.has(team.id)).toBe(true);

    // Maak scope + 2 risico's (op cluster en op team)
    const scopeResp = await request.post(`${API_BASE}/api/v1/scopes/`, {
      data: { name: `Scope-${stamp}`, type: 'cluster', domain: 'ISMS' },
      headers: { Authorization: `Bearer ${token}` },
    });
    const scopeId = (await scopeResp.json()).id;

    async function mkRisk(title: string, unitId: string) {
      await request.post(`${API_BASE}/api/v1/risks/`, {
        data: {
          scope_id: scopeId,
          domain: 'ISMS',
          title: `${title}-${stamp}`,
          description: 'E2E',
          likelihood: 2,
          impact: 3,
          organizational_unit_id: unitId,
        },
        headers: { Authorization: `Bearer ${token}` },
      });
    }
    await mkRisk('OnCluster', cluster.id);
    await mkRisk('OnTeam', team.id);

    // Filter direct = alleen cluster-risico
    const direct = await request.get(
      `${API_BASE}/api/v1/risks/?organizational_unit_id=${cluster.id}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    const directTitles = ((await direct.json()) as Array<{ title: string }>).map(
      (r) => r.title,
    );
    expect(directTitles.some((t) => t.startsWith('OnCluster'))).toBe(true);
    expect(directTitles.some((t) => t.startsWith('OnTeam'))).toBe(false);

    // include_descendants = beide
    const incl = await request.get(
      `${API_BASE}/api/v1/risks/?organizational_unit_id=${cluster.id}&include_descendants=true`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    const inclTitles = ((await incl.json()) as Array<{ title: string }>).map(
      (r) => r.title,
    );
    expect(inclTitles.some((t) => t.startsWith('OnCluster'))).toBe(true);
    expect(inclTitles.some((t) => t.startsWith('OnTeam'))).toBe(true);
  });
});
