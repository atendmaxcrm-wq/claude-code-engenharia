'use strict';

/**
 * Pre-flight and post-install validators
 */

const { execSync } = require('child_process');

/**
 * Run pre-flight checks before installation
 * @returns {Promise<{ok: boolean, nodeVersion?: string, jqAvailable?: boolean, error?: string}>}
 */
async function preFlightChecks() {
  // Check Node version
  const nodeVersion = process.version;
  const major = parseInt(nodeVersion.slice(1).split('.')[0], 10);
  if (major < 18) {
    return { ok: false, error: `Node.js 18+ required (found ${nodeVersion})` };
  }

  // Check jq (optional but recommended)
  let jqAvailable = false;
  try {
    execSync('jq --version', { stdio: 'ignore' });
    jqAvailable = true;
  } catch {
    // jq not found - optional
  }

  return { ok: true, nodeVersion, jqAvailable };
}

/**
 * Validate PostgreSQL connection (for full module)
 * @param {object} config - Database configuration
 * @returns {Promise<{ok: boolean, error?: string}>}
 */
async function validatePostgres(config) {
  try {
    const { Pool } = require('pg');
    const pool = new Pool({
      host: config.dbHost || 'localhost',
      port: parseInt(config.dbPort || '5432', 10),
      user: config.dbUser || 'postgres',
      password: config.dbPassword || '',
      database: 'postgres',
      connectionTimeoutMillis: 5000,
    });

    const result = await pool.query('SELECT version()');
    await pool.end();

    return { ok: true, version: result.rows[0].version };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

module.exports = { preFlightChecks, validatePostgres };
