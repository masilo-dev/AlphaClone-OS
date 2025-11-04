# AlphaClone-OS Agent Subsystem

This directory contains the intelligent agent subsystem for AlphaClone-OS. The agents provide advanced capabilities like system monitoring, security analysis, and AI-powered operations.

## Integration with Kernel

The agent subsystem integrates with the existing kernel simulator:
- Uses VFS for persistent storage
- Managed by process scheduler
- IPC through kernel primitives

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the system:
```bash
cp agent_runtime/config.example.json /etc/alphaclone/agent_config.json
# Edit config as needed
```

3. Start the agent runtime:
```bash
make run
```

4. Check agent status:
```bash
make status
```

## Development Mode Demo

The security_agent and aiops_agent demonstrate basic interaction:

1. Start agents:
```bash
python3 agent_launcher.py start
```

2. Watch logs:
```bash
tail -f /var/log/alphaclone/agents.log
```

3. Trigger a demo interaction:
```python
# Using Python REPL
from agent_runtime.runtime import AgentRuntime
runtime = AgentRuntime("/etc/alphaclone/agent_config.json")
runtime.send_message("aiops_agent", "security_agent", {
    "type": "check_process",
    "pid": 1234
})
```

## Architecture

See full documentation in `/docs/agent_integration.md`

Key components:
- agent_runtime: Core services and IPC
- agents/*: Individual agent implementations
- Persistent memory with SQLite backend
- Local AI inference capabilities

## Security Notes

- Agents run in restricted sandboxes
- Memory is encrypted at rest
- Cloud sync disabled by default
- TPM integration available when hardware present

## Contributing

1. Review the architecture docs
2. Install dev dependencies: `pip install -r requirements-dev.txt`
3. Run tests: `make test`
4. Submit PR with new agent or feature

## License

Same as AlphaClone-OS main license