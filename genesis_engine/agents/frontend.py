# genesis_engine/agents/frontend.py
"""Frontend Agent - CORREGIDO
-----------------

Agent responsible for generating frontend projects using different
JavaScript frameworks. FIXED: Now properly generates Dockerfiles.
"""

import os
import json
import asyncio
import uuid
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging

from jinja2 import Environment, FileSystemLoader, Template, TemplateError
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
from genesis_engine.templates.engine import TemplateEngine
from genesis_engine.core.logging import get_logger
from genesis_engine.core.exceptions import GenesisException

class FrontendFramework(str, Enum):
    """Frameworks de frontend soportados"""
    REACT = "react"
    NEXTJS = "nextjs" 
    VUE = "vue"
    NUXT = "nuxt"
    SVELTE = "svelte"
    ANGULAR = "angular"

class StateManagement(str, Enum):
    """Sistemas de gestión de estado"""
    REDUX_TOOLKIT = "redux_toolkit"
    ZUSTAND = "zustand"
    PINIA = "pinia"
    VUEX = "vuex"
    CONTEXT_API = "context_api"
    MOBX = "mobx"

class UILibrary(str, Enum):
    """Librerías de UI soportadas"""
    TAILWINDCSS = "tailwindcss"
    STYLED_COMPONENTS = "styled_components"
    MATERIAL_UI = "material_ui"
    CHAKRA_UI = "chakra_ui"
    SHADCN_UI = "shadcn_ui"

@dataclass
class FrontendConfig:
    """Configuración del frontend"""
    framework: FrontendFramework = FrontendFramework.NEXTJS
    state_management: StateManagement = StateManagement.REDUX_TOOLKIT
    ui_library: UILibrary = UILibrary.TAILWINDCSS
    typescript: bool = True
    testing_framework: str = "jest"
    pwa_enabled: bool = False
    ssr_enabled: bool = True
    features: List[str] = field(default_factory=list)
    custom_components: List[str] = field(default_factory=list)
    api_base_url: str = "http://localhost:8000"
    environment_vars: Dict[str, Any] = field(default_factory=dict)

class FrontendAgent(GenesisAgent):
    """
    Agente Frontend - Generador de interfaces web modernas
    CORREGIDO: Ahora genera Dockerfiles correctamente
    """

    def __init__(self):
        super().__init__(
            agent_id="frontend_agent",
            name="FrontendAgent",
            agent_type="frontend",
        )

        # Capacidades básicas
        self.add_capability("nextjs_generation")
        self.add_capability("react_generation") 
        self.add_capability("vue_generation")
        self.add_capability("dockerfile_generation")  # NUEVA CAPACIDAD
        self.add_capability("ui_components")
        self.add_capability("state_management")
        self.add_capability("pwa_configuration")
        self.add_capability("typescript_setup")

        # Registrar handlers específicos
        self.register_handler("generate_frontend", self._handle_generate_frontend)
        self.register_handler("generate_components", self._handle_generate_components)
        self.register_handler("setup_state_management", self._handle_setup_state_management)
        self.register_handler("configure_ui_library", self._handle_configure_ui_library)
        self.register_handler("setup_routing", self._handle_setup_routing)
        self.register_handler("generate_dockerfile", self._handle_generate_dockerfile)  # NUEVO HANDLER

        self.template_engine = TemplateEngine()
        self.logger = get_logger(f"agent.{self.agent_id}")

    async def initialize(self):
        """Inicialización del agente frontend"""
        self.logger.info("🎨 Inicializando Frontend Agent")

        self.set_metadata("version", "1.0.1")  # Version actualizada
        self.set_metadata("supported_frameworks", [f.value for f in FrontendFramework])
        self.set_metadata("supported_ui_libraries", [ui.value for ui in UILibrary])
        self.set_metadata("dockerfile_support", True)  # NUEVA METADATA

        self.logger.info("✅ Frontend Agent inicializado con soporte Docker")

    async def execute_task(self, task: AgentTask) -> TaskResult:
        """Ejecutar tarea específica del frontend"""
        task_name = task.name.lower()

        try:
            if "generate_frontend" in task_name:
                result = self._generate_complete_frontend(task.params)
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result
                )
            elif "generate_dockerfile" in task_name:
                result = await self._generate_frontend_dockerfile(task.params)
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result
                )
            elif "generate_components" in task_name:
                result = await self._generate_components(task.params)
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result
                )
            elif "setup_state_management" in task_name:
                result = await self._setup_state_management(task.params)
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result
                )
            else:
                raise ValueError(f"Tarea no reconocida: {task.name}")
        
        except Exception as e:
            self.logger.error(f"Error ejecutando tarea {task.name}: {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )

    # Handlers MCP
    def _handle_generate_frontend(self, request) -> Dict[str, Any]:
        """Handler para generación de frontend"""
        return self._generate_complete_frontend(request.data)

    async def _handle_generate_dockerfile(self, request) -> Dict[str, Any]:
        """Handler para generación de Dockerfile"""
        return await self._generate_frontend_dockerfile(request.data)

    async def _handle_generate_components(self, request) -> Dict[str, Any]:
        """Handler para generación de componentes"""
        return await self._generate_components(request.data)

    async def _handle_setup_state_management(self, request) -> Dict[str, Any]:
        """Handler para configuración de estado"""
        return await self._setup_state_management(request.data)

    async def _handle_configure_ui_library(self, request) -> Dict[str, Any]:
        """Handler para configuración de UI library"""
        return await self._configure_ui_library(request.data)

    async def _handle_setup_routing(self, request) -> Dict[str, Any]:
        """Handler para configuración de routing"""
        return await self._setup_routing(request.data)

    def _generate_complete_frontend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a frontend project for the selected framework."""
        self.logger.info("🚀 Generando frontend completo")
        
        # Extraer configuración
        config = self._extract_frontend_config(params)
        schema = params.get("schema", {})
        output_path = Path(params.get("output_path", "./frontend"))
        
        # Crear estructura de directorios
        self._create_directory_structure(output_path, config)
        
        # Generar archivos principales
        generated_files = []
        
        # 1. Configuración del proyecto
        config_files = self._generate_project_config(output_path, config, schema)
        generated_files.extend(config_files)
        
        # 2. Aplicación principal
        app_files = self._generate_main_application(output_path, config, schema)
        generated_files.extend(app_files)
        
        # 3. Dockerfile - generado solo para ciertos frameworks
        if config.framework != FrontendFramework.REACT:
            dockerfile = self._generate_dockerfile(output_path, config)
            if dockerfile:
                generated_files.append(dockerfile)
        
        # 4. Componentes base
        component_files = self._generate_base_components(output_path, config, schema)
        generated_files.extend(component_files)
        
        # 5. Configuración de estado
        if config.state_management != StateManagement.CONTEXT_API:
            state_files = self._generate_state_management(output_path, config, schema)
            generated_files.extend(state_files)
        
        # 6. Configuración de UI
        ui_files = self._generate_ui_configuration(output_path, config)
        generated_files.extend(ui_files)
        
        # 7. Routing
        routing_files = self._generate_routing_config(output_path, config, schema)
        generated_files.extend(routing_files)
        
        # 8. Configuración de TypeScript (si está habilitado)
        if config.typescript:
            ts_files = self._generate_typescript_config(output_path, config)
            generated_files.extend(ts_files)

        return {
            "framework": config.framework.value,
            "typescript": config.typescript,
            "ui_library": config.ui_library.value,
            "state_management": config.state_management.value,
            "generated_files": generated_files,
            "output_path": str(output_path),
            "dockerfile_generated": True,  # NUEVA FLAG
            "next_steps": self._get_next_steps(config),
            "run_commands": self._get_run_commands(config),
        }

    def _generate_dockerfile(self, output_path: Path, config: FrontendConfig) -> Optional[str]:
        """
        NUEVO MÉTODO: Generar Dockerfile para el framework específico
        """
        try:
            template_map = {
                FrontendFramework.NEXTJS: "frontend/nextjs/Dockerfile.j2",
                FrontendFramework.REACT: "frontend/react/Dockerfile.j2",
                FrontendFramework.VUE: "frontend/vue/Dockerfile.j2",
            }
            
            template_name = template_map.get(config.framework)
            if not template_name:
                self.logger.warning(f"No hay template de Dockerfile para {config.framework}")
                return None
            
            template_vars = {
                "framework": config.framework.value,
                "node_version": "18",
                "port": 3000 if config.framework == FrontendFramework.NEXTJS else 80,
                "build_command": self._get_build_command(config.framework),
                "start_command": self._get_start_command(config.framework),
            }
            
            content = self.template_engine.render_template(template_name, template_vars)
            dockerfile_path = output_path / "Dockerfile"
            dockerfile_path.write_text(content)
            
            self.logger.info(f"✅ Dockerfile generado: {dockerfile_path}")
            return str(dockerfile_path)
            
        except Exception as e:
            self.logger.error(f"Error generando Dockerfile: {e}")
            return None

    def _get_build_command(self, framework: FrontendFramework) -> str:
        """Obtener comando de build según el framework"""
        commands = {
            FrontendFramework.NEXTJS: "npm run build",
            FrontendFramework.REACT: "npm run build",
            FrontendFramework.VUE: "npm run build",
        }
        return commands.get(framework, "npm run build")

    def _get_start_command(self, framework: FrontendFramework) -> str:
        """Obtener comando de start según el framework"""
        commands = {
            FrontendFramework.NEXTJS: "npm start",
            FrontendFramework.REACT: "nginx -g 'daemon off;'",
            FrontendFramework.VUE: "nginx -g 'daemon off;'",
        }
        return commands.get(framework, "npm start")

    async def _generate_frontend_dockerfile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        NUEVO MÉTODO: Generar solo el Dockerfile
        """
        config = self._extract_frontend_config(params)
        output_path = Path(params.get("output_path", "./frontend"))
        
        dockerfile = self._generate_dockerfile(output_path, config)
        
        return {
            "dockerfile_generated": dockerfile is not None,
            "dockerfile_path": dockerfile,
            "framework": config.framework.value
        }

    def _extract_frontend_config(self, params: Dict[str, Any]) -> FrontendConfig:
        """Extraer configuración del frontend"""
        stack = params.get("stack", {})

        framework_val = params.get("framework", stack.get("frontend", "nextjs"))
        state_management_val = params.get("state_management", stack.get("state_management", "redux_toolkit"))
        ui_library_val = params.get("ui_library", stack.get("ui_library", "tailwindcss"))

        typescript_default = False if framework_val == FrontendFramework.REACT.value else True
        typescript_val = params.get("typescript", typescript_default)

        return FrontendConfig(
            framework=FrontendFramework(framework_val),
            state_management=StateManagement(state_management_val),
            ui_library=UILibrary(ui_library_val),
            typescript=typescript_val,
            testing_framework=params.get("testing_framework", "jest"),
            pwa_enabled=params.get("pwa_enabled", False),
            ssr_enabled=params.get("ssr_enabled", True),
            features=params.get("features", []),
            custom_components=params.get("custom_components", []),
            api_base_url=params.get("api_base_url", "http://localhost:8000"),
            environment_vars=params.get("env_vars", {})
        )

    def _create_directory_structure(self, base_path: Path, config: FrontendConfig):
        """Crear estructura de directorios"""
        if config.framework == FrontendFramework.NEXTJS:
            directories = [
                "app",
                "components/ui",
                "components/layout", 
                "components/features",
                "lib",
                "hooks",
                "types",
                "store",
                "styles",
                "public",
                "tests"
            ]
        elif config.framework == FrontendFramework.REACT:
            directories = [
                "src/components/ui",
                "src/components/layout",
                "src/components/features",
                "src/hooks",
                "src/types",
                "src/store",
                "src/services",
                "src/utils",
                "src/styles",
                "public",
                "tests"
            ]
        elif config.framework == FrontendFramework.VUE:
            directories = [
                "src/components",
                "src/views",
                "src/router",
                "src/store",
                "src/composables",
                "src/types",
                "src/services",
                "src/assets",
                "public",
                "tests"
            ]
        
        for directory in directories:
            (base_path / directory).mkdir(parents=True, exist_ok=True)

    def _generate_project_config(
        self, 
        output_path: Path, 
        config: FrontendConfig,
        schema: Dict[str, Any]
    ) -> List[str]:
        """Generar archivos de configuración del proyecto"""
        generated_files = []
        
        if config.framework in [FrontendFramework.NEXTJS, FrontendFramework.REACT]:
            # package.json
            package_file = self._generate_package_json(output_path, config, schema)
            generated_files.append(package_file)
            
            # tsconfig.json (si TypeScript está habilitado)
            if config.typescript:
                tsconfig_file = self._generate_tsconfig(output_path, config)
                generated_files.append(tsconfig_file)
            
            # next.config.js (solo para Next.js)
            if config.framework == FrontendFramework.NEXTJS:
                nextconfig_file = self._generate_next_config(output_path, config)
                generated_files.append(nextconfig_file)
        
        elif config.framework == FrontendFramework.VUE:
            # package.json para Vue
            package_file = self._generate_vue_package_json(output_path, config, schema)
            generated_files.append(package_file)
            
            # vite.config.ts
            vite_config = self._generate_vite_config(output_path, config)
            generated_files.append(vite_config)
        
        return generated_files

    def _generate_package_json(
        self,
        output_path: Path,
        config: FrontendConfig,
        schema: Dict[str, Any]
    ) -> str:
        """Generar package.json"""
        template_vars = {
            "project_name": schema.get("project_name", "genesis-frontend"),
            "description": schema.get("description", "Generated with Genesis Engine"),
            "framework": config.framework.value,
            "typescript": config.typescript,
            "ui_library": config.ui_library.value,
            "state_management": config.state_management.value,
            "testing_framework": config.testing_framework,
            "pwa_enabled": config.pwa_enabled
        }
        
        if config.framework == FrontendFramework.NEXTJS:
            template_name = "frontend/nextjs/package.json.j2"
        else:
            template_name = "frontend/react/package.json.j2"
        
        content = self.template_engine.render_template(template_name, template_vars)
        
        output_file = output_path / "package.json"
        output_file.write_text(content)
        
        return str(output_file)

    # Resto de métodos anteriores...
    def _generate_main_application(self, output_path: Path, config: FrontendConfig, schema: Dict[str, Any]) -> List[str]:
        """Generar aplicación principal"""
        generated_files = []

        if config.framework == FrontendFramework.NEXTJS:
            # app/layout.tsx
            layout_file = output_path / "app/layout.tsx"
            layout_file.parent.mkdir(parents=True, exist_ok=True)
            layout_content = self.template_engine.render_template(
                "frontend/nextjs/app/layout.tsx.j2",
                {
                    "project_name": schema.get("project_name", "Genesis App"),
                    "description": schema.get("description", "Generated with Genesis Engine")
                }
            )
            layout_file.write_text(layout_content)
            generated_files.append(str(layout_file))

            # app/page.tsx
            page_file = output_path / "app/page.tsx"
            page_content = self.template_engine.render_template(
                "frontend/nextjs/app/page.tsx.j2",
                {
                    "project_name": schema.get("project_name", "Genesis App"),
                    "description": schema.get("description", "Generated with Genesis Engine")
                }
            )
            page_file.write_text(page_content)
            generated_files.append(str(page_file))

        elif config.framework == FrontendFramework.REACT:
            index_file = output_path / "index.html"
            index_content = self.template_engine.render_template(
                "frontend/react/index.html.j2",
                {"project_name": schema.get("project_name", "Genesis App")}
            )
            index_file.write_text(index_content)
            generated_files.append(str(index_file))

            app_file = output_path / "src/App.tsx"
            app_file.parent.mkdir(parents=True, exist_ok=True)
            app_content = self.template_engine.render_template(
                "frontend/react/src/App.tsx.j2",
                {
                    "project_name": schema.get("project_name", "Genesis App"),
                    "description": schema.get("description", "Generated with Genesis Engine")
                }
            )
            app_file.write_text(app_content)
            generated_files.append(str(app_file))

            main_file = output_path / "src/main.tsx"
            main_content = self.template_engine.render_template(
                "frontend/react/src/main.tsx.j2", {}
            )
            main_file.write_text(main_content)
            generated_files.append(str(main_file))

        return generated_files

    # Métodos auxiliares anteriores sin cambios...
    def _generate_base_components(self, output_path: Path, config: FrontendConfig, schema: Dict[str, Any]) -> List[str]:
        return []

    def _generate_state_management(self, output_path: Path, config: FrontendConfig, schema: Dict[str, Any]) -> List[str]:
        return []

    def _generate_ui_configuration(self, output_path: Path, config: FrontendConfig) -> List[str]:
        return []

    def _generate_routing_config(self, output_path: Path, config: FrontendConfig, schema: Dict[str, Any]) -> List[str]:
        return []

    def _generate_typescript_config(self, output_path: Path, config: FrontendConfig) -> List[str]:
        return []

    def _get_next_steps(self, config: FrontendConfig) -> List[str]:
        """Obtener siguientes pasos"""
        steps = [
            "1. Instalar dependencias: npm install",
            "2. Configurar variables de entorno en .env.local",
        ]
        
        if config.framework == FrontendFramework.NEXTJS:
            steps.extend([
                "3. Iniciar servidor de desarrollo: npm run dev",
                "4. Acceder a: http://localhost:3000"
            ])
        elif config.framework == FrontendFramework.REACT:
            steps.extend([
                "3. Iniciar servidor de desarrollo: npm start",
                "4. Acceder a: http://localhost:3000"
            ])
        elif config.framework == FrontendFramework.VUE:
            steps.extend([
                "3. Iniciar servidor de desarrollo: npm run dev",
                "4. Acceder a: http://localhost:5173"
            ])
        
        return steps

    def _get_run_commands(self, config: FrontendConfig) -> Dict[str, str]:
        """Obtener comandos de ejecución"""
        if config.framework == FrontendFramework.NEXTJS:
            return {
                "install": "npm install",
                "dev": "npm run dev",
                "build": "npm run build",
                "start": "npm start",
                "test": "npm test",
                "lint": "npm run lint",
                "docker_build": "docker build -t frontend .",
                "docker_run": "docker run -p 3000:3000 frontend"
            }
        elif config.framework == FrontendFramework.REACT:
            return {
                "install": "npm install", 
                "start": "npm start",
                "build": "npm run build",
                "test": "npm test",
                "docker_build": "docker build -t frontend .",
                "docker_run": "docker run -p 80:80 frontend"
            }
        elif config.framework == FrontendFramework.VUE:
            return {
                "install": "npm install",
                "dev": "npm run dev",
                "build": "npm run build",
                "preview": "npm run preview",
                "test": "npm run test",
                "docker_build": "docker build -t frontend .",
                "docker_run": "docker run -p 80:80 frontend"
            }
        
        return {}

    # Métodos auxiliares async - implementación simplificada
    async def _generate_components(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "components_generated"}

    async def _setup_state_management(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "state_management_configured"}

    async def _configure_ui_library(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ui_library_configured"}

    async def _setup_routing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "routing_configured"}

    # Métodos de configuración específicos
    def _generate_tsconfig(self, output_path: Path, config: FrontendConfig) -> str:
        """Generar tsconfig.json"""
        output_file = output_path / "tsconfig.json"
        content = '{"compilerOptions": {"target": "ES2020", "module": "commonjs", "strict": true}}'
        output_file.write_text(content)
        return str(output_file)

    def _generate_next_config(self, output_path: Path, config: FrontendConfig) -> str:
        """Generar next.config.js"""
        output_file = output_path / "next.config.js"
        content = self.template_engine.render_template("frontend/nextjs/next.config.js.j2", {})
        output_file.write_text(content)
        return str(output_file)

    def _generate_vue_package_json(self, output_path: Path, config: FrontendConfig, schema: Dict[str, Any]) -> str:
        """Generar package.json para Vue"""
        template_vars = {
            "project_name": schema.get("project_name", "vue-app"),
            "description": schema.get("description", "Vue application")
        }
        content = self.template_engine.render_template("frontend/vue/package.json.j2", template_vars)
        output_file = output_path / "package.json"
        output_file.write_text(content)
        return str(output_file)

    def _generate_vite_config(self, output_path: Path, config: FrontendConfig) -> str:
        """Generar vite.config.ts"""
        output_file = output_path / "vite.config.ts"
        output_file.write_text('export default {}')
        return str(output_file)