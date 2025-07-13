<!-- ECOSYSTEM_DOCTRINE: genesis-engine -->
# 🧠 Ecosystem Doctrine — Genesis Engine (Framework Modular)

Este repositorio forma parte del ecosistema **Fast-Engine / Genesis Engine / MCPturbo**.  
Su función es ser el **framework principal de generación de software basado en agentes de IA**.

## 🧠 Rol Declarado

- Tipo: **Framework modular**
- Nombre: `genesis-engine`
- Dominio: Desarrollo de software full-stack
- Función: Ejecutar flujos de trabajo mediante agentes IA especializados

## 🔒 Mandamientos del Proyecto

### 1. **No reimplementarás lo que ya hace MCPturbo**
Genesis Engine debe usar exclusivamente las primitivas de orquestación de MCPturbo.  
No debe definir su propio protocolo, lógica de reintentos ni workflows paralelos.

### 2. **No hablarás directamente con el usuario final**
Genesis Engine **no tiene CLI propia ni interfaz gráfica**.  
Recibe instrucciones del exterior (como `fast-engine`) y ejecuta.

### 3. **Todo lo harás a través de agentes**
Ningún módulo debe hacer lógica de negocio directa.  
Todo debe delegarse a agentes como `BackendAgent`, `DevOpsAgent`, etc.

### 4. **Nunca generarás prompts directamente**
La generación de prompts debe realizarse dentro de los agentes, no desde el orquestador ni servicios globales.

### 5. **No generarás código estático ni hardcodeado**
Todo el output debe renderizarse usando templates declarativos (Jinja2, etc.).

### 6. **Cada agente tendrá una única responsabilidad**
Agentes deben ser pequeños, independientes y reemplazables.  
Si un agente crece demasiado, se divide.

### 7. **Nunca importarás código de Fast-Engine**
Genesis Engine debe ignorar por completo la CLI de consumo.  
Es responsabilidad de `fast-engine` iniciar flujos, pero nunca compartir lógica.

---

## 🧩 Interfaz esperada por consumidores

Los consumidores externos (como `fast-engine`) deben usar:

- `genesis_main.run(project_name, template_name)`
- `GenesisOrchestrator.execute_workflow(name, initial_data)`
- `ProjectManager.load/save_plan()`
- `AgentRegistry.register(agent)`

---

## 📦 Separación de capas (importante)

| Capa           | Puede importar desde | No puede importar desde |
|----------------|----------------------|--------------------------|
| genesis-engine | mcpturbo             | fast-engine              |
| fast-engine    | genesis-engine       | mcpturbo directamente    |

---

## 🤖 AI Agents, please read:

Este repositorio sigue una arquitectura basada en agentes y workflows.

Si estás revisando código, escribiendo tests o generando lógica nueva:
- ❌ No implementes lógica de negocio fuera de los agentes.
- ❌ No crees nuevas estructuras de orquestación paralelas al orchestrador de MCPturbo.
- ✅ Usá los agentes para cualquier decisión basada en LLMs o generación de código.

Toda excepción debe documentarse en `DOCTRINE_CHANGE_REQUEST.md` y pasar por revisión técnica.

---

## 📎 Referencias

- MCPturbo Core → [https://github.com/fmonfasani/mcpturbo](https://github.com/your-org/mcpturbo)
- Fast-Engine CLI → [https://github.com/your-org/fast-engine](https://github.com/your-org/fast-engine)
