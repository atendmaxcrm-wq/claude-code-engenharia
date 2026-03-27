#!/usr/bin/env node
'use strict';

/**
 * MCP Memory Server - Claude Code Memory RAG System
 *
 * Provides 12 tools for memory CRUD, semantic search,
 * session management, markdown import, and analytics.
 *
 * Transport: stdio (standard MCP protocol)
 * Database: PostgreSQL 16 + pgvector
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

const { healthCheck } = require('../../db');

// Load all tool modules
const storeTools = require('./tools/store');
const searchTools = require('./tools/search');
const sessionTools = require('./tools/session');
const importTools = require('./tools/import');
const statsTools = require('./tools/stats');

// Merge all tools into a single registry
const TOOLS = {
  ...storeTools,
  ...searchTools,
  ...sessionTools,
  ...importTools,
  ...statsTools,
};

async function main() {
  // Check database connectivity
  const health = await healthCheck();
  if (!health.connected) {
    process.stderr.write(`[mcp-memory] WARNING: Database not connected: ${health.error}\n`);
  } else {
    process.stderr.write(`[mcp-memory] Connected to PostgreSQL (pgvector ${health.pgvector})\n`);
  }

  const server = new Server(
    { name: 'claude-code-memory', version: '1.0.0' },
    { capabilities: { tools: {} } },
  );

  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    const toolList = Object.values(TOOLS).map((tool) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema,
    }));
    return { tools: toolList };
  });

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    const tool = TOOLS[name];
    if (!tool) {
      return {
        content: [{ type: 'text', text: JSON.stringify({ error: `Unknown tool: ${name}` }) }],
        isError: true,
      };
    }

    try {
      return await tool.handler(args || {});
    } catch (err) {
      process.stderr.write(`[mcp-memory] Tool ${name} error: ${err.message}\n`);
      return {
        content: [{ type: 'text', text: JSON.stringify({ error: err.message }) }],
        isError: true,
      };
    }
  });

  // Start server on stdio
  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stderr.write('[mcp-memory] Claude Code Memory MCP server started on stdio\n');
}

main().catch((err) => {
  process.stderr.write(`[mcp-memory] FATAL: ${err.message}\n`);
  process.exit(1);
});
