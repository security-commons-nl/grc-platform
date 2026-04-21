# Bijdragen aan grc-platform

Bedankt voor je interesse. Deze repo volgt de organisatiebrede richtlijnen van security-commons-nl:

- [CONTRIBUTING.md (org-wide)](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md)
- [DOCUMENTATION-STANDARD.md](https://github.com/security-commons-nl/.github/blob/main/DOCUMENTATION-STANDARD.md)
- [PRINCIPLES.md](https://github.com/security-commons-nl/.github/blob/main/PRINCIPLES.md)

## Project-specifieke werkwijze

Zie [docs/development.md](docs/development.md) voor de volledige ontwikkelaarsgids: commands, architectuur, data-modellen, auth, UI-principes en ontwerpprincipes.

### Tests draaien

```bash
docker-compose exec api pytest --tb=short
```

### Documentatie genereren

```bash
python generate-docs.py
```
Dit produceert `docs/platform-overzicht.html` en `docs/architectuur.html` uit de codebase — niet handmatig bewerken.

### PRs

- Elke bouwsteen heeft een test. Geen code zonder eval.
- Gedragswijzigingen die zichtbaar zijn voor gebruikers vereisen update van `docs/gebruik.md`, `docs/architectuur.md` of `docs/configuratie.md`.
- EU Data Sovereignty: geen externe AI-APIs zonder juridische clearance.
