"""
Backend Agent - Generación de código backend

Este agente es responsable de:
- Generar código backend completo (FastAPI, Node/NestJS, etc.)
- Crear modelos de datos y ORMs
- Generar APIs REST y endpoints
- Configurar base de datos y migraciones
- Implementar autenticación y autorización
- Generar documentación de API
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
from genesis_engine.templates.engine import TemplateEngine

class BackendFramework(str, Enum):
    """Frameworks de backend soportados"""
    FASTAPI = "fastapi"
    NESTJS = "nestjs"
    EXPRESS = "express"
    DJANGO = "django"
    FLASK = "flask"
    SPRING_BOOT = "spring_boot"

class DatabaseType(str, Enum):
    """Tipos de base de datos"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"

class AuthMethod(str, Enum):
    """Métodos de autenticación"""
    JWT = "jwt"
    SESSION = "session"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"

@dataclass
class BackendConfig:
    """Configuración del backend"""
    framework: BackendFramework
    database: DatabaseType
    auth_method: AuthMethod
    features: List[str]
    dependencies: List[str]
    environment_vars: Dict[str, str]

@dataclass
class APIEndpoint:
    """Definición de un endpoint de API"""
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    auth_required: bool
    tags: List[str]

class BackendAgent(GenesisAgent):
    """
    Agente Backend - Generador de código backend
    
    Responsable de generar código backend completo basado en el schema
    del proyecto y las especificaciones de la arquitectura.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="backend_agent",
            name="BackendAgent",
            agent_type="backend"
        )
        
        # Capacidades del agente
        self.add_capability("fastapi_generation")
        self.add_capability("nestjs_generation")
        self.add_capability("database_modeling")
        self.add_capability("api_design")
        self.add_capability("authentication_setup")
        self.add_capability("migration_generation")
        self.add_capability("swagger_documentation")
        
        # Registrar handlers específicos
        self.register_handler("generate_backend", self._handle_generate_backend)
        self.register_handler("generate_models", self._handle_generate_models)
        self.register_handler("generate_api", self._handle_generate_api)
        self.register_handler("setup_database", self._handle_setup_database)
        self.register_handler("setup_auth", self._handle_setup_auth)
        self.register_handler("generate_docs", self._handle_generate_docs)
        
        # Motor de templates
        self.template_engine = TemplateEngine()
        
        # Configuraciones por framework
        try:
            self.framework_configs = self._load_framework_configs()
        except NotImplementedError:
            self.logger.warning("Framework config loader not implemented")
            self.framework_configs = {}
        
    async def initialize(self):
        """Inicialización del agente backend"""
        self.logger.info("⚙️ Inicializando Backend Agent")
        
        # Cargar templates de código
        try:
            await self._load_code_templates()
        except NotImplementedError:
            self.logger.warning("Code template loading not implemented")

        # Configurar generadores específicos
        try:
            await self._setup_code_generators()
        except NotImplementedError:
            self.logger.warning("Code generators setup not implemented")
        
        self.set_metadata("version", "1.0.0")
        self.set_metadata("supported_frameworks", list(BackendFramework))
        
        self.logger.info("✅ Backend Agent inicializado")
    
    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica del backend"""
        task_name = task.name.lower()
        
        if "generate_backend" in task_name:
            return await self._generate_complete_backend(task.params)
        elif "generate_models" in task_name:
            return await self._generate_data_models(task.params)
        elif "generate_api" in task_name:
            return await self._generate_api_endpoints(task.params)
        elif "setup_database" in task_name:
            return await self._setup_database_config(task.params)
        elif "setup_auth" in task_name:
            return await self._setup_authentication(task.params)
        elif "generate_docs" in task_name:
            return await self._generate_api_documentation(task.params)
        else:
            raise ValueError(f"Tarea no reconocida: {task.name}")
    
    async def _generate_complete_backend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generar backend completo"""
        self.logger.info("🚀 Generando backend completo")
        
        project_schema = params.get("schema", {})
        config = self._extract_backend_config(params)
        output_path = Path(params.get("output_path", "./backend"))
        
        # Crear estructura de directorios
        self._create_directory_structure(output_path, config.framework)
        
        # Generar archivos principales
        generated_files = []
        
        # 1. Archivo principal de la aplicación
        main_file = await self._generate_main_application(output_path, config, project_schema)
        generated_files.append(main_file)
        
        # 2. Modelos de datos
        model_files = await self._generate_data_models({
            "schema": project_schema,
            "config": config,
            "output_path": output_path / "models"
        })
        generated_files.extend(model_files)
        
        # 3. Endpoints de API
        api_files = await self._generate_api_endpoints({
            "schema": project_schema,
            "config": config,
            "output_path": output_path / "routes"
        })
        generated_files.extend(api_files)
        
        # 4. Configuración de base de datos
        db_files = await self._setup_database_config({
            "config": config,
            "schema": project_schema,
            "output_path": output_path
        })
        generated_files.extend(db_files)
        
        # 5. Configuración de autenticación
        auth_files = await self._setup_authentication({
            "config": config,
            "output_path": output_path / "auth"
        })
        generated_files.extend(auth_files)
        
        # 6. Archivos de configuración
        config_files = await self._generate_config_files(output_path, config, project_schema)
        generated_files.extend(config_files)
        
        # 7. Documentación
        doc_files = await self._generate_api_documentation({
            "schema": project_schema,
            "config": config,
            "output_path": output_path / "docs"
        })
        generated_files.extend(doc_files)
        
        result = {
            "framework": config.framework.value,
            "database": config.database.value,
            "generated_files": generated_files,
            "output_path": str(output_path),
            "next_steps": self._get_next_steps(config),
            "run_commands": self._get_run_commands(config)
        }
        
        self.logger.info(f"✅ Backend generado - {len(generated_files)} archivos creados")
        return result
    
    def _extract_backend_config(self, params: Dict[str, Any]) -> BackendConfig:
        """Extraer configuración del backend"""
        stack = params.get("stack", {})
        
        return BackendConfig(
            framework=BackendFramework(stack.get("backend", "fastapi")),
            database=DatabaseType(stack.get("database", "postgresql")),
            auth_method=AuthMethod(stack.get("auth", "jwt")),
            features=params.get("features", []),
            dependencies=params.get("dependencies", []),
            environment_vars=params.get("env_vars", {})
        )
    
    def _create_directory_structure(self, base_path: Path, framework: BackendFramework):
        """Crear estructura de directorios"""
        if framework == BackendFramework.FASTAPI:
            directories = [
                "app/models",
                "app/routes", 
                "app/services",
                "app/auth",
                "app/core",
                "app/db",
                "app/schemas",
                "tests",
                "migrations",
                "docs"
            ]
        elif framework == BackendFramework.NESTJS:
            directories = [
                "src/modules",
                "src/entities",
                "src/controllers",
                "src/services",
                "src/auth",
                "src/config",
                "src/database",
                "test",
                "docs"
            ]
        else:
            directories = [
                "src/models",
                "src/routes",
                "src/services",
                "src/middleware",
                "src/config",
                "tests",
                "docs"
            ]
        
        for directory in directories:
            (base_path / directory).mkdir(parents=True, exist_ok=True)
            
            # Crear __init__.py para Python
            if framework in [BackendFramework.FASTAPI, BackendFramework.DJANGO, BackendFramework.FLASK]:
                init_file = base_path / directory / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("")
    
    async def _generate_main_application(
        self, 
        output_path: Path, 
        config: BackendConfig, 
        schema: Dict[str, Any]
    ) -> str:
        """Generar archivo principal de la aplicación"""
        
        if config.framework == BackendFramework.FASTAPI:
            template_name = "fastapi/main.py.j2"
            output_file = output_path / "app" / "main.py"
            
            template_vars = {
                "project_name": schema.get("project_name", "Genesis App"),
                "description": schema.get("description", "Generated by Genesis Engine"),
                "version": "1.0.0",
                "cors_enabled": True,
                "auth_enabled": config.auth_method != AuthMethod.API_KEY,
                "database_enabled": True,
                "entities": schema.get("entities", [])
            }
            
        elif config.framework == BackendFramework.NESTJS:
            template_name = "nestjs/main.ts.j2"
            output_file = output_path / "src" / "main.ts"
            
            template_vars = {
                "project_name": schema.get("project_name", "Genesis App"),
                "port": 3000,
                "cors_enabled": True,
                "swagger_enabled": True
            }
        
        else:
            raise ValueError(f"Framework no soportado: {config.framework}")
        
        # Generar archivo usando template
        content = await self.template_engine.render_template(template_name, template_vars)
        
        output_file.write_text(content)
        
        self.logger.info(f"📝 Archivo principal generado: {output_file}")
        return str(output_file)
    
    async def _generate_data_models(self, params: Dict[str, Any]) -> List[str]:
        """Generar modelos de datos"""
        self.logger.info("📊 Generando modelos de datos")
        
        schema = params.get("schema", {})
        config = params.get("config")
        output_path = Path(params.get("output_path", "./models"))
        
        entities = schema.get("entities", [])
        generated_files = []
        
        for entity in entities:
            if config.framework == BackendFramework.FASTAPI:
                # Generar modelo SQLAlchemy
                model_file = await self._generate_sqlalchemy_model(
                    entity, output_path, config
                )
                generated_files.append(model_file)
                
                # Generar schema Pydantic
                schema_file = await self._generate_pydantic_schema(
                    entity, output_path.parent / "schemas", config
                )
                generated_files.append(schema_file)
                
            elif config.framework == BackendFramework.NESTJS:
                # Generar entidad TypeORM
                entity_file = await self._generate_typeorm_entity(
                    entity, output_path, config
                )
                generated_files.append(entity_file)
        
        self.logger.info(f"✅ {len(generated_files)} modelos generados")
        return generated_files
    
    async def _generate_sqlalchemy_model(
        self, 
        entity: Dict[str, Any], 
        output_path: Path, 
        config: BackendConfig
    ) -> str:
        """Generar modelo SQLAlchemy"""
        
        template_vars = {
            "entity_name": entity["name"],
            "table_name": entity.get("metadata", {}).get("table_name", entity["name"].lower() + "s"),
            "attributes": entity.get("attributes", {}),
            "relationships": entity.get("relationships", []),
            "constraints": entity.get("constraints", []),
            "database_type": config.database.value
        }
        
        content = await self.template_engine.render_template(
            "fastapi/models/model.py.j2", 
            template_vars
        )
        
        output_file = output_path / f"{entity['name'].lower()}.py"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _generate_pydantic_schema(
        self, 
        entity: Dict[str, Any], 
        output_path: Path, 
        config: BackendConfig
    ) -> str:
        """Generar schema Pydantic"""
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        template_vars = {
            "entity_name": entity["name"],
            "attributes": entity.get("attributes", {}),
            "description": entity.get("description", f"Schema for {entity['name']}")
        }
        
        content = await self.template_engine.render_template(
            "fastapi/schemas/schema.py.j2",
            template_vars
        )
        
        output_file = output_path / f"{entity['name'].lower()}.py"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _generate_api_endpoints(self, params: Dict[str, Any]) -> List[str]:
        """Generar endpoints de API"""
        self.logger.info("🌐 Generando endpoints de API")
        
        schema = params.get("schema", {})
        config = params.get("config")
        output_path = Path(params.get("output_path", "./routes"))
        
        entities = schema.get("entities", [])
        generated_files = []
        
        for entity in entities:
            if config.framework == BackendFramework.FASTAPI:
                router_file = await self._generate_fastapi_router(
                    entity, output_path, config
                )
                generated_files.append(router_file)
                
            elif config.framework == BackendFramework.NESTJS:
                controller_file = await self._generate_nestjs_controller(
                    entity, output_path, config
                )
                generated_files.append(controller_file)
        
        # Generar archivo de rutas principal
        main_routes_file = await self._generate_main_routes(
            entities, output_path, config
        )
        generated_files.append(main_routes_file)
        
        self.logger.info(f"✅ {len(generated_files)} archivos de API generados")
        return generated_files
    
    async def _generate_fastapi_router(
        self,
        entity: Dict[str, Any],
        output_path: Path,
        config: BackendConfig
    ) -> str:
        """Generar router FastAPI"""
        
        entity_name = entity["name"]
        entity_lower = entity_name.lower()
        
        # Generar endpoints CRUD estándar
        endpoints = [
            {
                "method": "GET",
                "path": f"/{entity_lower}s",
                "function": f"get_{entity_lower}s",
                "description": f"Get all {entity_lower}s",
                "auth_required": True
            },
            {
                "method": "GET", 
                "path": f"/{entity_lower}s/{{id}}",
                "function": f"get_{entity_lower}",
                "description": f"Get {entity_lower} by ID",
                "auth_required": True
            },
            {
                "method": "POST",
                "path": f"/{entity_lower}s",
                "function": f"create_{entity_lower}",
                "description": f"Create new {entity_lower}",
                "auth_required": True
            },
            {
                "method": "PUT",
                "path": f"/{entity_lower}s/{{id}}",
                "function": f"update_{entity_lower}",
                "description": f"Update {entity_lower}",
                "auth_required": True
            },
            {
                "method": "DELETE",
                "path": f"/{entity_lower}s/{{id}}",
                "function": f"delete_{entity_lower}",
                "description": f"Delete {entity_lower}",
                "auth_required": True
            }
        ]
        
        template_vars = {
            "entity_name": entity_name,
            "entity_lower": entity_lower,
            "endpoints": endpoints,
            "attributes": entity.get("attributes", {}),
            "auth_enabled": config.auth_method != AuthMethod.API_KEY
        }
        
        content = await self.template_engine.render_template(
            "fastapi/routes/router.py.j2",
            template_vars
        )
        
        output_file = output_path / f"{entity_lower}.py"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _setup_database_config(self, params: Dict[str, Any]) -> List[str]:
        """Configurar base de datos"""
        self.logger.info("🗄️ Configurando base de datos")
        
        config = params.get("config")
        schema = params.get("schema", {})
        output_path = Path(params.get("output_path", "./"))
        
        generated_files = []
        
        if config.framework == BackendFramework.FASTAPI:
            # Generar configuración de SQLAlchemy
            db_config_file = await self._generate_sqlalchemy_config(
                output_path / "app" / "db", config
            )
            generated_files.append(db_config_file)
            
            # Generar migraciones Alembic
            migration_files = await self._setup_alembic_migrations(
                output_path, config, schema
            )
            generated_files.extend(migration_files)
        
        elif config.framework == BackendFramework.NESTJS:
            # Generar configuración de TypeORM
            db_config_file = await self._generate_typeorm_config(
                output_path / "src" / "database", config
            )
            generated_files.append(db_config_file)
        
        self.logger.info(f"✅ Configuración de BD generada - {len(generated_files)} archivos")
        return generated_files
    
    async def _setup_authentication(self, params: Dict[str, Any]) -> List[str]:
        """Configurar autenticación"""
        self.logger.info("🔐 Configurando autenticación")
        
        config = params.get("config")
        output_path = Path(params.get("output_path", "./auth"))
        
        generated_files = []
        
        if config.auth_method == AuthMethod.JWT:
            if config.framework == BackendFramework.FASTAPI:
                auth_files = await self._generate_fastapi_jwt_auth(output_path, config)
                generated_files.extend(auth_files)
                
            elif config.framework == BackendFramework.NESTJS:
                auth_files = await self._generate_nestjs_jwt_auth(output_path, config)
                generated_files.extend(auth_files)
        
        self.logger.info(f"✅ Autenticación configurada - {len(generated_files)} archivos")
        return generated_files
    
    async def _generate_config_files(
        self, 
        output_path: Path, 
        config: BackendConfig, 
        schema: Dict[str, Any]
    ) -> List[str]:
        """Generar archivos de configuración"""
        generated_files = []
        
        if config.framework == BackendFramework.FASTAPI:
            # requirements.txt
            requirements_file = await self._generate_python_requirements(
                output_path, config
            )
            generated_files.append(requirements_file)
            
            # .env template
            env_file = await self._generate_env_template(output_path, config)
            generated_files.append(env_file)
            
            # Dockerfile
            dockerfile = await self._generate_dockerfile_python(output_path, config)
            generated_files.append(dockerfile)
            
        elif config.framework == BackendFramework.NESTJS:
            # package.json
            package_file = await self._generate_package_json(output_path, config, schema)
            generated_files.append(package_file)
            
            # .env template
            env_file = await self._generate_env_template(output_path, config)
            generated_files.append(env_file)
            
            # Dockerfile
            dockerfile = await self._generate_dockerfile_node(output_path, config)
            generated_files.append(dockerfile)
        
        return generated_files
    
    def _get_next_steps(self, config: BackendConfig) -> List[str]:
        """Obtener siguientes pasos"""
        if config.framework == BackendFramework.FASTAPI:
            return [
                "1. Instalar dependencias: pip install -r requirements.txt",
                "2. Configurar variables de entorno en .env",
                "3. Ejecutar migraciones: alembic upgrade head",
                "4. Iniciar servidor: uvicorn app.main:app --reload",
                "5. Acceder a docs: http://localhost:8000/docs"
            ]
        elif config.framework == BackendFramework.NESTJS:
            return [
                "1. Instalar dependencias: npm install",
                "2. Configurar variables de entorno en .env",
                "3. Ejecutar migraciones: npm run migration:run",
                "4. Iniciar servidor: npm run start:dev",
                "5. Acceder a docs: http://localhost:3000/api/docs"
            ]
        
        return []
    
    def _get_run_commands(self, config: BackendConfig) -> Dict[str, str]:
        """Obtener comandos de ejecución"""
        if config.framework == BackendFramework.FASTAPI:
            return {
                "install": "pip install -r requirements.txt",
                "migrate": "alembic upgrade head",
                "dev": "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
                "prod": "uvicorn app.main:app --host 0.0.0.0 --port 8000",
                "test": "pytest"
            }
        elif config.framework == BackendFramework.NESTJS:
            return {
                "install": "npm install",
                "migrate": "npm run migration:run",
                "dev": "npm run start:dev",
                "prod": "npm run start:prod",
                "test": "npm run test"
            }
        
        return {}
    
    # Handlers MCP
    async def _handle_generate_backend(self, request) -> Dict[str, Any]:
        """Handler para generación de backend"""
        return await self._generate_complete_backend(request.params)
    
    async def _handle_generate_models(self, request) -> Dict[str, Any]:
        """Handler para generación de modelos"""
        files = await self._generate_data_models(request.params)
        return {"generated_files": files}
    
    async def _handle_generate_api(self, request) -> Dict[str, Any]:
        """Handler para generación de API"""
        files = await self._generate_api_endpoints(request.params)
        return {"generated_files": files}
    
    async def _handle_setup_database(self, request) -> Dict[str, Any]:
        """Handler para configuración de BD"""
        files = await self._setup_database_config(request.params)
        return {"generated_files": files}
    
    async def _handle_setup_auth(self, request) -> Dict[str, Any]:
        """Handler para configuración de auth"""
        files = await self._setup_authentication(request.params)
        return {"generated_files": files}
    
    async def _handle_generate_docs(self, request) -> Dict[str, Any]:
        """Handler para generación de docs"""
        files = await self._generate_api_documentation(request.params)
        return {"generated_files": files}
    
    # Métodos auxiliares que se implementarían completamente
    def _load_framework_configs(self) -> Dict[str, Any]:
        """Cargar configuraciones por framework"""
        raise NotImplementedError("_load_framework_configs not implemented")
    
    async def _load_code_templates(self):
        """Cargar templates de código"""
        raise NotImplementedError("_load_code_templates not implemented")
    
    async def _setup_code_generators(self):
        """Configurar generadores de código"""
        raise NotImplementedError("_setup_code_generators not implemented")
    
    async def _generate_typeorm_entity(self, entity: Dict[str, Any], output_path: Path, config: BackendConfig) -> str:
        """Generar entidad TypeORM"""
        raise NotImplementedError("_generate_typeorm_entity not implemented")
    
    async def _generate_nestjs_controller(self, entity: Dict[str, Any], output_path: Path, config: BackendConfig) -> str:
        """Generar controlador NestJS"""
        raise NotImplementedError("_generate_nestjs_controller not implemented")
    
    async def _generate_main_routes(self, entities: List[Dict[str, Any]], output_path: Path, config: BackendConfig) -> str:
        """Generar archivo principal de rutas"""
        raise NotImplementedError("_generate_main_routes not implemented")
    
    async def _generate_sqlalchemy_config(self, output_path: Path, config: BackendConfig) -> str:
        """Generar configuración SQLAlchemy"""
        raise NotImplementedError("_generate_sqlalchemy_config not implemented")
    
    async def _setup_alembic_migrations(self, output_path: Path, config: BackendConfig, schema: Dict[str, Any]) -> List[str]:
        """Configurar migraciones Alembic"""
        raise NotImplementedError("_setup_alembic_migrations not implemented")
    
    async def _generate_typeorm_config(self, output_path: Path, config: BackendConfig) -> str:
        """Generar configuración TypeORM"""
        raise NotImplementedError("_generate_typeorm_config not implemented")
    
    async def _generate_fastapi_jwt_auth(self, output_path: Path, config: BackendConfig) -> List[str]:
        """Generar autenticación JWT para FastAPI"""
        raise NotImplementedError("_generate_fastapi_jwt_auth not implemented")
    
    async def _generate_nestjs_jwt_auth(self, output_path: Path, config: BackendConfig) -> List[str]:
        """Generar autenticación JWT para NestJS"""
        raise NotImplementedError("_generate_nestjs_jwt_auth not implemented")
    
    async def _generate_python_requirements(self, output_path: Path, config: BackendConfig) -> str:
        """Generar requirements.txt"""
        raise NotImplementedError("_generate_python_requirements not implemented")
    
    async def _generate_env_template(self, output_path: Path, config: BackendConfig) -> str:
        """Generar template .env"""
        raise NotImplementedError("_generate_env_template not implemented")
    
    async def _generate_dockerfile_python(self, output_path: Path, config: BackendConfig) -> str:
        """Generar Dockerfile para Python"""
        raise NotImplementedError("_generate_dockerfile_python not implemented")
    
    async def _generate_package_json(self, output_path: Path, config: BackendConfig, schema: Dict[str, Any]) -> str:
        """Generar package.json"""
        raise NotImplementedError("_generate_package_json not implemented")
    
    async def _generate_dockerfile_node(self, output_path: Path, config: BackendConfig) -> str:
        """Generar Dockerfile para Node.js"""
        raise NotImplementedError("_generate_dockerfile_node not implemented")
    
    async def _generate_api_documentation(self, params: Dict[str, Any]) -> List[str]:
        """Generar documentación de API"""
        raise NotImplementedError("_generate_api_documentation not implemented")
