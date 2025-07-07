"""
Template Engine - Motor de plantillas Jinja2 para Genesis Engine

Este módulo es responsable de:
- Cargar y renderizar plantillas Jinja2
- Gestionar templates modulares por tecnología
- Proporcionar funciones helper personalizadas
- Validar sintaxis y variables de templates
- Cache de templates para mejor performance
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

from jinja2 import Environment, FileSystemLoader, Template, TemplateError
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask
from genesis_engine.templates.engine import TemplateEngine


# Instancia global del motor de templates
template_engine = TemplateEngine()


class FrontendAgent(GenesisAgent):
    """Agente Frontend - Generador de interfaz Next.js"""

    def __init__(self):
        super().__init__(
            agent_id="frontend_agent",
            name="FrontendAgent",
            agent_type="frontend",
        )

        # Capacidades básicas
        self.add_capability("nextjs_generation")
        self.add_capability("ui_components")
        self.add_capability("state_management")

        self.register_handler("generate_frontend", self._handle_generate_frontend)

        self.template_engine = TemplateEngine()

    async def initialize(self):
        """Inicialización del agente frontend"""
        self.logger.info("🎨 Inicializando Frontend Agent")

        self.set_metadata("version", "1.0.0")
        self.set_metadata("supported_frameworks", ["nextjs"])

        self.logger.info("✅ Frontend Agent inicializado")

    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica del frontend"""
        task_name = task.name.lower()

        if "generate_frontend" in task_name:
            return await self._generate_complete_frontend(task.params)

        raise ValueError(f"Tarea no reconocida: {task.name}")

    async def _handle_generate_frontend(self, request) -> Dict[str, Any]:
        """Handler para generación de frontend"""
        return await self._generate_complete_frontend(request.params)

    async def _generate_complete_frontend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generar proyecto Next.js básico"""
        self.logger.info("🚀 Generando frontend Next.js")

        schema = params.get("schema", {})
        output_path = Path(params.get("output_path", "./frontend"))
        output_path.mkdir(parents=True, exist_ok=True)

        template_vars = {
            "project_name": schema.get("project_name", "genesis_app"),
            "description": schema.get("description", "Generated with Genesis Engine"),
            "typescript": params.get("typescript", True),
            "styling": params.get("styling", "tailwind"),
            "state_management": params.get("state_management", "redux_toolkit"),
            "ui_components": params.get("ui_components", "shadcn"),
        }

        templates = [
            t for t in self.template_engine.list_templates("frontend/nextjs/*")
            if t.endswith(".j2")
        ]

        generated_files: List[str] = []
        prefix = "frontend/nextjs/"

        for tpl in templates:
            content = await self.template_engine.render_template(tpl, template_vars)

            rel_path = Path(tpl[len(prefix):]).with_suffix("")
            out_file = output_path / rel_path
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(content)
            generated_files.append(str(out_file))

        return {
            "framework": "nextjs",
            "generated_files": generated_files,
            "output_path": str(output_path),
            "next_steps": [
                "1. Instalar dependencias: npm install",
                "2. Iniciar servidor de desarrollo: npm run dev",
            ],
            "run_commands": {
                "dev": "npm run dev",
                "build": "npm run build",
                "test": "npm test",
            },
        }
