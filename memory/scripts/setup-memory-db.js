#!/usr/bin/env node
'use strict';

/**
 * Setup Memory Database
 *
 * Creates the claude_memory database and runs all migrations.
 * Idempotent: safe to run multiple times.
 *
 * Usage: node setup-memory-db.js
 */

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');

const MIGRATIONS_DIR = path.join(__dirname, '..', 'migrations');

async function main() {
  const adminPool = new Pool({
    host: process.env.MEMORY_DB_HOST || 'localhost',
    port: parseInt(process.env.MEMORY_DB_PORT || '5432', 10),
    user: process.env.MEMORY_DB_USER || 'postgres',
    password: process.env.MEMORY_DB_PASSWORD || '',
    database: 'postgres',
  });

  const dbName = process.env.MEMORY_DB_NAME || 'claude_memory';

  try {
    // Check if database exists
    const exists = await adminPool.query(
      'SELECT 1 FROM pg_database WHERE datname = $1',
      [dbName],
    );

    if (exists.rows.length === 0) {
      console.log(`Creating database ${dbName}...`);
      await adminPool.query(`CREATE DATABASE ${dbName}`);
      console.log(`Database ${dbName} created.`);
    } else {
      console.log(`Database ${dbName} already exists.`);
    }
  } finally {
    await adminPool.end();
  }

  // Connect to the new database and run migrations
  const appPool = new Pool({
    host: process.env.MEMORY_DB_HOST || 'localhost',
    port: parseInt(process.env.MEMORY_DB_PORT || '5432', 10),
    user: process.env.MEMORY_DB_USER || 'postgres',
    password: process.env.MEMORY_DB_PASSWORD || '',
    database: dbName,
  });

  try {
    const files = fs.readdirSync(MIGRATIONS_DIR)
      .filter((f) => f.endsWith('.sql'))
      .sort();

    console.log(`Running ${files.length} migrations...`);

    for (const file of files) {
      const sql = fs.readFileSync(path.join(MIGRATIONS_DIR, file), 'utf-8');
      console.log(`  Running ${file}...`);
      await appPool.query(sql);
      console.log(`  OK: ${file}`);
    }

    console.log('All migrations complete.');

    // Verify
    const tables = await appPool.query(
      "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename",
    );
    console.log('\nTables created:');
    tables.rows.forEach((r) => console.log(`  - ${r.tablename}`));

    const extensions = await appPool.query(
      "SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp')",
    );
    console.log('\nExtensions:');
    extensions.rows.forEach((r) => console.log(`  - ${r.extname} v${r.extversion}`));
  } finally {
    await appPool.end();
  }
}

main().catch((err) => {
  console.error('Setup failed:', err.message);
  process.exit(1);
});
