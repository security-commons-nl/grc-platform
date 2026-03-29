#!/usr/bin/env python3
"""Auto-generate platform documentation from codebase introspection.

Generates:
  docs/platform-overzicht.html  — Functioneel (voor TIMS/stakeholders)
  docs/architectuur.html        — Technisch (voor developers/beheerders)

Usage:
  cd IMS-tooling && python generate-docs.py
"""

import sys
import os
import glob
import html
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# ── CSS shared between both docs ──────────────────────────────────────────

SHARED_CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg-primary: #0a0f1a;
    --bg-card: #111827;
    --bg-card-hover: #1f2937;
    --border: #374151;
    --text-primary: #f9fafb;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --accent: #6366f1;
    --accent-hover: #818cf8;
    --isms: #60a5fa;
    --pims: #a78bfa;
    --bcms: #34d399;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
  }

  body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; }
  h2 { font-size: 1.3rem; font-weight: 600; margin: 2rem 0 1rem; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
  h3 { font-size: 1rem; font-weight: 600; margin: 1.5rem 0 0.5rem; }

  .subtitle { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 2rem; }
  .generated { color: var(--text-muted); font-size: 0.75rem; margin-bottom: 2rem; }

  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
  .grid-2 { display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 1rem; }

  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    transition: border-color 0.2s;
  }
  .card:hover { border-color: var(--accent); }

  .badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
  }
  .badge-v { background: rgba(239,68,68,0.2); color: #fca5a5; }
  .badge-a { background: rgba(245,158,11,0.2); color: #fcd34d; }
  .badge-fase0 { background: rgba(99,102,241,0.2); color: #a5b4fc; }
  .badge-fase1 { background: rgba(96,165,250,0.2); color: #93c5fd; }
  .badge-fase2 { background: rgba(52,211,153,0.2); color: #6ee7b7; }
  .badge-fase3 { background: rgba(167,139,250,0.2); color: #c4b5fd; }
  .badge-agent { background: rgba(99,102,241,0.15); color: var(--accent); }
  .badge-method { background: rgba(52,211,153,0.15); color: var(--bcms); font-family: monospace; }

  .stat { text-align: center; }
  .stat-value { font-size: 2rem; font-weight: 700; color: var(--accent); }
  .stat-label { font-size: 0.8rem; color: var(--text-secondary); }

  .step-number {
    display: inline-flex; align-items: center; justify-content: center;
    width: 2.5rem; height: 2.5rem; border-radius: 8px;
    background: rgba(99,102,241,0.15); color: var(--accent);
    font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
  }

  .output-list { list-style: none; padding: 0; }
  .output-list li { padding: 0.2rem 0; font-size: 0.85rem; color: var(--text-secondary); }
  .output-list li::before { content: '→ '; color: var(--text-muted); }

  table { width: 100%; border-collapse: collapse; margin: 0.5rem 0; }
  th { text-align: left; padding: 0.5rem; font-size: 0.75rem; color: var(--text-muted); border-bottom: 1px solid var(--border); text-transform: uppercase; }
  td { padding: 0.5rem; font-size: 0.85rem; border-bottom: 1px solid rgba(55,65,81,0.5); }
  tr:hover td { background: rgba(99,102,241,0.05); }

  code { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; background: rgba(99,102,241,0.1); padding: 0.1rem 0.3rem; border-radius: 4px; }

  .dep-arrow { color: var(--text-muted); font-size: 0.8rem; }
  .dep-b { color: var(--danger); }
  .dep-w { color: var(--warning); }

  .nav { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
  .nav a { color: var(--accent); text-decoration: none; font-size: 0.85rem; padding: 0.4rem 0.8rem; border: 1px solid var(--border); border-radius: 8px; transition: all 0.2s; }
  .nav a:hover { background: var(--bg-card); border-color: var(--accent); }
"""


# ── Data extraction ───────────────────────────────────────────────────────

def get_steps_and_outputs():
    """Extract step definitions and outputs from seed migrations."""
    from app.models.core_models import Base
    # Parse seed data from migration files instead of DB
    steps = []
    step_data = [
        ("1", 0, "Bestuurlijk commitment", "sims"),
        ("2a", 0, "Organisatiecontext vaststellen", "tims"),
        ("2b", 0, "Scope bepalen", "sims"),
        ("3a", 0, "Governance- en beleidsvoorstel opstellen", "tims"),
        ("3b", 0, "Governance en beleid vaststellen", "sims"),
        ("4", 0, "Gap-analyse", "tims"),
        ("5", 0, "Registers & risicobeoordeling", "tims"),
        ("6", 0, "Normenkader & kerncontrols", "tims"),
        ("7", 1, "Onboarding & awareness lijnmanagement", "tims"),
        ("8", 1, "Koppeling processen, systemen & verwerkingen", "tims"),
        ("9", 1, "Risicoanalyse door lijnmanagement", "lijnmanagement"),
        ("10", 1, "Risicobehandeling & controls toewijzen", "tims"),
        ("11", 1, "Statement of Applicability (SoA)", "tims"),
        ("12", 1, "Monitoring & rapportage inrichten", "tims"),
        ("13", 2, "Interne audit plannen & uitvoeren", "tims"),
        ("14", 2, "Management review", "sims"),
        ("15", 2, "Afwijkingen, incidenten & corrigerende maatregelen", "discipline_eigenaar"),
        ("16", 2, "Evidence-verzameling & control-monitoring", "discipline_eigenaar"),
        ("17", 2, "PDCA-cyclus formaliseren", "tims"),
        ("18", 3, "Certificeringsgereedheid", "sims"),
        ("19", 3, "Geavanceerde analytics & rapportage", "tims"),
        ("20", 3, "Externe integraties", "tims"),
        ("21", 3, "Multi-framework optimalisatie", "tims"),
        ("22", 3, "Benchmarking & kennisdeling", "sims"),
    ]
    for num, phase, name, gremium in step_data:
        steps.append({"number": num, "phase": phase, "name": name, "gremium": gremium})
    return steps


def get_outputs():
    """Extract output definitions per step."""
    outputs = {}
    output_defs = [
        ("1", "Besluitmemo", "decision", "V"),
        ("1", "Besluitlog #001", "decision", "V"),
        ("2a", "Organisatiecontextdocument", "document", "V"),
        ("2a", "Stakeholderregister", "register", "V"),
        ("2a", "PII-rol", "document", "V"),
        ("2b", "Formeel scopebesluit", "decision", "V"),
        ("3a", "Concept governance-document", "document", "V"),
        ("3a", "Concept IMS-beleid", "document", "V"),
        ("3a", "Communicatiematrix", "document", "V"),
        ("3b", "Formeel governance-besluit", "decision", "V"),
        ("3b", "IMS-beleid (definitief)", "document", "V"),
        ("3b", "Besluitlog", "decision", "V"),
        ("4", "Nulmeting per domein", "document", "V"),
        ("4", "Volwassenheidsprofiel v1", "document", "V"),
        ("5", "Registerinventarisatie", "register", "V"),
        ("5", "Eerste risicobeeld", "document", "V"),
        ("5", "Risicobeoordelingsmethodiek", "document", "V"),
        ("6", "Normenkader", "document", "V"),
        ("6", "Minimale werkset kerncontrols", "document", "V"),
        ("6", "Besluitlog", "decision", "V"),
    ]
    for step_num, name, otype, req in output_defs:
        outputs.setdefault(step_num, []).append({"name": name, "type": otype, "requirement": req})
    return outputs


def get_agents():
    """Extract agent registry."""
    try:
        from app.services.agents.registry import AGENT_REGISTRY
        return [
            {"step": num, "name": cls.agent_name, "prompt": cls.prompt_file}
            for num, cls in AGENT_REGISTRY.items()
        ]
    except Exception:
        return []


def get_models():
    """Extract SQLAlchemy model info."""
    from app.models.core_models import Base
    tables = []
    for name, table in sorted(Base.metadata.tables.items()):
        cols = []
        for col in table.columns:
            cols.append({
                "name": col.name,
                "type": str(col.type),
                "nullable": col.nullable,
                "pk": col.primary_key,
                "fk": str(list(col.foreign_keys)[0].target_fullname) if col.foreign_keys else None,
            })
        tables.append({"name": name, "columns": cols})
    return tables


def get_routes():
    """Extract FastAPI routes."""
    from app.main import app
    routes = []

    def _extract(route_list, prefix=""):
        for r in route_list:
            if hasattr(r, "routes"):
                _extract(r.routes, prefix + getattr(r, "prefix", ""))
            elif hasattr(r, "methods") and hasattr(r, "path"):
                methods = sorted(r.methods - {"HEAD", "OPTIONS"})
                if methods:
                    routes.append({
                        "methods": methods,
                        "path": prefix + r.path,
                        "name": r.name or "",
                    })

    _extract(app.routes)
    return sorted(routes, key=lambda r: r["path"])


def get_migrations():
    """List alembic migrations."""
    mig_dir = Path(__file__).parent / "backend" / "alembic" / "versions"
    migrations = []
    for f in sorted(mig_dir.glob("*.py")):
        if f.name.startswith("__"):
            continue
        first_line = ""
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith('"""'):
                    first_line = line.strip().strip('"')
                    break
        migrations.append({"file": f.name, "description": first_line})
    return migrations


def get_test_stats():
    """Count tests per file."""
    test_dir = Path(__file__).parent / "backend" / "tests"
    stats = []
    total = 0
    for f in sorted(test_dir.glob("test_*.py")):
        count = 0
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith("async def test_") or line.strip().startswith("def test_"):
                    count += 1
        # Parametrize multiplier
        with open(f, encoding="utf-8") as fh:
            content = fh.read()
            if "parametrize" in content:
                import re
                matches = re.findall(r'@pytest\.mark\.parametrize\([^,]+,\s*\[([^\]]+)\]', content)
                for m in matches:
                    items = m.count("(")
                    if items > 1:
                        count += items - 1
        total += count
        stats.append({"file": f.name, "tests": count})
    return stats, total


def get_dependencies():
    """Step dependencies."""
    return [
        ("2a", "1", "B"), ("2b", "1", "B"), ("2b", "2a", "B"),
        ("3a", "2b", "B"), ("3b", "3a", "B"), ("4", "3b", "B"),
        ("5", "4", "B"), ("6", "5", "B"), ("7", "6", "B"),
        ("8", "7", "W"), ("9", "8", "B"), ("9", "7", "B"),
        ("10", "9", "B"), ("11", "10", "B"), ("12", "11", "W"),
        ("13", "12", "W"), ("13", "11", "B"), ("14", "13", "B"),
        ("15", "11", "W"), ("16", "10", "B"), ("17", "14", "B"),
        ("18", "17", "B"), ("19", "17", "W"), ("20", "17", "W"),
        ("21", "17", "W"), ("22", "18", "W"),
    ]


# ── HTML generation ──────────────────────────────────────────────────────

def generate_functional_html(steps, outputs, agents, deps):
    fase_labels = {0: "Fundament", 1: "Lijnmanagement", 2: "PDCA & Evidence", 3: "Volwassen GRC"}
    fase_badge = {0: "fase0", 1: "fase1", 2: "fase2", 3: "fase3"}
    agent_map = {a["step"]: a["name"] for a in agents}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Stats
    total_outputs = sum(len(v) for v in outputs.values())

    html_parts = [f"""<!DOCTYPE html>
<html lang="nl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IMS Platform — Overzicht</title>
<style>{SHARED_CSS}</style>
</head><body>
<h1>IMS Platform — Functioneel Overzicht</h1>
<p class="subtitle">Integrated Management System voor gemeenten (ISMS · PIMS · BCMS)</p>
<p class="generated">Auto-generated op {now} uit codebase</p>

<div class="nav">
  <a href="#stats">Statistieken</a>
  <a href="#stappen">22 Stappen</a>
  <a href="#agents">AI Agents</a>
  <a href="#deps">Afhankelijkheden</a>
  <a href="architectuur.html">→ Technische architectuur</a>
</div>

<h2 id="stats">Statistieken</h2>
<div class="grid">
  <div class="card stat"><div class="stat-value">{len(steps)}</div><div class="stat-label">Processtappen</div></div>
  <div class="card stat"><div class="stat-value">{total_outputs}</div><div class="stat-label">Output-definities (Fase 0)</div></div>
  <div class="card stat"><div class="stat-value">{len(agents)}</div><div class="stat-label">AI Agents</div></div>
  <div class="card stat"><div class="stat-value">4</div><div class="stat-label">Fasen</div></div>
</div>
"""]

    # Steps per fase
    html_parts.append('<h2 id="stappen">Processtappen</h2>')
    for fase in range(4):
        fase_steps = [s for s in steps if s["phase"] == fase]
        html_parts.append(f'<h3>Fase {fase} — {fase_labels[fase]} ({len(fase_steps)} stappen)</h3>')
        html_parts.append('<div class="grid">')
        for s in fase_steps:
            num = s["number"]
            agent_badge = f'<span class="badge badge-agent">{agent_map[num]}</span>' if num in agent_map else ''
            step_outputs = outputs.get(num, [])
            output_html = ""
            if step_outputs:
                items = "".join(
                    f'<li>{html.escape(o["name"])} <span class="badge badge-{"v" if o["requirement"]=="V" else "a"}">{o["requirement"]}</span></li>'
                    for o in step_outputs
                )
                output_html = f'<ul class="output-list">{items}</ul>'

            html_parts.append(f'''
              <div class="card">
                <div style="display:flex;gap:0.75rem;align-items:flex-start">
                  <div class="step-number">{html.escape(num)}</div>
                  <div style="flex:1">
                    <div style="font-weight:600;font-size:0.95rem">{html.escape(s["name"])}</div>
                    <div style="margin-top:0.3rem">
                      <span class="badge badge-{fase_badge[fase]}">Fase {fase}</span>
                      <span class="badge" style="background:rgba(156,163,175,0.15);color:var(--text-secondary)">{html.escape(s["gremium"])}</span>
                      {agent_badge}
                    </div>
                    {output_html}
                  </div>
                </div>
              </div>''')
        html_parts.append('</div>')

    # Agents
    html_parts.append('<h2 id="agents">AI Agents (Fase 0)</h2><div class="grid">')
    for a in agents:
        step = next((s for s in steps if s["number"] == a["step"]), None)
        step_name = step["name"] if step else "?"
        html_parts.append(f'''
          <div class="card">
            <div style="font-weight:600;color:var(--accent)">{html.escape(a["name"])}</div>
            <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.3rem">Stap {html.escape(a["step"])}: {html.escape(step_name)}</div>
            <div style="margin-top:0.5rem;font-size:0.8rem;color:var(--text-muted)">Prompt: <code>{html.escape(a["prompt"])}</code></div>
          </div>''')
    html_parts.append('</div>')

    # Dependencies
    html_parts.append('<h2 id="deps">Afhankelijkheden</h2><table><tr><th>Stap</th><th>Afhankelijk van</th><th>Type</th></tr>')
    for step_num, dep_num, dep_type in deps:
        cls = "dep-b" if dep_type == "B" else "dep-w"
        label = "Blokkerend" if dep_type == "B" else "Waarschuwing"
        html_parts.append(f'<tr><td><strong>{html.escape(step_num)}</strong></td><td>{html.escape(dep_num)}</td><td><span class="{cls}">{label}</span></td></tr>')
    html_parts.append('</table>')

    html_parts.append('</body></html>')
    return "\n".join(html_parts)


def generate_technical_html(tables, routes, migrations, test_stats, total_tests, agents):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html_parts = [f"""<!DOCTYPE html>
<html lang="nl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IMS Platform — Architectuur</title>
<style>{SHARED_CSS}</style>
</head><body>
<h1>IMS Platform — Technische Architectuur</h1>
<p class="subtitle">Datamodel · API · Services · Tests</p>
<p class="generated">Auto-generated op {now} uit codebase</p>

<div class="nav">
  <a href="#stats">Statistieken</a>
  <a href="#datamodel">Datamodel</a>
  <a href="#api">API Endpoints</a>
  <a href="#migrations">Migraties</a>
  <a href="#tests">Tests</a>
  <a href="platform-overzicht.html">→ Functioneel overzicht</a>
</div>

<h2 id="stats">Statistieken</h2>
<div class="grid">
  <div class="card stat"><div class="stat-value">{len(tables)}</div><div class="stat-label">Database tabellen</div></div>
  <div class="card stat"><div class="stat-value">{len(routes)}</div><div class="stat-label">API Endpoints</div></div>
  <div class="card stat"><div class="stat-value">{len(migrations)}</div><div class="stat-label">Migraties</div></div>
  <div class="card stat"><div class="stat-value">{total_tests}</div><div class="stat-label">Tests</div></div>
</div>
"""]

    # Data model
    html_parts.append('<h2 id="datamodel">Datamodel</h2><div class="grid-2">')
    for table in tables:
        cols_html = ""
        for col in table["columns"]:
            pk = " 🔑" if col["pk"] else ""
            fk = f' → <code>{html.escape(col["fk"])}</code>' if col["fk"] else ""
            null = " (nullable)" if col["nullable"] and not col["pk"] else ""
            cols_html += f'<tr><td><code>{html.escape(col["name"])}</code>{pk}</td><td style="color:var(--text-muted)">{html.escape(str(col["type"]))}{null}{fk}</td></tr>'

        html_parts.append(f'''
          <div class="card">
            <div style="font-weight:600;font-family:monospace;color:var(--accent)">{html.escape(table["name"])}</div>
            <div style="font-size:0.75rem;color:var(--text-muted);margin:0.3rem 0">{len(table["columns"])} kolommen</div>
            <table>{cols_html}</table>
          </div>''')
    html_parts.append('</div>')

    # API
    html_parts.append('<h2 id="api">API Endpoints</h2><table><tr><th>Methode</th><th>Pad</th><th>Naam</th></tr>')
    for r in routes:
        methods = " ".join(f'<span class="badge badge-method">{m}</span>' for m in r["methods"])
        html_parts.append(f'<tr><td>{methods}</td><td><code>{html.escape(r["path"])}</code></td><td style="color:var(--text-muted)">{html.escape(r["name"])}</td></tr>')
    html_parts.append('</table>')

    # Migrations
    html_parts.append('<h2 id="migrations">Migratie-keten</h2><table><tr><th>Bestand</th><th>Beschrijving</th></tr>')
    for m in migrations:
        html_parts.append(f'<tr><td><code>{html.escape(m["file"])}</code></td><td>{html.escape(m["description"])}</td></tr>')
    html_parts.append('</table>')

    # Tests
    html_parts.append(f'<h2 id="tests">Tests ({total_tests} totaal)</h2><div class="grid">')
    for s in test_stats:
        html_parts.append(f'''
          <div class="card" style="display:flex;justify-content:space-between;align-items:center">
            <code>{html.escape(s["file"])}</code>
            <span class="stat-value" style="font-size:1.2rem">{s["tests"]}</span>
          </div>''')
    html_parts.append('</div>')

    html_parts.append('</body></html>')
    return "\n".join(html_parts)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print("Extracting data from codebase...")

    steps = get_steps_and_outputs()
    outputs = get_outputs()
    agents = get_agents()
    deps = get_dependencies()
    tables = get_models()
    routes = get_routes()
    migrations = get_migrations()
    test_stats, total_tests = get_test_stats()

    print(f"  {len(steps)} steps, {sum(len(v) for v in outputs.values())} outputs")
    print(f"  {len(agents)} agents")
    print(f"  {len(tables)} tables, {len(routes)} routes")
    print(f"  {len(migrations)} migrations, {total_tests} tests")

    docs_dir = Path(__file__).parent / "docs"
    docs_dir.mkdir(exist_ok=True)

    # Functional
    func_html = generate_functional_html(steps, outputs, agents, deps)
    func_path = docs_dir / "platform-overzicht.html"
    func_path.write_text(func_html, encoding="utf-8")
    print(f"\n  Written: {func_path}")

    # Technical
    tech_html = generate_technical_html(tables, routes, migrations, test_stats, total_tests, agents)
    tech_path = docs_dir / "architectuur.html"
    tech_path.write_text(tech_html, encoding="utf-8")
    print(f"  Written: {tech_path}")

    print("\nDone! Open the HTML files in a browser to view.")


if __name__ == "__main__":
    main()
