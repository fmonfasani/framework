# genesis_engine/agents/architect.py
"""
ArchitectAgent corregido - Agente especializado en diseño de arquitectura
Implementa todos los handlers necesarios para comunicación MCP
"""
from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ArchitectAgent(GenesisAgent):
    """
    Agente especializado en diseño de arquitectura y análisis de requisitos
    Responsable de:
    - Analizar requisitos del proyecto
    - Diseñar arquitectura técnica
    - Generar schema del proyecto
    - Validar coherencia entre componentes
    """
    
    def __init__(self):
        super().__init__(
            agent_id="architect_agent",
            name="ArchitectAgent",
            agent_type="architect"
        )
        
        # Agregar capacidades específicas
        self._setup_capabilities()
        
        # Registrar handlers específicos del arquitecto
        self._register_architect_handlers()
        
        # Plantillas de arquitectura disponibles
        self.architecture_patterns = {
            "layered": "Arquitectura en capas (Presentation, Business, Data)",
            "microservices": "Arquitectura de microservicios",
            "serverless": "Arquitectura serverless",
            "event_driven": "Arquitectura dirigida por eventos"
        }
        
        # Stacks tecnológicos soportados
        self.tech_stacks = {
            "python_fullstack": {
                "backend": "FastAPI + SQLAlchemy + PostgreSQL",
                "frontend": "Next.js + TypeScript + Tailwind",
                "deployment": "Docker + Docker Compose"
            },
            "node_fullstack": {
                "backend": "NestJS + TypeORM + PostgreSQL", 
                "frontend": "React + TypeScript + Redux",
                "deployment": "Docker + Kubernetes"
            },
            "minimal_api": {
                "backend": "FastAPI + SQLite",
                "frontend": "Static HTML/CSS/JS",
                "deployment": "Single Docker container"
            }
        }
    
    def _setup_capabilities(self):
        """Configurar capacidades del agente"""
        capabilities = [
            "analyze_requirements",
            "design_architecture", 
            "generate_schema",
            "validate_architecture",
            "suggest_technologies",
            "estimate_complexity",
            "create_project_structure"
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    def _register_architect_handlers(self):
        """Registrar handlers específicos del arquitecto"""
        self.register_handler("analyze_requirements", self._handle_analyze_requirements)
        self.register_handler("design_architecture", self._handle_design_architecture)
        self.register_handler("generate_schema", self._handle_generate_schema)
        self.register_handler("validate_architecture", self._handle_validate_architecture)
        self.register_handler("suggest_technologies", self._handle_suggest_technologies)
    
    async def execute_task(self, task: AgentTask) -> TaskResult:
        """
        Ejecutar tarea específica del arquitecto
        Este es el método principal que maneja todas las tareas
        """
        try:
            self.logger.info(f"🏗️ Ejecutando tarea de arquitectura: {task.name}")
            
            # Routing de tareas por nombre
            if task.name == "analyze_requirements":
                result = await self._analyze_requirements(task.params)
            elif task.name == "design_architecture":
                result = await self._design_architecture(task.params)
            elif task.name == "generate_schema":
                result = await self._generate_project_schema(task.params)
            elif task.name == "validate_architecture":
                result = await self._validate_architecture(task.params)
            elif task.name == "suggest_technologies":
                result = await self._suggest_technologies(task.params)
            elif task.name == "estimate_complexity":
                result = await self._estimate_complexity(task.params)
            else:
                # Tarea genérica o no reconocida
                result = await self._handle_generic_task(task)
            
            self.logger.info(f"✅ Tarea {task.name} completada exitosamente")
            
            return TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                metadata={
                    "agent": self.name,
                    "task_type": task.name,
                    "complexity": self._assess_task_complexity(task)
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando tarea {task.name}: {str(e)}")
            
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                metadata={
                    "agent": self.name,
                    "task_type": task.name,
                    "error_type": type(e).__name__
                }
            )
    
    async def _handle_analyze_requirements(self, request) -> Dict[str, Any]:
        """Handler directo para analyze_requirements"""
        data = getattr(request, 'data', {})
        return await self._analyze_requirements(data)
    
    async def _handle_design_architecture(self, request) -> Dict[str, Any]:
        """Handler directo para design_architecture"""
        data = getattr(request, 'data', {})
        return await self._design_architecture(data)
    
    async def _handle_generate_schema(self, request) -> Dict[str, Any]:
        """Handler directo para generate_schema"""
        data = getattr(request, 'data', {})
        return await self._generate_project_schema(data)
    
    async def _handle_validate_architecture(self, request) -> Dict[str, Any]:
        """Handler directo para validate_architecture"""
        data = getattr(request, 'data', {})
        return await self._validate_architecture(data)
    
    async def _handle_suggest_technologies(self, request) -> Dict[str, Any]:
        """Handler directo para suggest_technologies"""
        data = getattr(request, 'data', {})
        return await self._suggest_technologies(data)
    
    async def _analyze_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analizar requisitos del proyecto y categorizarlos
        Esta es la función que está fallando en el error actual
        """
        self.logger.info("🔍 Iniciando análisis de requisitos...")
        
        # Extraer parámetros
        description = params.get("description", "")
        project_type = params.get("type", "web_app")
        features = params.get("features", [])
        constraints = params.get("constraints", [])
        
        # Análisis de descripción
        description_analysis = self._analyze_description(description)
        
        # Categorizar requisitos
        requirements = {
            "functional": [],
            "non_functional": [],
            "technical": [],
            "business": [],
            "constraints": constraints
        }
        
        # Requisitos funcionales basados en features
        for feature in features:
            functional_reqs = self._get_functional_requirements(feature)
            requirements["functional"].extend(functional_reqs)
        
        # Requisitos técnicos
        requirements["technical"] = self._get_technical_requirements(features, project_type)
        
        # Requisitos no funcionales
        requirements["non_functional"] = self._get_non_functional_requirements(project_type)
        
        # Requisitos de negocio
        requirements["business"] = self._get_business_requirements(description_analysis, features)
        
        # Estimación de complejidad
        complexity = self._estimate_project_complexity(features, requirements)
        
        result = {
            "project_type": project_type,
            "description": description,
            "description_analysis": description_analysis,
            "features": features,
            "requirements": requirements,
            "complexity": complexity,
            "estimated_timeline": self._estimate_timeline(complexity),
            "recommended_team_size": self._estimate_team_size(complexity),
            "analysis_metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "analyzer": self.name,
                "version": self.version
            }
        }
        
        self.logger.info(f"✅ Análisis de requisitos completado. Complejidad: {complexity}")
        return result
    
    async def _design_architecture(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Diseñar arquitectura técnica del proyecto"""
        self.logger.info("🎨 Diseñando arquitectura...")
        
        requirements = params.get("requirements", {})
        features = params.get("features", [])
        complexity = params.get("complexity", "medium")
        
        # Seleccionar patrón de arquitectura
        architecture_pattern = self._select_architecture_pattern(complexity, features)
        
        # Diseñar capas
        layers = self._design_layers(architecture_pattern, features)
        
        # Diseñar componentes
        components = self._design_components(features, requirements)
        
        # Seleccionar tecnologías
        technologies = self._select_technologies(complexity, features)
        
        # Diseñar comunicación entre componentes
        communication = self._design_communication(components, architecture_pattern)
        
        architecture = {
            "pattern": architecture_pattern,
            "layers": layers,
            "components": components,
            "technologies": technologies,
            "communication": communication,
            "data_flow": self._design_data_flow(components),
            "security_considerations": self._design_security(features),
            "scalability_considerations": self._design_scalability(complexity),
            "design_metadata": {
                "designed_at": datetime.utcnow().isoformat(),
                "designer": self.name,
                "pattern_rationale": f"Seleccionado por complejidad {complexity} y features {features}"
            }
        }
        
        self.logger.info(f"✅ Arquitectura diseñada con patrón: {architecture_pattern}")
        return architecture
    
    async def _generate_project_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generar schema completo del proyecto"""
        self.logger.info("📋 Generando schema del proyecto...")
        
        # Extraer datos de entrada
        name = params.get("name", "genesis_project")
        description = params.get("description", "")
        requirements = params.get("requirements", {})
        architecture = params.get("architecture", {})
        features = params.get("features", [])
        
        # Generar esquema completo
        schema = {
            "project": {
                "name": name,
                "description": description,
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "generator": "Genesis Engine",
                "generator_version": self.version
            },
            "requirements": requirements,
            "architecture": architecture,
            "features": features,
            "structure": {
                "backend": self._generate_backend_structure(requirements, features, architecture),
                "frontend": self._generate_frontend_structure(requirements, features, architecture),
                "database": self._generate_database_structure(requirements, features),
                "deployment": self._generate_deployment_structure(architecture),
                "documentation": self._generate_documentation_structure()
            },
            "entities": self._generate_entities(requirements, features),
            "apis": self._generate_api_endpoints(requirements, features),
            "workflows": self._generate_workflows(features),
            "dependencies": self._generate_dependencies(architecture),
            "configuration": self._generate_configuration(architecture, features),
            "generated_files": [],  # Se llenará durante la generación
            "schema_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generator": self.name,
                "schema_version": "1.0.0"
            }
        }
        
        self.logger.info(f"✅ Schema generado para proyecto: {name}")
        return schema
    
    async def _validate_architecture(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validar coherencia de la arquitectura"""
        architecture = params.get("architecture", {})
        requirements = params.get("requirements", {})
        
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Validaciones específicas
        self._validate_layer_consistency(architecture, validation_result)
        self._validate_component_dependencies(architecture, validation_result)
        self._validate_technology_compatibility(architecture, validation_result)
        self._validate_security_requirements(architecture, requirements, validation_result)
        
        return validation_result
    
    async def _suggest_technologies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sugerir tecnologías basadas en requisitos"""
        features = params.get("features", [])
        complexity = params.get("complexity", "medium")
        constraints = params.get("constraints", [])
        
        suggestions = {}
        
        for stack_name, stack_config in self.tech_stacks.items():
            score = self._score_technology_stack(stack_config, features, complexity, constraints)
            suggestions[stack_name] = {
                "config": stack_config,
                "score": score,
                "pros": self._get_stack_pros(stack_name, features),
                "cons": self._get_stack_cons(stack_name, features)
            }
        
        # Ordenar por score
        sorted_suggestions = dict(sorted(suggestions.items(), key=lambda x: x[1]["score"], reverse=True))
        
        return {
            "suggestions": sorted_suggestions,
            "recommended": list(sorted_suggestions.keys())[0] if sorted_suggestions else None
        }
    
    async def _estimate_complexity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Estimar complejidad del proyecto"""
        features = params.get("features", [])
        requirements = params.get("requirements", {})
        
        complexity_score = 0
        factors = {}
        
        # Factores de complejidad
        factors["feature_count"] = len(features)
        factors["auth_complexity"] = 2 if "authentication" in features else 0
        factors["db_complexity"] = 2 if "database" in features else 0
        factors["api_complexity"] = 1 if "api" in features else 0
        factors["ui_complexity"] = 3 if "frontend" in features else 0
        
        # Calcular score total
        complexity_score = sum(factors.values())
        
        # Determinar nivel de complejidad
        if complexity_score <= 3:
            level = "low"
        elif complexity_score <= 8:
            level = "medium"
        else:
            level = "high"
        
        return {
            "level": level,
            "score": complexity_score,
            "factors": factors,
            "estimated_dev_time": self._estimate_development_time(level),
            "recommended_approach": self._recommend_approach(level)
        }
    
    async def _handle_generic_task(self, task: AgentTask) -> Dict[str, Any]:
        """Manejar tareas genéricas no específicas"""
        return {
            "message": f"Tarea genérica {task.name} procesada por ArchitectAgent",
            "task_id": task.id,
            "params": task.params,
            "agent": self.name
        }
    
    # Métodos auxiliares para análisis
    
    def _analyze_description(self, description: str) -> Dict[str, Any]:
        """Analizar descripción del proyecto"""
        words = description.lower().split()
        
        # Keywords que indican tipo de aplicación
        web_keywords = ["web", "website", "portal", "dashboard"]
        api_keywords = ["api", "service", "microservice", "backend"]
        mobile_keywords = ["mobile", "app", "ios", "android"]
        
        analysis = {
            "type_indicators": {
                "web": any(keyword in words for keyword in web_keywords),
                "api": any(keyword in words for keyword in api_keywords),
                "mobile": any(keyword in words for keyword in mobile_keywords)
            },
            "complexity_indicators": {
                "enterprise": any(word in words for word in ["enterprise", "corporate", "business"]),
                "saas": any(word in words for word in ["saas", "subscription", "tenant"]),
                "ecommerce": any(word in words for word in ["shop", "store", "ecommerce", "payment"])
            },
            "word_count": len(words),
            "technical_terms": [word for word in words if word in ["database", "api", "authentication", "payment"]]
        }
        
        return analysis
    
    def _get_functional_requirements(self, feature: str) -> List[str]:
        """Obtener requisitos funcionales para una feature"""
        feature_requirements = {
            "authentication": [
                "Usuario puede registrarse en el sistema",
                "Usuario puede iniciar sesión",
                "Usuario puede cerrar sesión",
                "Sistema puede validar credenciales"
            ],
            "database": [
                "Sistema puede almacenar datos persistentemente",
                "Sistema puede consultar datos eficientemente",
                "Sistema mantiene integridad de datos"
            ],
            "api": [
                "Sistema expone endpoints REST",
                "API puede manejar múltiples formatos",
                "API retorna respuestas estructuradas"
            ],
            "frontend": [
                "Usuario puede interactuar con interfaz gráfica",
                "Interfaz es responsive y accesible",
                "Sistema muestra feedback visual"
            ]
        }
        
        return feature_requirements.get(feature, [f"Funcionalidad básica de {feature}"])
    
    def _get_technical_requirements(self, features: List[str], project_type: str) -> List[str]:
        """Obtener requisitos técnicos"""
        requirements = [
            "Código debe ser mantenible y documentado",
            "Sistema debe usar control de versiones",
            "Aplicación debe ser containerizable"
        ]
        
        if "database" in features:
            requirements.append("Base de datos debe ser ACID compliant")
        
        if "api" in features:
            requirements.append("API debe seguir estándares REST")
        
        if "frontend" in features:
            requirements.append("Frontend debe ser compatible con navegadores modernos")
        
        return requirements
    
    def _get_non_functional_requirements(self, project_type: str) -> List[str]:
        """Obtener requisitos no funcionales"""
        return [
            "Sistema debe ser seguro contra ataques comunes",
            "Aplicación debe tener tiempo de respuesta < 2 segundos",
            "Sistema debe ser escalable horizontalmente",
            "Código debe tener cobertura de tests > 80%",
            "Aplicación debe tener logging estructurado"
        ]
    
    def _get_business_requirements(self, description_analysis: Dict[str, Any], features: List[str]) -> List[str]:
        """Obtener requisitos de negocio"""
        requirements = [
            "Sistema debe ser fácil de usar",
            "Aplicación debe reducir carga de trabajo manual"
        ]
        
        if description_analysis["complexity_indicators"]["saas"]:
            requirements.extend([
                "Sistema debe soportar multi-tenancy",
                "Aplicación debe tener modelo de subscripción"
            ])
        
        if "authentication" in features:
            requirements.append("Sistema debe proteger datos de usuarios")
        
        return requirements
    
    def _estimate_project_complexity(self, features: List[str], requirements: Dict[str, Any]) -> str:
        """Estimar complejidad del proyecto"""
        score = 0
        
        # Puntos por features
        score += len(features) * 2
        
        # Puntos por requisitos
        score += len(requirements.get("functional", [])) * 1
        score += len(requirements.get("technical", [])) * 1.5
        
        # Features complejas
        complex_features = ["authentication", "payment", "ai", "real_time"]
        score += sum(3 for feature in features if feature in complex_features)
        
        if score <= 10:
            return "low"
        elif score <= 25:
            return "medium"
        else:
            return "high"
    
    def _estimate_timeline(self, complexity: str) -> str:
        """Estimar timeline basado en complejidad"""
        timelines = {
            "low": "1-2 semanas",
            "medium": "1-2 meses", 
            "high": "3-6 meses"
        }
        return timelines.get(complexity, "2-4 semanas")
    
    def _estimate_team_size(self, complexity: str) -> str:
        """Estimar tamaño de equipo"""
        team_sizes = {
            "low": "1-2 desarrolladores",
            "medium": "2-4 desarrolladores",
            "high": "4-8 desarrolladores"
        }
        return team_sizes.get(complexity, "2-3 desarrolladores")
    
    def _select_architecture_pattern(self, complexity: str, features: List[str]) -> str:
        """Seleccionar patrón de arquitectura apropiado"""
        if complexity == "low":
            return "layered"
        elif len(features) > 8 or "microservices" in features:
            return "microservices"
        elif "real_time" in features:
            return "event_driven"
        else:
            return "layered"
    
    def _design_layers(self, pattern: str, features: List[str]) -> List[Dict[str, Any]]:
        """Diseñar capas de la arquitectura"""
        if pattern == "layered":
            return [
                {
                    "name": "presentation",
                    "description": "User interface and user experience",
                    "technologies": ["React", "Next.js", "HTML/CSS"],
                    "responsibilities": ["UI Components", "State Management", "User Interactions"]
                },
                {
                    "name": "business",
                    "description": "Business logic and application services",
                    "technologies": ["FastAPI", "Python", "Business Logic"],
                    "responsibilities": ["API Endpoints", "Business Rules", "Data Validation"]
                },
                {
                    "name": "data",
                    "description": "Data access and persistence",
                    "technologies": ["SQLAlchemy", "PostgreSQL", "Redis"],
                    "responsibilities": ["Data Models", "Database Operations", "Caching"]
                }
            ]
        else:
            return [{"name": pattern, "description": f"Architecture pattern: {pattern}"}]
    
    def _design_components(self, features: List[str], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Diseñar componentes principales"""
        components = []
        
        # Componente web frontend
        if "frontend" in features:
            components.append({
                "name": "web_frontend",
                "type": "frontend",
                "technology": "Next.js",
                "responsibilities": ["UI", "State Management", "API Integration"],
                "dependencies": ["api_server"]
            })
        
        # Componente API server
        if "api" in features or "backend" in features:
            components.append({
                "name": "api_server",
                "type": "backend",
                "technology": "FastAPI",
                "responsibilities": ["Business Logic", "API Endpoints", "Authentication"],
                "dependencies": ["database"] if "database" in features else []
            })
        
        # Componente base de datos
        if "database" in features:
            components.append({
                "name": "database",
                "type": "data",
                "technology": "PostgreSQL",
                "responsibilities": ["Data Storage", "Data Integrity", "Querying"],
                "dependencies": []
            })
        
        return components
    
    def _select_technologies(self, complexity: str, features: List[str]) -> Dict[str, str]:
        """Seleccionar stack tecnológico"""
        # Por ahora, usar stack Python por defecto
        tech_stack = {
            "backend_framework": "FastAPI",
            "backend_language": "Python",
            "frontend_framework": "Next.js",
            "frontend_language": "TypeScript",
            "database": "PostgreSQL",
            "deployment": "Docker",
            "ci_cd": "GitHub Actions"
        }
        
        # Ajustes basados en complejidad
        if complexity == "low":
            tech_stack["database"] = "SQLite"
            tech_stack["deployment"] = "Single Container"
        
        if "authentication" in features:
            tech_stack["auth"] = "JWT + OAuth2"
        
        return tech_stack
    
    def _design_communication(self, components: List[Dict[str, Any]], pattern: str) -> Dict[str, Any]:
        """Diseñar comunicación entre componentes"""
        return {
            "type": "REST API",
            "protocol": "HTTP/HTTPS",
            "format": "JSON",
            "authentication": "JWT tokens",
            "error_handling": "HTTP status codes + structured responses"
        }
    
    def _design_data_flow(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Diseñar flujo de datos"""
        flows = []
        
        # Si hay frontend y backend, crear flujo típico
        frontend = next((c for c in components if c["type"] == "frontend"), None)
        backend = next((c for c in components if c["type"] == "backend"), None)
        database = next((c for c in components if c["type"] == "data"), None)
        
        if frontend and backend:
            flows.append({
                "from": frontend["name"],
                "to": backend["name"],
                "type": "HTTP Request",
                "description": "User actions and data requests"
            })
        
        if backend and database:
            flows.append({
                "from": backend["name"],
                "to": database["name"],
                "type": "SQL Query",
                "description": "Data persistence and retrieval"
            })
        
        return flows
    
    def _design_security(self, features: List[str]) -> List[str]:
        """Diseñar consideraciones de seguridad"""
        security_measures = [
            "HTTPS enforcement",
            "CORS configuration",
            "Input validation and sanitization",
            "SQL injection prevention"
        ]
        
        if "authentication" in features:
            security_measures.extend([
                "Password hashing with bcrypt",
                "JWT token validation",
                "Session management"
            ])
        
        return security_measures
    
    def _design_scalability(self, complexity: str) -> List[str]:
        """Diseñar consideraciones de escalabilidad"""
        measures = [
            "Database connection pooling",
            "Containerized deployment",
            "Load balancer ready"
        ]
        
        if complexity == "high":
            measures.extend([
                "Horizontal scaling support",
                "Caching layer implementation",
                "Database read replicas"
            ])
        
        return measures
    
    def _generate_backend_structure(self, requirements: Dict[str, Any], features: List[str], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generar estructura del backend"""
        return {
            "framework": "FastAPI",
            "language": "Python",
            "models": self._generate_data_models(features),
            "endpoints": self._generate_api_endpoints(requirements, features),
            "services": self._generate_services(features),
            "middlewares": ["CORS", "Authentication", "Logging", "Error Handling"]
        }
    
    def _generate_frontend_structure(self, requirements: Dict[str, Any], features: List[str], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generar estructura del frontend"""
        return {
            "framework": "Next.js",
            "language": "TypeScript",
            "pages": self._generate_pages(features),
            "components": self._generate_ui_components(features),
            "state_management": "Redux Toolkit",
            "styling": "Tailwind CSS"
        }
    
    def _generate_database_structure(self, requirements: Dict[str, Any], features: List[str]) -> Dict[str, Any]:
        """Generar estructura de base de datos"""
        return {
            "type": "PostgreSQL",
            "tables": self._generate_database_tables(features),
            "relationships": self._generate_relationships(features),
            "indexes": self._generate_indexes(features),
            "migrations": "Alembic"
        }
    
    def _generate_deployment_structure(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generar estructura de deployment"""
        return {
            "containerization": "Docker",
            "orchestration": "Docker Compose",
            "ci_cd": "GitHub Actions",
            "environments": ["development", "staging", "production"],
            "monitoring": "Prometheus + Grafana"
        }
    
    def _generate_documentation_structure(self) -> Dict[str, Any]:
        """Generar estructura de documentación"""
        return {
            "api_docs": "OpenAPI/Swagger",
            "readme": "Project overview and setup",
            "contributing": "Development guidelines",
            "deployment": "Deployment instructions"
        }
    
    def _generate_entities(self, requirements: Dict[str, Any], features: List[str]) -> List[Dict[str, Any]]:
        """Generar entidades del dominio"""
        entities = []
        
        if "authentication" in features:
            entities.append({
                "name": "User",
                "description": "System user entity",
                "attributes": ["id", "email", "password_hash", "created_at", "updated_at"],
                "relationships": []
            })
        
        # Agregar más entidades basadas en features
        return entities
    
    def _generate_data_models(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar modelos de datos"""
        models = []
        
        if "authentication" in features:
            models.append({
                "name": "User",
                "table": "users",
                "fields": [
                    {"name": "id", "type": "UUID", "primary_key": True},
                    {"name": "email", "type": "String", "unique": True, "nullable": False},
                    {"name": "password_hash", "type": "String", "nullable": False},
                    {"name": "is_active", "type": "Boolean", "default": True},
                    {"name": "created_at", "type": "DateTime", "default": "now"},
                    {"name": "updated_at", "type": "DateTime", "default": "now", "onupdate": "now"}
                ]
            })
        
        return models
    
    def _generate_api_endpoints(self, requirements: Dict[str, Any], features: List[str]) -> List[Dict[str, Any]]:
        """Generar endpoints de la API"""
        endpoints = [
            {"method": "GET", "path": "/", "description": "Health check endpoint"},
            {"method": "GET", "path": "/health", "description": "Application health status"}
        ]
        
        if "authentication" in features:
            endpoints.extend([
                {"method": "POST", "path": "/api/v1/auth/register", "description": "User registration"},
                {"method": "POST", "path": "/api/v1/auth/login", "description": "User login"},
                {"method": "POST", "path": "/api/v1/auth/logout", "description": "User logout"},
                {"method": "GET", "path": "/api/v1/auth/me", "description": "Get current user"}
            ])
        
        return endpoints
    
    def _generate_services(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar servicios del backend"""
        services = []
        
        if "authentication" in features:
            services.append({
                "name": "AuthService",
                "description": "Handle user authentication and authorization",
                "methods": ["register", "login", "logout", "validate_token"]
            })
        
        return services
    
    def _generate_pages(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar páginas del frontend"""
        pages = [
            {"name": "Home", "path": "/", "description": "Landing page"},
            {"name": "About", "path": "/about", "description": "About page"}
        ]
        
        if "authentication" in features:
            pages.extend([
                {"name": "Login", "path": "/login", "description": "User login page"},
                {"name": "Register", "path": "/register", "description": "User registration page"},
                {"name": "Dashboard", "path": "/dashboard", "description": "User dashboard", "protected": True}
            ])
        
        return pages
    
    def _generate_ui_components(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar componentes UI"""
        components = [
            {"name": "Layout", "type": "layout", "description": "Main application layout"},
            {"name": "Header", "type": "navigation", "description": "Navigation header"},
            {"name": "Footer", "type": "layout", "description": "Application footer"}
        ]
        
        if "authentication" in features:
            components.extend([
                {"name": "LoginForm", "type": "form", "description": "User login form"},
                {"name": "RegisterForm", "type": "form", "description": "User registration form"},
                {"name": "UserProfile", "type": "display", "description": "User profile display"}
            ])
        
        return components
    
    def _generate_database_tables(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar tablas de base de datos"""
        tables = []
        
        if "authentication" in features:
            tables.append({
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY"]},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": ["UNIQUE", "NOT NULL"]},
                    {"name": "password_hash", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
                    {"name": "is_active", "type": "BOOLEAN", "constraints": ["DEFAULT TRUE"]},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": ["DEFAULT CURRENT_TIMESTAMP"]},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": ["DEFAULT CURRENT_TIMESTAMP"]}
                ]
            })
        
        return tables
    
    def _generate_relationships(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar relaciones entre tablas"""
        relationships = []
        # Por ahora retornar lista vacía, se expandirá según necesidades
        return relationships
    
    def _generate_indexes(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar índices de base de datos"""
        indexes = []
        
        if "authentication" in features:
            indexes.append({
                "table": "users",
                "columns": ["email"],
                "type": "unique",
                "name": "idx_users_email"
            })
        
        return indexes
    
    def _generate_workflows(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generar workflows de la aplicación"""
        workflows = []
        
        if "authentication" in features:
            workflows.append({
                "name": "user_registration",
                "steps": [
                    "User fills registration form",
                    "System validates input",
                    "System creates user account", 
                    "System sends confirmation email",
                    "User confirms account"
                ]
            })
        
        return workflows
    
    def _generate_dependencies(self, architecture: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generar dependencias del proyecto"""
        return {
            "backend": [
                "fastapi>=0.68.0",
                "uvicorn[standard]>=0.15.0",
                "sqlalchemy>=1.4.0",
                "alembic>=1.7.0",
                "psycopg2-binary>=2.9.0",
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.4",
                "python-multipart>=0.0.5"
            ],
            "frontend": [
                "next@latest",
                "react@^18.0.0",
                "typescript@^4.0.0",
                "@reduxjs/toolkit@^1.8.0",
                "tailwindcss@^3.0.0"
            ]
        }
    
    def _generate_configuration(self, architecture: Dict[str, Any], features: List[str]) -> Dict[str, Any]:
        """Generar configuración del proyecto"""
        config = {
            "environment_variables": {
                "DATABASE_URL": "Connection string for the database",
                "SECRET_KEY": "Secret key for JWT token signing"
            },
            "docker": {
                "base_images": {
                    "backend": "python:3.11-slim",
                    "frontend": "node:18-alpine"
                }
            }
        }
        
        if "authentication" in features:
            config["environment_variables"].update({
                "JWT_SECRET_KEY": "JWT secret key",
                "JWT_ALGORITHM": "HS256",
                "ACCESS_TOKEN_EXPIRE_MINUTES": "30"
            })
        
        return config
    
    # Métodos auxiliares adicionales
    
    def _assess_task_complexity(self, task: AgentTask) -> str:
        """Evaluar complejidad de una tarea"""
        param_count = len(task.params) if task.params else 0
        
        if param_count <= 2:
            return "low"
        elif param_count <= 5:
            return "medium"
        else:
            return "high"
    
    def _validate_layer_consistency(self, architecture: Dict[str, Any], result: Dict[str, Any]):
        """Validar consistencia entre capas"""
        layers = architecture.get("layers", [])
        if len(layers) < 2:
            result["warnings"].append("Arquitectura tiene pocas capas definidas")
    
    def _validate_component_dependencies(self, architecture: Dict[str, Any], result: Dict[str, Any]):
        """Validar dependencias entre componentes"""
        components = architecture.get("components", [])
        for component in components:
            deps = component.get("dependencies", [])
            for dep in deps:
                if not any(c["name"] == dep for c in components):
                    result["errors"].append(f"Componente {component['name']} depende de {dep} que no existe")
    
    def _validate_technology_compatibility(self, architecture: Dict[str, Any], result: Dict[str, Any]):
        """Validar compatibilidad de tecnologías"""
        technologies = architecture.get("technologies", {})
        
        # Validaciones básicas de compatibilidad
        if technologies.get("frontend_framework") == "React" and technologies.get("backend_framework") == "Django":
            result["suggestions"].append("Considerar usar Django REST Framework para mejor integración con React")
    
    def _validate_security_requirements(self, architecture: Dict[str, Any], requirements: Dict[str, Any], result: Dict[str, Any]):
        """Validar requisitos de seguridad"""
        security = architecture.get("security_considerations", [])
        
        if not security:
            result["warnings"].append("No se encontraron consideraciones de seguridad definidas")
        
        if "authentication" in str(requirements) and "JWT" not in str(security):
            result["suggestions"].append("Considerar implementar autenticación JWT")
    
    def _score_technology_stack(self, stack_config: Dict[str, str], features: List[str], complexity: str, constraints: List[str]) -> float:
        """Puntuar stack tecnológico"""
        score = 5.0  # Score base
        
        # Ajustar score basado en features
        if "authentication" in features and "FastAPI" in stack_config.get("backend", ""):
            score += 1.0
        
        # Ajustar por complejidad
        if complexity == "high" and "microservices" in str(stack_config).lower():
            score += 1.5
        
        # Ajustar por constraints
        for constraint in constraints:
            if constraint.lower() in str(stack_config).lower():
                score -= 0.5
        
        return min(10.0, max(0.0, score))
    
    def _get_stack_pros(self, stack_name: str, features: List[str]) -> List[str]:
        """Obtener ventajas de un stack"""
        return [
            "Bien documentado",
            "Comunidad activa",
            "Buena performance"
        ]
    
    def _get_stack_cons(self, stack_name: str, features: List[str]) -> List[str]:
        """Obtener desventajas de un stack"""
        return [
            "Curva de aprendizaje",
            "Dependencias externas"
        ]
    
    def _estimate_development_time(self, complexity_level: str) -> str:
        """Estimar tiempo de desarrollo"""
        times = {
            "low": "1-2 semanas",
            "medium": "1-2 meses",
            "high": "3-6 meses"
        }
        return times.get(complexity_level, "2-4 semanas")
    
    def _recommend_approach(self, complexity_level: str) -> str:
        """Recomendar enfoque de desarrollo"""
        approaches = {
            "low": "Desarrollo iterativo con MVP rápido",
            "medium": "Desarrollo ágil con sprints de 2 semanas",
            "high": "Arquitectura modular con equipos especializados"
        }
        return approaches.get(complexity_level, "Desarrollo iterativo")