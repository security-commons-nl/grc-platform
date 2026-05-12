"""Tests voor RFC 0002 — organisatie-eenheden (sub-tenant hiërarchie)."""

import pytest

from tests.conftest import make_token


# ── Helpers ────────────────────────────────────────────────────────────────


async def _create_unit(client, token, name, parent_id=None, **extra):
    payload = {
        "name": name,
        "unit_type": "cluster",
        "parent_id": parent_id,
    }
    payload.update(extra)
    r = await client.post(
        "/api/v1/organizational-units/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    return r


async def _create_scope(client, token):
    r = await client.post(
        "/api/v1/scopes/",
        json={"name": "Scope", "type": "cluster", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    return r.json()["id"]


# ── CRUD ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_root_unit(client, tenant_token):
    r = await _create_unit(client, tenant_token, "Cluster A")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "Cluster A"
    assert body["parent_id"] is None
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_create_child_unit(client, tenant_token):
    parent = await _create_unit(client, tenant_token, "Cluster A")
    child = await _create_unit(
        client, tenant_token, "Team A1", parent_id=parent.json()["id"]
    )
    assert child.status_code == 201
    assert child.json()["parent_id"] == parent.json()["id"]


@pytest.mark.asyncio
async def test_self_parent_blocked_by_db_constraint(client, tenant_token):
    """De CHECK ck_org_unit_no_self_parent blokkeert id == parent_id."""
    unit = await _create_unit(client, tenant_token, "Cluster A")
    unit_id = unit.json()["id"]
    r = await client.patch(
        f"/api/v1/organizational-units/{unit_id}",
        json={"parent_id": unit_id},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    # Server-side check vangt het af vóór DB; would_create_cycle returnt True.
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_cycle_detection_via_patch(client, tenant_token):
    """A → B → C; nieuwe parent van A zetten op C zou cyclus geven."""
    a = (await _create_unit(client, tenant_token, "A")).json()
    b = (await _create_unit(client, tenant_token, "B", parent_id=a["id"])).json()
    c = (await _create_unit(client, tenant_token, "C", parent_id=b["id"])).json()

    r = await client.patch(
        f"/api/v1/organizational-units/{a['id']}",
        json={"parent_id": c["id"]},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422
    assert "cyclus" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_depth_limit_blocks_seventh_level(client, tenant_token):
    """Max diepte 6 — een 7e niveau aanmaken faalt met 422."""
    parent = (await _create_unit(client, tenant_token, "L1")).json()
    for i in range(2, 7):
        parent = (
            await _create_unit(
                client, tenant_token, f"L{i}", parent_id=parent["id"]
            )
        ).json()
    # L1..L6 staan; L7 moet falen
    r = await _create_unit(client, tenant_token, "L7", parent_id=parent["id"])
    assert r.status_code == 422
    assert "diepte" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_with_children_returns_409(client, tenant_token):
    parent = (await _create_unit(client, tenant_token, "Parent")).json()
    await _create_unit(client, tenant_token, "Child", parent_id=parent["id"])

    r = await client.delete(
        f"/api/v1/organizational-units/{parent['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_descendants_endpoint(client, tenant_token):
    a = (await _create_unit(client, tenant_token, "A")).json()
    b = (await _create_unit(client, tenant_token, "B", parent_id=a["id"])).json()
    c = (await _create_unit(client, tenant_token, "C", parent_id=b["id"])).json()

    r = await client.get(
        f"/api/v1/organizational-units/{a['id']}/descendants",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    ids = set(r.json())
    assert {a["id"], b["id"], c["id"]} == ids


@pytest.mark.asyncio
async def test_tree_endpoint(client, tenant_token):
    a = (await _create_unit(client, tenant_token, "A")).json()
    b = (await _create_unit(client, tenant_token, "B")).json()  # andere root
    a1 = (await _create_unit(client, tenant_token, "A1", parent_id=a["id"])).json()

    r = await client.get(
        "/api/v1/organizational-units/tree",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    tree = r.json()
    # Twee root-units
    root_ids = {n["id"] for n in tree}
    assert {a["id"], b["id"]} <= root_ids
    a_node = next(n for n in tree if n["id"] == a["id"])
    assert len(a_node["children"]) == 1
    assert a_node["children"][0]["id"] == a1["id"]


# ── Risk-filter integratie ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_risk_create_with_unit_in_other_tenant_rejected(
    client, tenant_token, admin_token
):
    """organizational_unit_id van andere tenant → 422."""
    # Andere tenant + unit daar.
    other_resp = await client.post(
        "/api/v1/tenants/",
        json={"name": "Andere", "type": "regio"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    other_token = make_token(tenant_id=other_resp.json()["id"], role="admin")
    other_unit = (
        await _create_unit(client, other_token, "Andere-cluster")
    ).json()

    # Probeer in eerste tenant een risk te maken met die unit
    scope_id = await _create_scope(client, tenant_token)
    r = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_id,
            "domain": "ISMS",
            "title": "Risico",
            "description": "Test",
            "likelihood": 1,
            "impact": 1,
            "organizational_unit_id": other_unit["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_risk_filter_by_unit(client, tenant_token):
    """Risk-list filtert op organizational_unit_id."""
    scope_id = await _create_scope(client, tenant_token)
    unit_a = (await _create_unit(client, tenant_token, "Cluster A")).json()
    unit_b = (await _create_unit(client, tenant_token, "Cluster B")).json()

    async def _mk(title, unit_id):
        await client.post(
            "/api/v1/risks/",
            json={
                "scope_id": scope_id,
                "domain": "ISMS",
                "title": title,
                "description": "Test",
                "likelihood": 1,
                "impact": 1,
                "organizational_unit_id": unit_id,
            },
            headers={"Authorization": f"Bearer {tenant_token}"},
        )

    await _mk("Risk in A", unit_a["id"])
    await _mk("Risk in A 2", unit_a["id"])
    await _mk("Risk in B", unit_b["id"])

    r = await client.get(
        f"/api/v1/risks/?organizational_unit_id={unit_a['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    titles = [risk["title"] for risk in r.json()]
    assert sorted(titles) == ["Risk in A", "Risk in A 2"]


@pytest.mark.asyncio
async def test_risk_filter_include_descendants(client, tenant_token):
    """include_descendants=true matcht ook child-units."""
    scope_id = await _create_scope(client, tenant_token)
    cluster = (await _create_unit(client, tenant_token, "Cluster")).json()
    team = (
        await _create_unit(client, tenant_token, "Team", parent_id=cluster["id"])
    ).json()

    async def _mk(title, unit_id):
        await client.post(
            "/api/v1/risks/",
            json={
                "scope_id": scope_id,
                "domain": "ISMS",
                "title": title,
                "description": "Test",
                "likelihood": 1,
                "impact": 1,
                "organizational_unit_id": unit_id,
            },
            headers={"Authorization": f"Bearer {tenant_token}"},
        )

    await _mk("On cluster", cluster["id"])
    await _mk("On team", team["id"])

    # Zonder include_descendants alleen direct
    r_direct = await client.get(
        f"/api/v1/risks/?organizational_unit_id={cluster['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert sorted([x["title"] for x in r_direct.json()]) == ["On cluster"]

    # Met include_descendants ook team-risico
    r_all = await client.get(
        f"/api/v1/risks/?organizational_unit_id={cluster['id']}&include_descendants=true",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert sorted([x["title"] for x in r_all.json()]) == ["On cluster", "On team"]


# ── Controls + Assessments koppelen aan org-units (RFC 0002 uitbreiding) ───


@pytest.mark.asyncio
async def test_control_create_with_unit(client, tenant_token):
    """Een control met geldige org-unit komt aan."""
    unit = (await _create_unit(client, tenant_token, "Cluster X")).json()
    r = await client.post(
        "/api/v1/controls/",
        json={
            "title": "Toegangscontrole op cluster",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "operationeel",
            "organizational_unit_id": unit["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["organizational_unit_id"] == unit["id"]


@pytest.mark.asyncio
async def test_control_cross_tenant_unit_rejected(client, tenant_token, admin_token):
    """Control met org-unit van andere tenant → 422."""
    other_resp = await client.post(
        "/api/v1/tenants/",
        json={"name": "Andere-Ctrl", "type": "regio"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    other_token = make_token(tenant_id=other_resp.json()["id"], role="admin")
    other_unit = (await _create_unit(client, other_token, "Andere-cluster-ctrl")).json()

    r = await client.post(
        "/api/v1/controls/",
        json={
            "title": "Cross-tenant",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "operationeel",
            "organizational_unit_id": other_unit["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_control_filter_by_unit_with_descendants(client, tenant_token):
    """Controls-list filtert op unit + include_descendants."""
    cluster = (await _create_unit(client, tenant_token, "Cluster Ctl")).json()
    team = (
        await _create_unit(client, tenant_token, "Team Ctl", parent_id=cluster["id"])
    ).json()

    async def _mk(title, unit_id):
        await client.post(
            "/api/v1/controls/",
            json={
                "title": title,
                "description": "Test",
                "domain": "ISMS",
                "implementation_status": "operationeel",
                "organizational_unit_id": unit_id,
            },
            headers={"Authorization": f"Bearer {tenant_token}"},
        )

    await _mk("Control on cluster", cluster["id"])
    await _mk("Control on team", team["id"])

    direct = await client.get(
        f"/api/v1/controls/?organizational_unit_id={cluster['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert sorted([x["title"] for x in direct.json()]) == ["Control on cluster"]

    deep = await client.get(
        f"/api/v1/controls/?organizational_unit_id={cluster['id']}&include_descendants=true",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert sorted([x["title"] for x in deep.json()]) == [
        "Control on cluster",
        "Control on team",
    ]


@pytest.mark.asyncio
async def test_assessment_create_with_unit(client, tenant_token):
    """Assessment met org-unit komt aan en is filterbaar."""
    unit = (await _create_unit(client, tenant_token, "Cluster Assm")).json()
    r = await client.post(
        "/api/v1/assessments/",
        json={
            "assessment_type": "audit",
            "domain": "ISMS",
            "status": "gepland",
            "planned_at": "2026-09-01",
            "organizational_unit_id": unit["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["organizational_unit_id"] == unit["id"]

    filt = await client.get(
        f"/api/v1/assessments/?organizational_unit_id={unit['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert any(a["organizational_unit_id"] == unit["id"] for a in filt.json())


@pytest.mark.asyncio
async def test_assessment_cross_tenant_unit_rejected(
    client, tenant_token, admin_token
):
    """Assessment met cross-tenant org-unit → 422."""
    other_resp = await client.post(
        "/api/v1/tenants/",
        json={"name": "Andere-Assm", "type": "regio"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    other_token = make_token(tenant_id=other_resp.json()["id"], role="admin")
    other_unit = (
        await _create_unit(client, other_token, "Andere-cluster-assm")
    ).json()

    r = await client.post(
        "/api/v1/assessments/",
        json={
            "assessment_type": "audit",
            "domain": "ISMS",
            "status": "gepland",
            "planned_at": "2026-09-15",
            "organizational_unit_id": other_unit["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422
