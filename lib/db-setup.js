'use strict';

/**
 * Database setup for full module
 *
 * Creates the database and runs migrations.
 */

const path = require('path');

/**
 * Setup PostgreSQL database for memory system
 * @param {object} config - Installation config
 * @returns {Promise<{ok: boolean, dbName?: string, pgvectorVersion?: string, tables?: string[], error?: string}>}
 */
async function setupDatabase(config) {
  try {
    // Dynamic require pg from target's memory/node_modules
    const pgPath = path.join(config.targetDir, 'memory', 'node_modules', 'pg');
    const { Pool } = require(pgPath);
    const fs = require('fs');

    const migrationsDir = path.join(config.targetDir, 'memory', 'migrations');
    const dbName = config.dbName || 'claude_memory';

    // Step 1: Connect to postgres db and create target database
    const adminPool = new Pool({
      host: config.dbHost || 'localhost',
      port: parseInt(config.dbPort || '5432', 10),
      user: config.dbUser || 'postgres',
      password: config.dbPassword || '',
      database: 'postgres',
      connectionTimeoutMillis: 5000,
    });

    try {
      const exists = await adminPool.query(
        'SELECT 1 FROM pg_database WHERE datname = $1',
        [dbName],
      );

      if (exists.rows.length === 0) {
        await adminPool.query(`CREATE DATABASE "${dbName}"`);
      }
    } finally {
      await adminPool.end();
    }

    // Step 2: Connect to target database and run migrations
    const appPool = new Pool({
      host: config.dbHost || 'localhost',
      port: parseInt(config.dbPort || '5432', 10),
      user: config.dbUser || 'postgres',
      password: config.dbPassword || '',
      database: dbName,
      connectionTimeoutMillis: 5000,
    });

    try {
      // Run migrations in order
      if (fs.existsSync(migrationsDir)) {
        const files = fs.readdirSync(migrationsDir)
          .filter(f => f.endsWith('.sql'))
          .sort();

        for (const file of files) {
          const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf-8');
          try {
            await appPool.query(sql);
          } catch (err) {
            // Ignore "already exists" errors (idempotent)
            if (!err.message.includes('already exists') && !err.message.includes('duplicate')) {
              throw err;
            }
          }
        }
      }

      // Verify
      const tables = await appPool.query(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename",
      );

      const extensions = await appPool.query(
        "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'",
      );

      const pgvectorVersion = extensions.rows.length > 0
        ? extensions.rows[0].extversion
        : 'not installed';

      return {
        ok: true,
        dbName,
        pgvectorVersion,
        tables: tables.rows.map(r => r.tablename),
      };
    } finally {
      await appPool.end();
    }
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

module.exports = { setupDatabase };
