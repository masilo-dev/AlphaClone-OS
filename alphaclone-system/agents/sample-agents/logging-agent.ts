/**
 * AlphaClone System OS - Logging Agent Sample
 * Purpose: Demonstrate a baseline agent that registers with the orchestrator and exposes log ingestion.
 * Author: AlphaClone Systems Core Team
 * License: MIT
 * TODO: Replace in-memory buffers with durable storage and integrate structured log routing.
 */

import Fastify, { type FastifyRequest } from 'fastify';
import axios from 'axios';

type RegistrationPayload = {
  id: string;
  status: 'running' | 'stopped';
};

const agentId = process.env.AGENT_ID ?? 'logging-agent';
const orchestratorUrl = process.env.ORCHESTRATOR_URL ?? 'http://localhost:7070';
const orchestratorToken = process.env.ORCHESTRATOR_TOKEN ?? 'set-me-with-github-secrets';

async function register(status: RegistrationPayload['status']): Promise<void> {
  await axios.post(
    `${orchestratorUrl}/agents/${agentId}/${status === 'running' ? 'start' : 'stop'}`,
    {},
    {
      headers: {
        'x-orchestrator-token': orchestratorToken,
      },
    }
  );
}

async function main(): Promise<void> {
  const app = Fastify({ logger: true });

  app.post('/logs', async (request: FastifyRequest) => {
    app.log.info({ body: request.body }, 'received log payload');
    return { status: 'accepted' };
  });

  await register('running');

  const port = Number.parseInt(process.env.AGENT_PORT ?? '8081', 10);
  await app.listen({ port, host: '0.0.0.0' });

  process.on('SIGINT', async () => {
    app.log.info('shutdown requested');
    await register('stopped');
    await app.close();
    process.exit(0);
  });
}

void main().catch((error) => {
  // eslint-disable-next-line no-console
  console.error('Logging agent failed', error);
  process.exit(1);
});
