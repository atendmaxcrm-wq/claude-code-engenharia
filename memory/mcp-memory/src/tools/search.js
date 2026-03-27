'use strict';

const { searchSimilar, searchFullText } = require('../../../search');
const { getById } = require('../../../memory-store');

const MEMORY_TYPES = ['decision', 'pattern', 'gotcha', 'insight', 'session_note', 'progress', 'roadmap', 'knowledge'];

const tools = {
  search_memories: {
    name: 'search_memories',
    description: 'Semantic similarity search across memories using vector embeddings. Returns ranked results with similarity scores.',
    inputSchema: {
      type: 'object',
      properties: {
        query_text: { type: 'string', description: 'Natural language search query' },
        match_count: { type: 'number', default: 10, description: 'Max results to return' },
        similarity_threshold: { type: 'number', default: 0.3, description: 'Min similarity (0-1)' },
        memory_type: { type: 'string', enum: MEMORY_TYPES, description: 'Filter by type' },
        agent_id: { type: 'string', description: 'Filter by agent' },
        tags: { type: 'array', items: { type: 'string' }, description: 'Filter by tags' },
      },
      required: ['query_text'],
    },
    handler: async (args) => {
      const result = await searchSimilar(args.query_text, {
        match_count: args.match_count,
        similarity_threshold: args.similarity_threshold,
        memory_type: args.memory_type || null,
        agent_id: args.agent_id || null,
        query_source: 'mcp-tool',
      });
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },

  search_memories_by_text: {
    name: 'search_memories_by_text',
    description: 'Full-text search using PostgreSQL tsvector (Portuguese dictionary). For keyword-based lookups.',
    inputSchema: {
      type: 'object',
      properties: {
        query_text: { type: 'string', description: 'Keywords to search' },
        match_count: { type: 'number', default: 10 },
        memory_type: { type: 'string', enum: MEMORY_TYPES },
        agent_id: { type: 'string' },
      },
      required: ['query_text'],
    },
    handler: async (args) => {
      const result = await searchFullText(args.query_text, {
        match_count: args.match_count,
        memory_type: args.memory_type || null,
        agent_id: args.agent_id || null,
      });
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },

  get_memory_by_id: {
    name: 'get_memory_by_id',
    description: 'Retrieve a specific memory by its UUID.',
    inputSchema: {
      type: 'object',
      properties: {
        id: { type: 'string', description: 'Memory UUID' },
      },
      required: ['id'],
    },
    handler: async (args) => {
      const result = await getById(args.id);
      if (!result) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: 'Memory not found' }) }], isError: true };
      }
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },
};

module.exports = tools;
