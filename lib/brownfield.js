'use strict';

/**
 * Brownfield detection - handles existing .claude/ installations
 *
 * Detects existing files and decides what to skip/merge.
 */

const fs = require('fs');
const path = require('path');

/**
 * Detect existing .claude/ installation
 * @param {string} targetDir - Project root directory
 * @param {object} opts - {force}
 * @returns {Promise<{hasExisting: boolean, existingFiles: string[]}>}
 */
async function handleBrownfield(targetDir, opts = {}) {
  const existingFiles = [];

  // Check .claude/ directory
  const claudeDir = path.join(targetDir, '.claude');
  if (fs.existsSync(claudeDir)) {
    scanDir(claudeDir, targetDir, existingFiles);
  }

  // Check memoria/ directory
  const memoriaDir = path.join(targetDir, 'memoria');
  if (fs.existsSync(memoriaDir)) {
    scanDir(memoriaDir, targetDir, existingFiles);
  }

  // Check memory/ directory
  const memoryDir = path.join(targetDir, 'memory');
  if (fs.existsSync(memoryDir)) {
    scanDir(memoryDir, targetDir, existingFiles);
  }

  // Check root files
  const rootFiles = ['CLAUDE.md', '.mcp.json'];
  for (const f of rootFiles) {
    if (fs.existsSync(path.join(targetDir, f))) {
      existingFiles.push(f);
    }
  }

  return {
    hasExisting: existingFiles.length > 0,
    existingFiles,
  };
}

/**
 * Recursively scan directory for files
 * @param {string} dir - Directory to scan
 * @param {string} baseDir - Base directory for relative paths
 * @param {string[]} results - Array to push results to
 */
function scanDir(dir, baseDir, results) {
  if (!fs.existsSync(dir)) return;

  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'node_modules') continue;
      scanDir(fullPath, baseDir, results);
    } else {
      results.push(path.relative(baseDir, fullPath));
    }
  }
}

/**
 * Merge settings.json files (existing + new)
 * Preserves existing hooks, adds new ones
 * @param {string} existingPath - Path to existing settings.json
 * @param {object} newSettings - New settings to merge
 * @returns {object} Merged settings
 */
function mergeSettings(existingPath, newSettings) {
  try {
    const existing = JSON.parse(fs.readFileSync(existingPath, 'utf-8'));

    // Merge hooks
    if (existing.hooks && newSettings.hooks) {
      for (const [event, hookConfigs] of Object.entries(newSettings.hooks)) {
        if (!existing.hooks[event]) {
          existing.hooks[event] = hookConfigs;
        }
        // Don't overwrite existing hook configs for the same event
      }
    } else if (newSettings.hooks) {
      existing.hooks = newSettings.hooks;
    }

    return existing;
  } catch {
    return newSettings;
  }
}

module.exports = { handleBrownfield, mergeSettings };
