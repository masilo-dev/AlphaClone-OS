/**
 * AlphaClone System OS - Agent Orchestrator Entry
 * Purpose: Launch the orchestrator service that manages AI agents following manifest schemas.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Harden authentication, add real message bus integration, and external observability hooks.
 */

import Fastify, { FastifyInstance } from 'fastify';
import fastifyEnv from '@fastify/env';
import fastifyCors from '@fastify/cors';
import { promises as fs } from 'fs';
import { join } from 'path';

type AgentManifest = {
  id: string;
  name: string;
  version: string;
  capabilities: string[];
  resources?: Record<string, unknown>;
  api_endpoints?: string[];
  permissions?: string[];
};

type AgentRecord = {
  manifest: AgentManifest;
  status: 'stopped' | 'running' | 'error';
};

type OrchestratorConfig = {
  AGENT_SPEC_PATH: string;
  ORCHESTRATOR_PORT: string;
  ORCHESTRATOR_HOST: string;
  ORCHESTRATOR_API_TOKEN: string;
};

declare module 'fastify' {
  interface FastifyInstance {
    config: OrchestratorConfig;
  }
}

const orchestratorConfigSchema = {
  type: 'object',
  properties: {
    AGENT_SPEC_PATH: {
      type: 'string',
      default: join(process.cwd(), '..', 'agent-specs'),
    },
    ORCHESTRATOR_PORT: {
      type: 'string',
      default: '7070',
    },
    ORCHESTRATOR_HOST: {
      type: 'string',
      default: '0.0.0.0',
    },
    ORCHESTRATOR_API_TOKEN: {
      type: 'string',
      default: 'set-me-with-github-secrets',
    },
  },
  required: ['ORCHESTRATOR_API_TOKEN'],
} as const;

async function loadAgentManifests(specDirectory: string): Promise<AgentRecord[]> {
  const entries = await fs.readdir(specDirectory, { withFileTypes: true }).catch(() => []);
  const manifests: AgentRecord[] = [];

  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.endsWith('.json')) {
      continue;
    }

    const manifestPath = join(specDirectory, entry.name);
    const data = await fs.readFile(manifestPath, 'utf-8');
    const manifest = JSON.parse(data) as AgentManifest;
    manifests.push({ manifest, status: 'stopped' });
  }

  return manifests;
}

async function registerRoutes(app: FastifyInstance, agents: Map<string, AgentRecord>): Promise<void> {
  app.addHook('preHandler', async (request, reply) => {
    const token = request.headers['x-orchestrator-token'];
    if (token !== app.config.ORCHESTRATOR_API_TOKEN) {
      reply.code(401);
      throw new Error('Unauthorized orchestrator access');
    }
  });

  app.get('/agents', async () => Array.from(agents.values()));

  app.post('/agents/:id/start', async (request, reply) => {
    const { id } = request.params as { id: string };
    const agent = agents.get(id);
    if (!agent) {
      reply.code(404);
      return { error: 'Agent not found' };
    }

    agent.status = 'running';
    return { status: 'ok' };
  });

  app.post('/agents/:id/stop', async (request, reply) => {
    const { id } = request.params as { id: string };
    const agent = agents.get(id);
    if (!agent) {
      reply.code(404);
      return { error: 'Agent not found' };
    }

    agent.status = 'stopped';
    return { status: 'ok' };
  });

  app.get('/healthz', async () => ({ status: 'ready' }));
}

async function bootstrap(): Promise<void> {
  const app = Fastify({ logger: true });

  await app.register(fastifyEnv, {
    schema: orchestratorConfigSchema,
    dotenv: true,
    data: process.env,
  });

  await app.after();
  await app.register(fastifyCors, { origin: false });

  const specs = await loadAgentManifests(app.config.AGENT_SPEC_PATH);
  const agentMap = new Map(specs.map((record) => [record.manifest.id, record]));

  await registerRoutes(app, agentMap);

  const port = Number.parseInt(app.config.ORCHESTRATOR_PORT, 10);
  await app.listen({ port, host: app.config.ORCHESTRATOR_HOST });

  app.log.info({ port }, 'Orchestrator API listening');
}

void bootstrap().catch((error) => {
  // eslint-disable-next-line no-console
  console.error('Failed to bootstrap orchestrator', error);
  process.exit(1);
});
