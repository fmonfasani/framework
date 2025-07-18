# Guía de Instalación

Esta guía describe los pasos básicos para instalar **Genesis Engine** en tu entorno local.

1. Asegúrate de tener Python 3.9+ y Node.js 18+ instalados.
2. Clona los repositorios principales y navega al directorio del core:
   ```bash
   git clone https://github.com/genesis-engine/genesis-core.git
   git clone https://github.com/genesis-engine/genesis-cli.git
   git clone https://github.com/genesis-engine/genesis-templates.git
   cd genesis-core
   ```
3. Instala las dependencias principales:
   ```bash
   pip install -e .
   pip install -e ../genesis-cli
   pip install -e ../genesis-templates
   ```
4. Comprueba la instalación ejecutando:
   ```bash
   genesis --version
   genesis doctor
   ```

Para un entorno de contribución consulta `CONTRIBUTING.md`.
