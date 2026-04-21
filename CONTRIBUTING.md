# Bijdragen aan grc-platform

Iets delen of verbeteren? Drie manieren, van makkelijk naar technisch.

## 1. Iets aanbieden of melden — geen Git-ervaring nodig

→ [**Bijdrage aanbieden**](https://github.com/security-commons-nl/grc-platform/issues/new?template=bijdrage-aanbieden.md)
  Ervaring met ISMS/PIMS/BCMS-inrichting, een use case of verbetervoorstel.

→ [**Fout of verbetering**](https://github.com/security-commons-nl/grc-platform/issues/new?template=fout-of-verbetering.md)
  Iets klopt niet, kan beter, of mist.

Vul alleen de vragen in die voor jou relevant zijn — we helpen je met de rest.

**Geen GitHub-account?** [Maak er gratis een](https://github.com/signup) (2 minuten), of vraag iemand in je netwerk om namens jou te posten.

## 2. Meediscussiëren

→ [**Discussions**](https://github.com/orgs/security-commons-nl/discussions)

Voor vragen, ervaringen en ideeën zonder directe actie.

## 3. Voor ontwikkelaars — code aanleveren

### Volledige ontwikkelaarsgids

Zie [docs/development.md](docs/development.md) voor commands, architectuur, data-modellen, auth, UI-principes en ontwerpprincipes.

### Tests draaien

```bash
docker-compose exec api pytest --tb=short
```

### Kernregels

- **Elke bouwsteen heeft een test.** Geen code zonder eval.
- **Gedragswijzigingen** die zichtbaar zijn voor gebruikers → update `docs/gebruik.md`, `docs/architectuur.md` of `docs/configuratie.md`.
- **EU Data Sovereignty:** geen externe AI-APIs zonder juridische clearance.
- **Documentatie auto-genereren:** `python generate-docs.py` produceert `docs/platform-overzicht.html` en `docs/architectuur.html` uit de codebase — niet handmatig bewerken.

---

**Organisatiebrede richtlijnen**: [security-commons-nl/.github](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md)
