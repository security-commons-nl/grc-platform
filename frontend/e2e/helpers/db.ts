import { execFileSync } from 'node:child_process';

// POSTGRES_USER/DB komen uit `.env` (lokaal vaak `postgres`/`ims`; in CI `ims`/`ims`).
// Lees ze uit env zodat de helper op beide draait zonder lokale aanpassing.
const PG_USER = process.env.POSTGRES_USER ?? 'postgres';
const PG_DB = process.env.POSTGRES_DB ?? 'ims';

const PSQL_ARGS = [
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
  '-F',
  '|',
];

function runPsql(sql: string): string {
  const out = execFileSync('docker', [...PSQL_ARGS, '-c', sql], {
    encoding: 'utf-8',
    cwd: process.env.COMPOSE_DIR ?? `${process.cwd()}/..`,
  });
  return out.trim();
}

export function queryScalar<T = string>(sql: string): T | null {
  const out = runPsql(sql);
  if (!out) return null;
  return out as unknown as T;
}

export function queryRows(sql: string): string[][] {
  const out = runPsql(sql);
  if (!out) return [];
  return out.split('\n').map((line) => line.split('|'));
}

export function queryCount(sql: string): number {
  const out = runPsql(sql);
  return parseInt(out, 10) || 0;
}

export function countRows(table: string, where = '1=1'): number {
  return queryCount(`SELECT COUNT(*) FROM ${table} WHERE ${where};`);
}

export function rowExists(table: string, where: string): boolean {
  return countRows(table, where) > 0;
}
