'use strict';

const { query } = require('../../../db');

const tools = {
  memory_stats: {
    name: 'memory_stats',
    description: 'Aggregated statistics about stored memories: counts by type, importance, agent, embedding coverage.',
    inputSchema: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      const [byType, byImportance, byAgent, coverage, total] = await Promise.all([
        query(`SELECT memory_type, COUNT(*) as count FROM memories
               WHERE is_active = true GROUP BY memory_type ORDER BY count DESC`),
        query(`SELECT importance, COUNT(*) as count FROM memories
               WHERE is_active = true GROUP BY importance ORDER BY count DESC`),
        query(`SELECT COALESCE(agent_id, 'global') as agent, COUNT(*) as count FROM memories
               WHERE is_active = true GROUP BY agent_id ORDER BY count DESC`),
        query(`SELECT
                 COUNT(*) as total,
                 COUNT(embedding) as with_embedding,
                 COUNT(*) - COUNT(embedding) as without_embedding
               FROM memories WHERE is_active = true`),
        query('SELECT COUNT(*) as total FROM memories'),
      ]);

      const stats = {
        total_memories: parseInt(total.rows[0].total),
        active_memories: parseInt(coverage.rows[0].total),
        embedding_coverage: {
          with_embedding: parseInt(coverage.rows[0].with_embedding),
          without_embedding: parseInt(coverage.rows[0].without_embedding),
        },
        by_type: byType.rows.map((r) => ({ type: r.memory_type, count: parseInt(r.count) })),
        by_importance: byImportance.rows.map((r) => ({ importance: r.importance, count: parseInt(r.count) })),
        by_agent: byAgent.rows.map((r) => ({ agent: r.agent, count: parseInt(r.count) })),
      };

      return { content: [{ type: 'text', text: JSON.stringify(stats) }] };
    },
  },
};

module.exports = tools;
