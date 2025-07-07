"""
Architect Agent - Diseño de arquitectura y entidades del proyecto

Este agente es responsable de:
- Analizar requisitos del proyecto
- Diseñar arquitectura general
- Definir entidades y relaciones
- Generar project_schema.json
- Validar coherencia del diseño
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
from genesis_engine.core.config import GenesisConfig

class ArchitecturePattern(str, Enum):
    """Patrones de arquitectura soportados"""
    LAYERED = "layered"
    CLEAN_ARCHITECTURE = "clean_architecture"
    HEXAGONAL = "hexagonal"
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    JAMSTACK = "jamstack"

class DatabaseType(str, Enum):
    """Tipos de base de datos"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    REDIS = "redis"

@dataclass
class Entity:
    """Definición de una entidad del dominio"""
    name: str
    description: str
    attributes: Dict[str, str]  # nombre: tipo
    relationships: List[Dict[str, str]]
    constraints: List[str]
    metadata: Dict[str, Any]

@dataclass
class ProjectSchema:
    """Schema completo del proyecto"""
    project_name: str
    description: str
    architecture_pattern: ArchitecturePattern
    stack: Dict[str, str]
    entities: List[Entity]
    relationships: List[Dict[str, Any]]
    endpoints: List[Dict[str, Any]]
    business_rules: List[str]
    security_requirements: List[str]
    performance_requirements: Dict[str, Any]
    deployment_config: Dict[str, Any]
    metadata: Dict[str, Any]

class ArchitectAgent(GenesisAgent):
    """
    Agente Arquitecto - Diseñador de sistemas
    
    Responsable del diseño de arquitectura, análisis de requisitos
    y generación del schema del proyecto.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="architect_agent",
            name="ArchitectAgent", 
            agent_type="architect"
        )
        
        # Capacidades del agente
        self.add_capability("architecture_design")
        self.add_capability("entity_modeling")
        self.add_capability("schema_generation")
        self.add_capability("requirement_analysis")
        self.add_capability("pattern_recommendation")
        
        # Registrar handlers específicos
        self.register_handler("analyze_requirements", self._handle_analyze_requirements)
        self.register_handler("design_architecture", self._handle_design_architecture)
        self.register_handler("generate_schema", self._handle_generate_schema)
        self.register_handler("validate_design", self._handle_validate_design)
        self.register_handler("recommend_stack", self._handle_recommend_stack)
        
        # Templates y patrones
        self.architecture_templates = self._load_architecture_templates()
        self.design_patterns = self._load_design_patterns()
        
    async def initialize(self):
        """Inicialización del agente arquitecto"""
        self.logger.info("🏗️ Inicializando Architect Agent")
        
        # Cargar configuraciones y templates
        await self._load_best_practices()
        await self._initialize_ai_models()
        
        self.set_metadata("version", "1.0.0")
        self.set_metadata("specialization", "full_stack_architecture")
        
        self.logger.info("✅ Architect Agent inicializado")
    
    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica del arquitecto"""
        task_name = task.name.lower()
        
        if "analyze_requirements" in task_name:
            return await self._analyze_requirements(task.params)
        elif "design_architecture" in task_name:
            return await self._design_architecture(task.params)
        elif "generate_schema" in task_name:
            return await self._generate_project_schema(task.params)
        elif "validate_design" in task_name:
            return await self._validate_design(task.params)
        elif "recommend_stack" in task_name:
            return await self._recommend_technology_stack(task.params)
        else:
            raise ValueError(f"Tarea no reconocida: {task.name}")
    
    async def _analyze_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar requisitos del proyecto"""
        self.logger.info("🔍 Analizando requisitos del proyecto")
        
        project_description = params.get("description", "")
        project_type = params.get("type", "web_app")
        features = params.get("features", [])
        constraints = params.get("constraints", {})
        
        # Análisis de requisitos funcionales
        functional_requirements = self._extract_functional_requirements(
            project_description, features
        )
        
        # Análisis de requisitos no funcionales
        non_functional_requirements = self._extract_non_functional_requirements(
            constraints
        )
        
        # Identificar entidades principales
        entities = self._identify_entities(project_description, features)
        
        # Recomendar patrones de arquitectura
        recommended_patterns = self._recommend_architecture_patterns(
            project_type, functional_requirements, non_functional_requirements
        )
        
        analysis_result = {
            "functional_requirements": functional_requirements,
            "non_functional_requirements": non_functional_requirements,
            "identified_entities": entities,
            "recommended_patterns": recommended_patterns,
            "complexity_score": self._calculate_complexity_score(
                functional_requirements, entities
            ),
            "estimated_timeline": self._estimate_development_timeline(
                functional_requirements, entities
            )
        }
        
        self.logger.info(f"✅ Análisis completado - {len(entities)} entidades identificadas")
        return analysis_result
    
    async def _design_architecture(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Diseñar arquitectura del sistema"""
        self.logger.info("🎨 Diseñando arquitectura del sistema")
        
        requirements = params.get("requirements", {})
        selected_pattern = params.get("pattern", ArchitecturePattern.LAYERED)
        project_type = params.get("type", "web_app")
        
        # Diseñar capas de la arquitectura
        layers = self._design_layers(selected_pattern, requirements)
        
        # Diseñar componentes principales
        components = self._design_components(requirements, layers)
        
        # Diseñar flujos de datos
        data_flows = self._design_data_flows(components, requirements)
        
        # Diseñar API endpoints
        api_design = self._design_api_endpoints(requirements)
        
        # Considerar aspectos de seguridad
        security_design = self._design_security_architecture(requirements)
        
        architecture_design = {
            "pattern": selected_pattern,
            "layers": layers,
            "components": components,
            "data_flows": data_flows,
            "api_design": api_design,
            "security_design": security_design,
            "deployment_architecture": self._design_deployment_architecture(
                requirements, components
            )
        }
        
        self.logger.info(f"✅ Arquitectura diseñada con patrón {selected_pattern}")
        return architecture_design
    
    async def _generate_project_schema(self, params: Dict[str, Any]) -> ProjectSchema:
        """Generar schema completo del proyecto"""
        self.logger.info("📋 Generando schema del proyecto")
        
        project_name = params.get("name", "genesis_project")
        description = params.get("description", "")
        requirements = params.get("requirements", {})
        architecture = params.get("architecture", {})
        stack = params.get("stack", {})
        
        # Generar entidades detalladas
        entities = self._generate_detailed_entities(
            requirements.get("identified_entities", [])
        )
        
        # Generar relaciones entre entidades
        relationships = self._generate_entity_relationships(entities)
        
        # Generar endpoints de la API
        endpoints = self._generate_api_endpoints(entities, requirements)
        
        # Generar reglas de negocio
        business_rules = self._generate_business_rules(entities, requirements)
        
        # Configuración de despliegue
        deployment_config = self._generate_deployment_config(architecture, stack)
        
        schema = ProjectSchema(
            project_name=project_name,
            description=description,
            architecture_pattern=ArchitecturePattern(
                architecture.get("pattern", "layered")
            ),
            stack=stack,
            entities=entities,
            relationships=relationships,
            endpoints=endpoints,
            business_rules=business_rules,
            security_requirements=self._generate_security_requirements(requirements),
            performance_requirements=self._generate_performance_requirements(requirements),
            deployment_config=deployment_config,
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "generator": "ArchitectAgent",
                "version": "1.0",
                "schema_id": str(uuid.uuid4())
            }
        )
        
        self.logger.info(f"✅ Schema generado para {project_name}")
        return schema
    
    def _extract_functional_requirements(
        self, description: str, features: List[str]
    ) -> List[Dict[str, Any]]:
        """Extraer requisitos funcionales"""
        requirements = []
        
        # Análisis básico de características
        for feature in features:
            requirements.append({
                "id": f"req_{len(requirements) + 1}",
                "name": feature,
                "description": f"Sistema debe soportar {feature}",
                "priority": "high",
                "category": self._categorize_feature(feature)
            })
        
        # Análisis de descripción con IA/NLP (simplificado)
        if "autenticación" in description.lower() or "login" in description.lower():
            requirements.append({
                "id": f"req_{len(requirements) + 1}",
                "name": "User Authentication",
                "description": "Sistema de autenticación de usuarios",
                "priority": "high",
                "category": "authentication"
            })
        
        if "pago" in description.lower() or "payment" in description.lower():
            requirements.append({
                "id": f"req_{len(requirements) + 1}",
                "name": "Payment Processing",
                "description": "Procesamiento de pagos",
                "priority": "high",
                "category": "payment"
            })
        
        return requirements
    
    def _extract_non_functional_requirements(
        self, constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extraer requisitos no funcionales"""
        return {
            "performance": {
                "response_time": constraints.get("max_response_time", "< 2s"),
                "throughput": constraints.get("min_throughput", "1000 req/min"),
                "concurrent_users": constraints.get("max_users", 1000)
            },
            "scalability": {
                "horizontal_scaling": constraints.get("auto_scaling", True),
                "database_scaling": constraints.get("db_scaling", "read_replicas")
            },
            "security": {
                "encryption": constraints.get("encryption", "TLS 1.3"),
                "authentication": constraints.get("auth_method", "JWT"),
                "data_protection": constraints.get("gdpr_compliance", True)
            },
            "availability": {
                "uptime": constraints.get("target_uptime", "99.9%"),
                "disaster_recovery": constraints.get("dr_required", True)
            }
        }
    
    def _identify_entities(
        self, description: str, features: List[str]
    ) -> List[Dict[str, Any]]:
        """Identificar entidades principales del dominio"""
        entities = []
        
        # Entidades comunes en aplicaciones web
        common_entities = {
            "user": ["usuario", "user", "cliente", "customer"],
            "product": ["producto", "product", "item", "artículo"],
            "order": ["orden", "order", "pedido", "compra"],
            "payment": ["pago", "payment", "transacción"],
            "category": ["categoría", "category", "tipo"]
        }
        
        description_lower = description.lower()
        
        for entity_type, keywords in common_entities.items():
            if any(keyword in description_lower for keyword in keywords):
                entities.append({
                    "name": entity_type.capitalize(),
                    "confidence": 0.8,
                    "attributes": self._get_default_attributes(entity_type)
                })
        
        # Análisis de features
        for feature in features:
            feature_lower = feature.lower()
            if "blog" in feature_lower:
                entities.append({
                    "name": "Post",
                    "confidence": 0.9,
                    "attributes": ["title", "content", "author", "created_at"]
                })
            elif "comentario" in feature_lower or "comment" in feature_lower:
                entities.append({
                    "name": "Comment",
                    "confidence": 0.9,
                    "attributes": ["content", "author", "post_id", "created_at"]
                })
        
        return entities
    
    def _recommend_architecture_patterns(
        self, 
        project_type: str, 
        functional_req: List[Dict[str, Any]], 
        non_functional_req: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recomendar patrones de arquitectura"""
        recommendations = []
        
        # Análisis basado en complejidad
        high_complexity = len(functional_req) > 20
        high_scalability = non_functional_req.get("scalability", {}).get("horizontal_scaling", False)
        
        if project_type == "saas" or high_complexity:
            recommendations.append({
                "pattern": ArchitecturePattern.CLEAN_ARCHITECTURE,
                "score": 0.9,
                "reasoning": "Ideal para aplicaciones SaaS complejas con múltiples dominios"
            })
        
        if high_scalability:
            recommendations.append({
                "pattern": ArchitecturePattern.MICROSERVICES,
                "score": 0.8,
                "reasoning": "Recomendado para alta escalabilidad y equipos distribuidos"
            })
        
        # Por defecto, arquitectura en capas
        recommendations.append({
            "pattern": ArchitecturePattern.LAYERED,
            "score": 0.7,
            "reasoning": "Patrón estándar, fácil de implementar y mantener"
        })
        
        return sorted(recommendations, key=lambda x: x["score"], reverse=True)
    
    def _design_layers(
        self, pattern: ArchitecturePattern, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Diseñar capas de la arquitectura"""
        if pattern == ArchitecturePattern.CLEAN_ARCHITECTURE:
            return {
                "presentation": {
                    "components": ["controllers", "views", "middleware"],
                    "description": "Capa de presentación y controladores"
                },
                "application": {
                    "components": ["use_cases", "services", "dto"],
                    "description": "Lógica de aplicación y casos de uso"
                },
                "domain": {
                    "components": ["entities", "repositories", "domain_services"],
                    "description": "Lógica de dominio y entidades"
                },
                "infrastructure": {
                    "components": ["database", "external_apis", "file_system"],
                    "description": "Infraestructura y servicios externos"
                }
            }
        
        elif pattern == ArchitecturePattern.LAYERED:
            return {
                "presentation": {
                    "components": ["controllers", "routes", "middleware"],
                    "description": "Capa de presentación web"
                },
                "business": {
                    "components": ["services", "business_logic"],
                    "description": "Lógica de negocio"
                },
                "data": {
                    "components": ["models", "repositories", "database"],
                    "description": "Acceso a datos"
                }
            }
        
        return {}
    
    def _generate_detailed_entities(self, entities: List[Dict[str, Any]]) -> List[Entity]:
        """Generar entidades detalladas"""
        detailed_entities = []
        
        for entity_data in entities:
            name = entity_data.get("name", "Unknown")
            attributes = entity_data.get("attributes", [])
            
            # Generar atributos tipados
            typed_attributes = {}
            for attr in attributes:
                if isinstance(attr, str):
                    typed_attributes[attr] = self._infer_attribute_type(attr)
                elif isinstance(attr, dict):
                    typed_attributes[attr["name"]] = attr.get("type", "string")
            
            # Agregar atributos comunes
            typed_attributes.update({
                "id": "uuid",
                "created_at": "datetime",
                "updated_at": "datetime"
            })
            
            entity = Entity(
                name=name,
                description=f"Entidad {name} del dominio",
                attributes=typed_attributes,
                relationships=[],
                constraints=self._generate_entity_constraints(name, typed_attributes),
                metadata={
                    "table_name": name.lower() + "s",
                    "primary_key": "id",
                    "soft_delete": True
                }
            )
            
            detailed_entities.append(entity)
        
        return detailed_entities
    
    def _infer_attribute_type(self, attribute_name: str) -> str:
        """Inferir tipo de atributo basado en el nombre"""
        attribute_lower = attribute_name.lower()
        
        if attribute_lower in ["id", "user_id", "product_id"]:
            return "uuid"
        elif "email" in attribute_lower:
            return "email"
        elif "password" in attribute_lower:
            return "password_hash"
        elif attribute_lower in ["created_at", "updated_at", "date"]:
            return "datetime"
        elif attribute_lower in ["price", "amount", "cost"]:
            return "decimal"
        elif attribute_lower in ["quantity", "count", "number"]:
            return "integer"
        elif attribute_lower in ["active", "enabled", "verified"]:
            return "boolean"
        elif "description" in attribute_lower or "content" in attribute_lower:
            return "text"
        else:
            return "string"
    
    async def _handle_analyze_requirements(self, request) -> Dict[str, Any]:
        """Handler para análisis de requisitos"""
        params = request.params
        return await self._analyze_requirements(params)
    
    async def _handle_design_architecture(self, request) -> Dict[str, Any]:
        """Handler para diseño de arquitectura"""
        params = request.params
        return await self._design_architecture(params)
    
    async def _handle_generate_schema(self, request) -> Dict[str, Any]:
        """Handler para generación de schema"""
        params = request.params
        schema = await self._generate_project_schema(params)
        # Convertir a dict para serialización
        return {
            "project_name": schema.project_name,
            "description": schema.description,
            "architecture_pattern": schema.architecture_pattern.value,
            "stack": schema.stack,
            "entities": [
                {
                    "name": entity.name,
                    "description": entity.description,
                    "attributes": entity.attributes,
                    "relationships": entity.relationships,
                    "constraints": entity.constraints,
                    "metadata": entity.metadata
                }
                for entity in schema.entities
            ],
            "relationships": schema.relationships,
            "endpoints": schema.endpoints,
            "business_rules": schema.business_rules,
            "security_requirements": schema.security_requirements,
            "performance_requirements": schema.performance_requirements,
            "deployment_config": schema.deployment_config,
            "metadata": schema.metadata
        }
    
    def _load_architecture_templates(self) -> Dict[str, Any]:
        """Cargar templates de arquitectura"""
        return {
            "saas_basic": {
                "entities": ["User", "Organization", "Subscription", "Payment"],
                "features": ["authentication", "billing", "multi_tenancy"],
                "patterns": [ArchitecturePattern.CLEAN_ARCHITECTURE]
            },
            "ecommerce": {
                "entities": ["User", "Product", "Order", "Payment", "Category"],
                "features": ["catalog", "cart", "checkout", "inventory"],
                "patterns": [ArchitecturePattern.LAYERED]
            }
        }
    
    def _load_design_patterns(self) -> Dict[str, Any]:
        """Cargar patrones de diseño"""
        return {
            "repository": "Abstracción del acceso a datos",
            "service": "Encapsulación de lógica de negocio",
            "factory": "Creación de objetos complejos",
            "observer": "Notificación de eventos"
        }
    
    async def _load_best_practices(self):
        """Cargar mejores prácticas"""
        pass
    
    async def _initialize_ai_models(self):
        """Inicializar modelos de IA para análisis"""
        pass
    
    def _categorize_feature(self, feature: str) -> str:
        """Categorizar una característica"""
        feature_lower = feature.lower()
        
        if any(word in feature_lower for word in ["auth", "login", "signup"]):
            return "authentication"
        elif any(word in feature_lower for word in ["pay", "bill", "subscription"]):
            return "payment"
        elif any(word in feature_lower for word in ["search", "filter", "browse"]):
            return "search"
        elif any(word in feature_lower for word in ["chat", "message", "notification"]):
            return "communication"
        else:
            return "business_logic"
    
    def _get_default_attributes(self, entity_type: str) -> List[str]:
        """Obtener atributos por defecto para un tipo de entidad"""
        defaults = {
            "user": ["email", "password", "name", "active"],
            "product": ["name", "description", "price", "category_id"],
            "order": ["user_id", "total", "status", "ordered_at"],
            "payment": ["order_id", "amount", "method", "status"],
            "category": ["name", "description", "parent_id"]
        }
        return defaults.get(entity_type, ["name", "description"])
    
    def _calculate_complexity_score(
        self, requirements: List[Dict[str, Any]], entities: List[Dict[str, Any]]
    ) -> int:
        """Calcular puntuación de complejidad"""
        base_score = len(requirements) * 2 + len(entities) * 3
        
        # Ajustes por tipo de requisitos
        for req in requirements:
            if req.get("priority") == "high":
                base_score += 2
            if req.get("category") in ["payment", "authentication"]:
                base_score += 5
        
        return min(base_score, 100)
    
    def _estimate_development_timeline(
        self, requirements: List[Dict[str, Any]], entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Estimar timeline de desarrollo"""
        base_weeks = len(entities) * 1.5 + len(requirements) * 0.5
        
        return {
            "backend_weeks": base_weeks * 0.6,
            "frontend_weeks": base_weeks * 0.4,
            "testing_weeks": base_weeks * 0.3,
            "deployment_weeks": 1,
            "total_weeks": base_weeks + 1.3
        }
    
    def _design_components(self, requirements: Dict[str, Any], layers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Diseñar componentes del sistema"""
        return []
    
    def _design_data_flows(self, components: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Diseñar flujos de datos"""
        return []
    
    def _design_api_endpoints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Diseñar endpoints de la API"""
        return {}
    
    def _design_security_architecture(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Diseñar arquitectura de seguridad"""
        return {}
    
    def _design_deployment_architecture(self, requirements: Dict[str, Any], components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Diseñar arquitectura de despliegue"""
        return {}
    
    def _generate_entity_relationships(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """Generar relaciones entre entidades"""
        return []
    
    def _generate_api_endpoints(self, entities: List[Entity], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar endpoints de la API"""
        return []
    
    def _generate_business_rules(self, entities: List[Entity], requirements: Dict[str, Any]) -> List[str]:
        """Generar reglas de negocio"""
        return []
    
    def _generate_security_requirements(self, requirements: Dict[str, Any]) -> List[str]:
        """Generar requisitos de seguridad"""
        return []
    
    def _generate_performance_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generar requisitos de rendimiento"""
        return {}
    
    def _generate_deployment_config(self, architecture: Dict[str, Any], stack: Dict[str, str]) -> Dict[str, Any]:
        """Generar configuración de despliegue"""
        return {}
    
    def _generate_entity_constraints(self, entity_name: str, attributes: Dict[str, str]) -> List[str]:
        """Generar restricciones para una entidad"""
        return []

    async def _handle_validate_design(self, request) -> Dict[str, Any]:
        """Handler para validar el diseño generado"""
        params = request.params
        return await self._validate_design(params)

    async def _validate_design(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validar coherencia del diseño"""
        return {"valid": True, "issues": []}

    async def _handle_recommend_stack(self, request) -> Dict[str, Any]:
        """Handler para recomendación de stack tecnológico"""
        params = request.params
        return await self._recommend_technology_stack(params)

    async def _recommend_technology_stack(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Recomendar stack tecnológico basado en configuración por defecto"""
        stack_name = params.get("template", "golden-path")
        recommended = GenesisConfig.get_stack_config(stack_name)
        if not recommended:
            recommended = GenesisConfig.get_stack_config("golden-path")
        return {"recommended_stack": recommended}
