# Guía de Migración desde la versión monolítica

A partir de la versión 1.1, Genesis Engine se divide en varios repositorios independientes.
Si aún utilizas el paquete monolítico `genesis-engine`, sigue estos pasos para actualizarte:

1. Desinstala el paquete antiguo:
   ```bash
   pip uninstall genesis-engine
   ```
2. Clona los nuevos repositorios y entra al directorio del core:
   ```bash
   git clone https://github.com/genesis-engine/genesis-core.git
   git clone https://github.com/genesis-engine/genesis-cli.git
   git clone https://github.com/genesis-engine/genesis-templates.git
   cd genesis-core
   ```
3. Instala cada componente de forma editable (o desde PyPI si lo prefieres):
   ```bash
   pip install -e .
   pip install -e ../genesis-cli
   pip install -e ../genesis-templates
   ```
4. Actualiza tus scripts o automatizaciones para importar desde `genesis_core` en lugar de `genesis_engine`.
   El uso básico del CLI no cambia.

Tras la migración podrás seguir ejecutando `genesis` normalmente, pero ahora cada
módulo evoluciona con su propio ciclo de versiones.
