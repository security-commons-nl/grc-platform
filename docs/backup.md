# Backup-strategie

> Voor systeembeheerders die het GRC-platform productie-rijp draaien en zich willen verzekeren van data-herstel bij incidenten.

---

## Strategie

| Frequentie | Bewaartermijn | Doel |
|------------|---------------|------|
| **Dagelijks** | 7 dumps | Snel herstel van recente datacorruptie of accidentele wijzigingen |
| **Wekelijks** (zondag) | 4 dumps | Langere terugkijkbare horizon voor moeilijker zichtbare problemen |

Een wekelijkse dump is automatisch ook de dagelijkse dump van die dag (zondag) — geen dubbele dump.

**Total: 7 + 4 = max. 11 bestanden op disk.** Voor een gemiddelde gemeentelijke deployment (10–50 MB ruwe data → 2–10 MB gzipt) komt dat neer op enkele tientallen MB schijfruimte.

---

## Scripts

| Script | Doel |
|--------|------|
| `scripts/backup-postgres.sh` | Maakt een gzipte pg_dump, past retentie toe |
| `scripts/restore-postgres.sh` | Restored een dump in de live database (vereist bevestiging) |
| `scripts/test-backup-restore.sh` | End-to-end test: backup → restore in test-database → vergelijk |

Alle scripts lezen credentials uit `.env` en gebruiken `docker compose exec` op de `db`-service.

---

## Dagelijkse backup automatiseren (cron)

Voeg toe aan de crontab van de gebruiker die de Docker-stack beheert:

```cron
# Dagelijks om 03:00 — backup met retentie
0 3 * * * /opt/grc-platform/scripts/backup-postgres.sh >> /var/log/grc-backup.log 2>&1

# Wekelijks op maandag 04:00 — verifieer backup/restore pipeline
0 4 * * 1 /opt/grc-platform/scripts/test-backup-restore.sh >> /var/log/grc-backup-test.log 2>&1
```

Pas `/opt/grc-platform` aan naar het pad waar je de repo hebt staan.

**Belangrijk:** de cron-gebruiker moet rechten hebben op de Docker-daemon (lid van `docker`-groep of root).

---

## Configuratie

Het backup-script accepteert environment-variabelen om de standaarden te overschrijven:

| Variabele | Default | Beschrijving |
|-----------|---------|--------------|
| `BACKUP_DIR` | `./backups` | Doelmap voor dumps |
| `BACKUP_DAILY_RETENTION` | `7` | Aantal te bewaren dagelijkse dumps |
| `BACKUP_WEEKLY_RETENTION` | `4` | Aantal te bewaren wekelijkse dumps |
| `COMPOSE_FILE` | `docker-compose.yml` | Compose-bestand met de db-service |
| `DB_SERVICE` | `db` | Service-naam van de PostgreSQL container |
| `ENV_FILE` | `./.env` | Locatie van de .env met credentials |

Voorbeeld voor afwijkende backup-locatie:

```bash
BACKUP_DIR=/mnt/nas/grc-backups ./scripts/backup-postgres.sh
```

---

## Herstellen

**Waarschuwing:** restore drops en herstelt de database. Alle huidige data gaat verloren — maak eerst een backup van de huidige staat als die nog waardevol is.

```bash
# Vraagt om bevestiging (typ de database-naam)
./scripts/restore-postgres.sh backups/daily/grc-20260512-030000.sql.gz

# Daarna: verifieer schema en pas eventueel nieuwe migraties toe
docker compose exec api alembic current
docker compose exec api alembic upgrade head
docker compose restart api
```

---

## Backup-test ritueel

Een backup die je nooit hebt teruggezet is geen backup. Test daarom maandelijks of de pipeline werkt:

```bash
./scripts/test-backup-restore.sh
```

Dit script maakt een nieuwe backup, restored die in een tijdelijke `ims_restore_test` database, vergelijkt tabel- en rij-aantallen tussen origineel en restore, en ruimt de test-database op.

Exit-code 0 = succes. Bij falen: onderzoek **direct** voordat je een echte recovery nodig hebt.

**Aanbeveling:** zet dit als wekelijkse cron (zie boven). Logs naar `/var/log/grc-backup-test.log` zodat je periodiek kan controleren of de tests slagen.

---

## Off-site backups

Voor verdere bescherming tegen disk-falen, ransomware of fysieke schade aan de server: kopieer de backup-map periodiek naar een externe locatie. Suggesties:

- **rsync** naar een NAS of tweede server: `rsync -avz ./backups/ backup-host:/srv/grc-backups/`
- **rclone** naar object storage (S3, Azure Blob, een EU-conforme aanbieder zoals Scaleway/Hetzner Storage Box)
- **Restic** of **borg** voor encrypted, deduped backups

Belangrijk bij off-site:
- Versleutel de dumps voordat ze de organisatie verlaten (`gpg --symmetric` of restic native encryption)
- Bewaar de encryptie-sleutel apart van de backup-locatie
- Test ook de off-site restore minstens halfjaarlijks

---

## Wat zit er in een dump

`pg_dump` met `--no-owner --no-privileges` produceert een schema + data dump die in elke PostgreSQL 16+ instance met pgvector kan worden teruggezet. Inclusief:

- Alle tabellen en data
- Indexen, constraints, foreign keys
- Sequences (auto-increment teller-stand)
- pgvector embeddings in `ims_knowledge_chunks`

Niet inclusief:
- RLS-policies — die staan in `alembic/versions/002_enable_rls.py` en worden hersteld door `alembic upgrade head` na restore
- Database-rolen en grants (deze maak je expliciet via de seed-stap)

Daarom is het **na een restore altijd nodig** om `alembic upgrade head` te draaien, zodat eventuele migraties die niet in de dump zitten alsnog toegepast worden en de RLS-policies actief zijn.
