'use strict';

const path = require('path');
const { parseMarkdownFile, parseAllMemoryFiles } = require('../../../markdown-importer');
const { upsertByTitle } = require('../../../memory-store');

const tools = {
  import_markdown: {
    name: 'import_markdown',
    description: 'Parse a Markdown file and import its sections as individual memories with embeddings.',
    inputSchema: {
      type: 'object',
      properties: {
        file_path: { type: 'string', description: 'Absolute path to the Markdown file' },
        memory_type: { type: 'string', description: 'Default memory type for imported items' },
        source_label: { type: 'string', description: 'Source label (e.g. "import")' },
      },
      required: ['file_path'],
    },
    handler: async (args) => {
      const items = parseMarkdownFile(args.file_path);
      const results = { imported: 0, skipped: 0, errors: [] };

      for (const item of items) {
        try {
          const memory = {
            ...item,
            memory_type: item.memory_type || args.memory_type || 'insight',
            source: args.source_label || 'import',
            source_file: args.file_path,
          };
          const result = await upsertByTitle(memory);
          if (result.is_new) {
            results.imported++;
          } else {
            results.skipped++;
          }
        } catch (err) {
          results.errors.push({ title: item.title, error: err.message });
        }
      }

      return { content: [{ type: 'text', text: JSON.stringify(results) }] };
    },
  },

  sync_from_markdown: {
    name: 'sync_from_markdown',
    description: 'Re-sync all standard memory Markdown files (insights.md, progresso.md, roadmaps/) into pgvector.',
    inputSchema: {
      type: 'object',
      properties: {
        project_root: { type: 'string', description: 'Project root path (default: auto-detect)' },
      },
    },
    handler: async (args) => {
      const projectRoot = args.project_root || process.env.PROJECT_ROOT || process.cwd();
      const memoriaDir = path.join(projectRoot, 'memoria');
      const allItems = parseAllMemoryFiles(memoriaDir);
      const results = { imported: 0, updated: 0, errors: [] };

      for (const item of allItems) {
        try {
          const result = await upsertByTitle(item);
          if (result.is_new) {
            results.imported++;
          } else {
            results.updated++;
          }
        } catch (err) {
          results.errors.push({ title: item.title, error: err.message });
        }
      }

      return { content: [{ type: 'text', text: JSON.stringify(results) }] };
    },
  },
};

module.exports = tools;
