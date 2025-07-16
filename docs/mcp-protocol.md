# Protocolo MCP

El *Multi-agent Communication Protocol* (MCP) define el formato de los mensajes y el flujo de interacción entre los agentes de Genesis Engine.

Un mensaje típico incluye:

```json
{
  "sender": "architect_agent",
  "recipient": "backend_agent",
  "action": "generate_backend",
  "params": {
    "schema": "..."
  }
}
```

Los agentes procesan los mensajes de manera asíncrona y devuelven la respuesta correspondiente para continuar el pipeline de generación.

## Ejemplo de uso con GenesisOrchestrator y MCPturbo

```python
import asyncio
from mcpturbo.protocol import TurboProtocol
from genesis_core.orchestrator import GenesisOrchestrator

async def main():
    turbo = TurboProtocol()
    orchestrator = GenesisOrchestrator()
    orchestrator.mcp = turbo
    await orchestrator.create_project({"name": "demo", "template": "saas-basic"})

asyncio.run(main())
```
