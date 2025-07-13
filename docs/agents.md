# Arquitectura de Agentes

Genesis Engine se compone de varios agentes especializados que colaboran para generar un proyecto completo.

- **ArchitectAgent**: diseña la arquitectura y define las entidades.
- **BackendAgent**: produce el código del backend y la base de datos.
- **FrontendAgent**: genera la interfaz de usuario.
- **DevOpsAgent**: configura contenedores y pipelines de CI/CD.
- **DeployAgent**: orquesta el despliegue de la aplicación.

Cada agente se comunica mediante el protocolo MCP descrito en `docs/mcp-protocol.md`.
