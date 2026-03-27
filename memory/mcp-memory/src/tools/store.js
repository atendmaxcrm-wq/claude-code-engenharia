'use strict';

const { createMemory, updateMemory, deactivateMemory } = require('../../../memory-store');

const MEMORY_TYPES = ['decision', 'pattern', 'gotcha', 'insight', 'session_note', 'progress', 'roadmap', 'knowledge'];
const IMPORTANCE_LEVELS = ['critical', 'high', 'normal', 'low'];

const tools = {
  store_memory: {
    name: 'store_memory',
    description: 'Store a new memory with automatic embedding generation. Use for decisions, patterns, gotchas, insights, and session notes.',
    inputSchema: {
      type: 'object',
      properties: {
        memory_type: { type: 'string', enum: MEMORY_TYPES, description: 'Type of memory' },
        title: { type: 'string', description: 'Concise title for the memory' },
        content: { type: 'string', description: 'Full content/description' },
        source: { type: 'string', description: 'Origin: manual, session, import, auto-gotcha', default: 'manual' },
        source_file: { type: 'string', description: 'Original file path if imported from markdown' },
        agent_id: { type: 'string', description: 'Agent that created this memory (dev, qa, architect, etc.)' },
        importance: { type: 'string', enum: IMPORTANCE_LEVELS, default: 'normal' },
        tags: { type: 'array', items: { type: 'string' }, description: 'Searchable tags' },
        metadata: { type: 'object', description: 'Additional structured data' },
        expires_at: { type: 'string', description: 'ISO timestamp for volatile memories (null = permanent)' },
      },
      required: ['memory_type', 'title', 'content'],
    },
    handler: async (args) => {
      const result = await createMemory(args);
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },

  update_memory: {
    name: 'update_memory',
    description: 'Update an existing memory by UUID. Re-generates embedding if title or content changes.',
    inputSchema: {
      type: 'object',
      properties: {
        id: { type: 'string', description: 'Memory UUID' },
        title: { type: 'string' },
        content: { type: 'string' },
        importance: { type: 'string', enum: IMPORTANCE_LEVELS },
        tags: { type: 'array', items: { type: 'string' } },
        metadata: { type: 'object' },
        is_active: { type: 'boolean' },
        expires_at: { type: 'string' },
      },
      required: ['id'],
    },
    handler: async (args) => {
      const { id, ...updates } = args;
      const result = await updateMemory(id, updates);
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },

  deactivate_memory: {
    name: 'deactivate_memory',
    description: 'Soft-delete a memory (sets is_active=false). The vector is preserved for audit.',
    inputSchema: {
      type: 'object',
      properties: {
        id: { type: 'string', description: 'Memory UUID to deactivate' },
      },
      required: ['id'],
    },
    handler: async (args) => {
      const result = await deactivateMemory(args.id);
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },
};

module.exports = tools;
