'use strict';

const {
  startSession,
  endSession,
  getCurrentSession,
  getNextSessionNumber,
} = require('../../../session-store');

const tools = {
  start_session: {
    name: 'start_session',
    description: 'Start a new memory session. Auto-assigns the next session number.',
    inputSchema: {
      type: 'object',
      properties: {
        agent_id: { type: 'string', description: 'Agent starting the session' },
        metadata: { type: 'object', description: 'Additional session metadata' },
      },
    },
    handler: async (args) => {
      const session_number = await getNextSessionNumber();
      const result = await startSession({
        session_number,
        agent_id: args.agent_id || null,
        metadata: args.metadata || {},
      });
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },

  end_session: {
    name: 'end_session',
    description: 'End the current session with a summary of work done and next steps.',
    inputSchema: {
      type: 'object',
      properties: {
        session_id: { type: 'string', description: 'Session UUID to close' },
        summary: { type: 'string', description: 'Brief summary of the session' },
        work_done: { type: 'array', items: { type: 'string' }, description: 'List of completed tasks' },
        next_steps: { type: 'array', items: { type: 'string' }, description: 'Next actions for the next session' },
        files_changed: { type: 'array', items: { type: 'string' }, description: 'Files created/modified' },
      },
      required: ['session_id', 'summary'],
    },
    handler: async (args) => {
      const { session_id, ...data } = args;
      const result = await endSession(session_id, data);
      if (!result) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: 'Session not found' }) }], isError: true };
      }
      return { content: [{ type: 'text', text: JSON.stringify(result) }] };
    },
  },

  get_current_session: {
    name: 'get_current_session',
    description: 'Get the most recent open session (where ended_at IS NULL).',
    inputSchema: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      const result = await getCurrentSession();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result || { message: 'No open session found' }),
        }],
      };
    },
  },
};

module.exports = tools;
