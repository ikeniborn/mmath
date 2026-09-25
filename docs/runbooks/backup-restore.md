# Backup and restore

All application state lives in the external PostgreSQL database, so backup and restore are database operations. Never run `docker compose down --volumes` or any volume-deletion command against a deployment; the project owns no data volume.

## Backup

The platform PostgreSQL already runs `postgresql-backup.timer` nightly: a globals dump plus a custom-format `--create` dump of every database, age-encrypted, uploaded to MinIO bucket `backups` under `minipc/postgres/backups`, with a remote restore drill and a seven-snapshot retention. The `mmath` database is covered automatically once it exists; confirm on the platform dashboard (`postgresql-platform`) that the latest backup age is fresh after the first deployment.

An ad-hoc dump uses the server's own `pg_dump` (client major version must match PostgreSQL 18):

```bash
pg_dump --no-owner --no-acl -U mmath -d mmath -f mmath-$(date +%Y%m%dT%H%M%SZ).sql
```

Store dumps outside the application host with the same care as the database credentials: they contain account emails and password hashes.

## Restore drill (synthetic, separate database)

Restore into a fresh database and compare state before trusting a backup. `scripts/backup_drill.py` does this against a PostgreSQL container: it dumps the source, restores into a new database on the same server, compares account ids, attempt count and the current problem of every active session, and drops the restore database unless `--keep` is given. It refuses to reuse an existing database name.

```bash
uv run --project backend python scripts/backup_drill.py --container mmath-t1-test-postgres-test-1 --user mmath_test --source mmath_t1_test --restore mmath_restore_drill
```

Run the drill on a copy or on the disposable test database, never against the production database name as the restore target.

## Restore for real

1. Stop the API (`docker compose ... stop api web`) so no writes race the restore.
2. Create a new empty database and restore the dump into it with `psql -v ON_ERROR_STOP=1`.
3. Compare the restored database with the expected state (the drill's three checks are the minimum).
4. Point `MMATH_DATABASE_URL` at the restored database, run `docker compose ... up -d --wait`; the migrate job brings the schema to the current revision if the dump predates it.
5. Sign in and resume an unfinished session to confirm the position survived.
