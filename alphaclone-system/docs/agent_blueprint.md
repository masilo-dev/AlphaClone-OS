<!--
Purpose: Teach contributors how to build AlphaClone System OS agents from schema to deployment.
Author: AlphaClone Systems Core Team
License: MIT
TODO: Add real manifest samples and automate schema validation walkthrough.
-->

# AlphaClone System OS Agent Blueprint

This guide walks through crafting an agent that integrates cleanly with the AlphaClone System OS orchestrator and adheres to security and lifecycle expectations.

## 1. Define the Manifest

Agents MUST ship a manifest that validates against `agents/agent-specs/ai-agent.schema.json`.

```json
{
  "id": "logging-agent",
  "name": "Logging Agent",
  "version": "v0.1.0",
  "capabilities": ["logs:ingest"],
  "resources": { "cpu": "250m", "memory": "256Mi" },
  "api_endpoints": ["http://localhost:8081/logs"],
  "permissions": ["bus:publish", "storage:append"]
}
```

## 2. Implement Required Endpoints

- **Health** – `/healthz` returning readiness.
- **Lifecycle Hooks** – Expose HTTP routes or message-bus handlers to respond to orchestrator commands.
- **Primary Capability API** – Provide the service interface described in `capabilities`.

## 3. Register with the Orchestrator

- Authenticate with the orchestrator using the `x-orchestrator-token` header.
- Call `POST /agents/:id/start` during boot, and `POST /agents/:id/stop` prior to shutdown.
- Maintain heartbeat messaging for long-running agents (future requirement).

## 4. Security Considerations

- Respect the principle of least privilege: request only capabilities you actively use.
- Store secrets in environment variables sourced from secure stores.
- Emit structured logs to allow downstream security agents to flag anomalies.

## 5. Recommended Patterns

- Use dependency injection for external services to ease sandboxing.
- Implement exponential backoff when communicating with the orchestrator.
- Provide tracing spans around critical operations to integrate with platform observability.

## 6. Example Agents

- **Logging Agent** – Ships in `agents/sample-agents/logging-agent.ts` and demonstrates lifecycle handshakes.
- **Indexer Agent** *(planned)* – Will build search indices from kernel telemetry.
- **Code Assistant Agent** *(planned)* – Leverages LLM tooling to assist developers via the runtime UI.

## 7. Validation Workflow

1. Run `pnpm lint` to perform static type checks.
2. Execute agent unit tests (future harness) and integration tests via the orchestrator sandbox.
3. Submit manifests for automated schema validation in CI.

Agents that respect this blueprint can ship alongside the kernel and runtime with minimal friction.
