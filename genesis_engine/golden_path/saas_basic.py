"""
Golden Path - SaaS Básico

El Golden Path es el flujo predefinido de Genesis Engine para crear
aplicaciones SaaS completas usando el stack tecnológico recomendado:

Backend: Python FastAPI + SQLAlchemy + PostgreSQL
Frontend: Next.js + TypeScript + Tailwind CSS + Redux Toolkit  
DevOps: Docker + GitHub Actions
Deploy: Local automático con opción de cloud

Este módulo define:
- Schema predefinido para aplicación SaaS
- Configuración del stack tecnológico
- Flujo de trabajo optimizado
- Plantillas especializadas
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from genesis_engine.agents.architect import ProjectSchema, Entity, ArchitecturePattern

@dataclass
class SaaSEntity:
    """Entidad predefinida para SaaS"""
    name: str
    description: str
    attributes: Dict[str, str]
    relationships: List[Dict[str, str]]
    is_core: bool = True
    generate_crud: bool = True
    
class GoldenPathSaaS:
    """
    Golden Path para aplicaciones SaaS básicas
    
    Proporciona un flujo predefinido y optimizado para crear
    aplicaciones SaaS completas con todas las funcionalidades
    estándar incluidas.
    """
    
    def __init__(self):
        self.name = "SaaS Básico"
        self.description = "Aplicación SaaS completa con autenticación, billing y multi-tenancy"
        self.version = "1.0.0"
        
        # Stack tecnológico predefinido
        self.default_stack = {
            "backend": "fastapi",
            "frontend": "nextjs", 
            "database": "postgresql",
            "state_management": "redux_toolkit",
            "styling": "tailwind",
            "auth": "jwt",
            "ui_components": "shadcn",
            "typescript": True,
            "docker": True,
            "ci_cd": "github_actions"
        }
        
        # Características incluidas
        self.included_features = [
            "user_authentication",
            "user_management", 
            "organization_management",
            "subscription_billing",
            "payment_processing",
            "email_notifications",
            "audit_logging",
            "api_documentation",
            "admin_dashboard",
            "user_dashboard",
            "responsive_design",
            "dark_mode",
            "multi_language",
            "search_functionality"
        ]
        
        # Entidades predefinidas
        self.saas_entities = self._define_saas_entities()
    
    def _define_saas_entities(self) -> List[SaaSEntity]:
        """Definir entidades para SaaS básico"""
        return [
            # Usuario
            SaaSEntity(
                name="User",
                description="Usuario del sistema con autenticación y perfil",
                attributes={
                    "email": "email",
                    "password_hash": "password_hash", 
                    "first_name": "string",
                    "last_name": "string",
                    "avatar_url": "string",
                    "phone": "string",
                    "timezone": "string",
                    "locale": "string",
                    "is_active": "boolean",
                    "is_verified": "boolean",
                    "last_login": "datetime",
                    "login_count": "integer"
                },
                relationships=[
                    {"type": "belongs_to", "entity": "Organization", "name": "organization"},
                    {"type": "has_many", "entity": "UserSession", "name": "sessions"},
                    {"type": "has_many", "entity": "AuditLog", "name": "audit_logs"}
                ],
                is_core=True,
                generate_crud=True
            ),
            
            # Organización/Tenant
            SaaSEntity(
                name="Organization",
                description="Organización para multi-tenancy",
                attributes={
                    "name": "string",
                    "slug": "string",
                    "description": "text",
                    "website": "string",
                    "logo_url": "string",
                    "industry": "string",
                    "size": "string",
                    "country": "string",
                    "timezone": "string",
                    "is_active": "boolean",
                    "settings": "json"
                },
                relationships=[
                    {"type": "has_many", "entity": "User", "name": "users"},
                    {"type": "has_many", "entity": "Subscription", "name": "subscriptions"},
                    {"type": "has_many", "entity": "Invoice", "name": "invoices"}
                ],
                is_core=True,
                generate_crud=True
            ),
            
            # Suscripción
            SaaSEntity(
                name="Subscription",
                description="Suscripción de billing para organizaciones",
                attributes={
                    "plan_name": "string",
                    "plan_type": "string", # free, basic, premium, enterprise
                    "status": "string", # active, cancelled, past_due, incomplete
                    "current_period_start": "datetime",
                    "current_period_end": "datetime",
                    "trial_start": "datetime",
                    "trial_end": "datetime",
                    "billing_cycle": "string", # monthly, yearly
                    "amount": "decimal",
                    "currency": "string",
                    "stripe_subscription_id": "string",
                    "stripe_customer_id": "string",
                    "auto_renew": "boolean",
                    "features": "json"
                },
                relationships=[
                    {"type": "belongs_to", "entity": "Organization", "name": "organization"},
                    {"type": "has_many", "entity": "Invoice", "name": "invoices"},
                    {"type": "has_many", "entity": "Usage", "name": "usage_records"}
                ],
                is_core=True,
                generate_crud=True
            ),
            
            # Facturación
            SaaSEntity(
                name="Invoice",
                description="Facturas y pagos",
                attributes={
                    "invoice_number": "string",
                    "status": "string", # draft, sent, paid, failed, cancelled
                    "amount_total": "decimal",
                    "amount_paid": "decimal",
                    "currency": "string",
                    "due_date": "datetime",
                    "paid_date": "datetime",
                    "description": "text",
                    "line_items": "json",
                    "stripe_invoice_id": "string",
                    "stripe_charge_id": "string",
                    "payment_method": "string",
                    "billing_address": "json",
                    "tax_amount": "decimal",
                    "discount_amount": "decimal"
                },
                relationships=[
                    {"type": "belongs_to", "entity": "Organization", "name": "organization"},
                    {"type": "belongs_to", "entity": "Subscription", "name": "subscription"}
                ],
                is_core=True,
                generate_crud=True
            ),
            
            # Uso/Métricas
            SaaSEntity(
                name="Usage",
                description="Registro de uso para billing por consumo",
                attributes={
                    "metric_name": "string", # api_calls, storage_gb, users_count
                    "quantity": "decimal",
                    "unit": "string",
                    "timestamp": "datetime",
                    "period_start": "datetime",
                    "period_end": "datetime",
                    "metadata": "json"
                },
                relationships=[
                    {"type": "belongs_to", "entity": "Organization", "name": "organization"},
                    {"type": "belongs_to", "entity": "Subscription", "name": "subscription"}
                ],
                is_core=False,
                generate_crud=True
            ),
            
            # Sesiones de usuario
            SaaSEntity(
                name="UserSession",
                description="Sesiones activas de usuarios",
                attributes={
                    "session_token": "string",
                    "ip_address": "string",
                    "user_agent": "string",
                    "device_type": "string",
                    "location": "string",
                    "is_active": "boolean",
                    "expires_at": "datetime",
                    "last_activity": "datetime"
                },
                relationships=[
                    {"type": "belongs_to", "entity": "User", "name": "user"}
                ],
                is_core=False,
                generate_crud=False
            ),
            
            # Auditoría
            SaaSEntity(
                name="AuditLog",
                description="Registro de auditoría de acciones",
                attributes={
                    "action": "string",
                    "resource_type": "string",
                    "resource_id": "string",
                    "ip_address": "string",
                    "user_agent": "string",
                    "changes": "json",
                    "metadata": "json"
                },
                relationships=[
                    {"type": "belongs_to", "entity": "User", "name": "user"},
                    {"type": "belongs_to", "entity": "Organization", "name": "organization"}
                ],
                is_core=False,
                generate_crud=False
            ),
            
            # Notificaciones
            SaaSEntity(
                name="Notification",
                description="Notificaciones para usuarios",
                attributes={
                    "title": "string",
                    "message": "text",
                    "type": "string", # info, success, warning, error
                    "channel": "string", # email, sms, push, in_app
                    "is_read": "boolean",
                    "read_at": "datetime",
                    "sent_at": "datetime",
                    "metadata": "json"
                },
                relationships=[
                    {"type": "belongs_to", "entity": "User", "name": "user"}
                ],
                is_core=False,
                generate_crud=True
            )
        ]
    
    def generate_project_schema(
        self, 
        project_name: str, 
        description: str = None,
        custom_stack: Dict[str, Any] = None
    ) -> ProjectSchema:
        """
        Generar schema completo del proyecto SaaS
        
        Args:
            project_name: Nombre del proyecto
            description: Descripción personalizada
            custom_stack: Stack personalizado (opcional)
            
        Returns:
            Schema completo del proyecto
        """
        
        # Usar stack personalizado o por defecto
        stack = {**self.default_stack, **(custom_stack or {})}
        
        # Convertir entidades SaaS a entidades de arquitectura
        entities = []
        for saas_entity in self.saas_entities:
            entity = Entity(
                name=saas_entity.name,
                description=saas_entity.description,
                attributes=saas_entity.attributes,
                relationships=saas_entity.relationships,
                constraints=self._generate_entity_constraints(saas_entity),
                metadata={
                    "table_name": saas_entity.name.lower() + "s",
                    "primary_key": "id",
                    "soft_delete": True,
                    "is_core": saas_entity.is_core,
                    "generate_crud": saas_entity.generate_crud,
                    "audit_enabled": True
                }
            )
            entities.append(entity)
        
        # Generar relaciones entre entidades
        relationships = self._generate_entity_relationships(entities)
        
        # Generar endpoints API
        endpoints = self._generate_api_endpoints(entities)
        
        # Reglas de negocio
        business_rules = self._generate_business_rules()
        
        # Requisitos de seguridad
        security_requirements = self._generate_security_requirements()
        
        # Requisitos de rendimiento
        performance_requirements = self._generate_performance_requirements()
        
        # Configuración de despliegue
        deployment_config = self._generate_deployment_config(stack)
        
        return ProjectSchema(
            project_name=project_name,
            description=description or self.description,
            architecture_pattern=ArchitecturePattern.CLEAN_ARCHITECTURE,
            stack=stack,
            entities=entities,
            relationships=relationships,
            endpoints=endpoints,
            business_rules=business_rules,
            security_requirements=security_requirements,
            performance_requirements=performance_requirements,
            deployment_config=deployment_config,
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "generator": "Genesis Engine - Golden Path SaaS",
                "version": self.version,
                "template": "saas_basic",
                "features": self.included_features,
                "entities_count": len(entities),
                "core_entities": [e.name for e in entities if e.metadata.get("is_core")]
            }
        )
    
    def _generate_entity_constraints(self, entity: SaaSEntity) -> List[str]:
        """Generar restricciones para una entidad"""
        constraints = []
        
        # Restricciones comunes
        constraints.extend([
            "NOT NULL id",
            "NOT NULL created_at",
            "NOT NULL updated_at"
        ])
        
        # Restricciones específicas por entidad
        if entity.name == "User":
            constraints.extend([
                "UNIQUE email",
                "NOT NULL email",
                "CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')",
                "NOT NULL password_hash",
                "NOT NULL first_name",
                "NOT NULL last_name"
            ])
        elif entity.name == "Organization":
            constraints.extend([
                "UNIQUE slug",
                "NOT NULL name",
                "NOT NULL slug",
                "CHECK (length(slug) >= 3)",
                "CHECK (slug ~ '^[a-z0-9-]+$')"
            ])
        elif entity.name == "Subscription":
            constraints.extend([
                "NOT NULL plan_name",
                "NOT NULL status",
                "CHECK (status IN ('active', 'cancelled', 'past_due', 'incomplete'))",
                "CHECK (amount >= 0)",
                "CHECK (current_period_end > current_period_start)"
            ])
        elif entity.name == "Invoice":
            constraints.extend([
                "UNIQUE invoice_number",
                "NOT NULL invoice_number",
                "NOT NULL status",
                "CHECK (status IN ('draft', 'sent', 'paid', 'failed', 'cancelled'))",
                "CHECK (amount_total >= 0)",
                "CHECK (amount_paid >= 0)",
                "CHECK (amount_paid <= amount_total)"
            ])
        
        return constraints
    
    def _generate_entity_relationships(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """Generar relaciones entre entidades"""
        relationships = [
            {
                "from": "User",
                "to": "Organization", 
                "type": "many_to_one",
                "foreign_key": "organization_id",
                "description": "Usuario pertenece a una organización"
            },
            {
                "from": "Subscription",
                "to": "Organization",
                "type": "many_to_one", 
                "foreign_key": "organization_id",
                "description": "Suscripción pertenece a una organización"
            },
            {
                "from": "Invoice",
                "to": "Organization",
                "type": "many_to_one",
                "foreign_key": "organization_id", 
                "description": "Factura pertenece a una organización"
            },
            {
                "from": "Invoice",
                "to": "Subscription",
                "type": "many_to_one",
                "foreign_key": "subscription_id",
                "description": "Factura pertenece a una suscripción"
            },
            {
                "from": "Usage",
                "to": "Organization",
                "type": "many_to_one",
                "foreign_key": "organization_id",
                "description": "Registro de uso pertenece a una organización"
            },
            {
                "from": "Usage", 
                "to": "Subscription",
                "type": "many_to_one",
                "foreign_key": "subscription_id",
                "description": "Registro de uso pertenece a una suscripción"
            },
            {
                "from": "UserSession",
                "to": "User",
                "type": "many_to_one",
                "foreign_key": "user_id",
                "description": "Sesión pertenece a un usuario"
            },
            {
                "from": "AuditLog",
                "to": "User",
                "type": "many_to_one",
                "foreign_key": "user_id",
                "description": "Log de auditoría pertenece a un usuario"
            },
            {
                "from": "AuditLog",
                "to": "Organization",
                "type": "many_to_one",
                "foreign_key": "organization_id",
                "description": "Log de auditoría pertenece a una organización"
            },
            {
                "from": "Notification",
                "to": "User",
                "type": "many_to_one",
                "foreign_key": "user_id",
                "description": "Notificación pertenece a un usuario"
            }
        ]
        
        return relationships
    
    def _generate_api_endpoints(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """Generar endpoints API para las entidades"""
        endpoints = []
        
        # Endpoints de autenticación
        auth_endpoints = [
            {
                "path": "/auth/register",
                "method": "POST",
                "description": "Registrar nuevo usuario",
                "tags": ["Authentication"],
                "auth_required": False
            },
            {
                "path": "/auth/login",
                "method": "POST", 
                "description": "Iniciar sesión",
                "tags": ["Authentication"],
                "auth_required": False
            },
            {
                "path": "/auth/logout",
                "method": "POST",
                "description": "Cerrar sesión",
                "tags": ["Authentication"], 
                "auth_required": True
            },
            {
                "path": "/auth/refresh",
                "method": "POST",
                "description": "Renovar token",
                "tags": ["Authentication"],
                "auth_required": True
            },
            {
                "path": "/auth/forgot-password",
                "method": "POST",
                "description": "Solicitar reset de contraseña",
                "tags": ["Authentication"],
                "auth_required": False
            },
            {
                "path": "/auth/reset-password",
                "method": "POST",
                "description": "Restablecer contraseña",
                "tags": ["Authentication"],
                "auth_required": False
            }
        ]
        endpoints.extend(auth_endpoints)
        
        # Endpoints CRUD para entidades que lo requieren
        for entity in entities:
            if entity.metadata.get("generate_crud", False):
                entity_name = entity.name.lower()
                entity_plural = entity_name + "s"
                
                crud_endpoints = [
                    {
                        "path": f"/{entity_plural}",
                        "method": "GET",
                        "description": f"Listar {entity_plural}",
                        "tags": [entity.name],
                        "auth_required": True
                    },
                    {
                        "path": f"/{entity_plural}/{{id}}",
                        "method": "GET", 
                        "description": f"Obtener {entity_name} por ID",
                        "tags": [entity.name],
                        "auth_required": True
                    },
                    {
                        "path": f"/{entity_plural}",
                        "method": "POST",
                        "description": f"Crear {entity_name}",
                        "tags": [entity.name],
                        "auth_required": True
                    },
                    {
                        "path": f"/{entity_plural}/{{id}}",
                        "method": "PUT",
                        "description": f"Actualizar {entity_name}",
                        "tags": [entity.name],
                        "auth_required": True
                    },
                    {
                        "path": f"/{entity_plural}/{{id}}",
                        "method": "DELETE",
                        "description": f"Eliminar {entity_name}",
                        "tags": [entity.name], 
                        "auth_required": True
                    }
                ]
                endpoints.extend(crud_endpoints)
        
        # Endpoints específicos de SaaS
        saas_endpoints = [
            {
                "path": "/billing/plans",
                "method": "GET",
                "description": "Obtener planes disponibles",
                "tags": ["Billing"],
                "auth_required": True
            },
            {
                "path": "/billing/checkout", 
                "method": "POST",
                "description": "Crear sesión de checkout",
                "tags": ["Billing"],
                "auth_required": True
            },
            {
                "path": "/billing/portal",
                "method": "POST",
                "description": "Acceder al portal de billing",
                "tags": ["Billing"],
                "auth_required": True
            },
            {
                "path": "/organizations/{id}/invite",
                "method": "POST",
                "description": "Invitar usuario a organización",
                "tags": ["Organizations"],
                "auth_required": True
            },
            {
                "path": "/usage/stats",
                "method": "GET",
                "description": "Obtener estadísticas de uso",
                "tags": ["Usage"],
                "auth_required": True
            }
        ]
        endpoints.extend(saas_endpoints)
        
        return endpoints
    
    def _generate_business_rules(self) -> List[str]:
        """Generar reglas de negocio"""
        return [
            "Un usuario solo puede pertenecer a una organización",
            "Una organización puede tener múltiples usuarios",
            "Una organización puede tener múltiples suscripciones (histórico)",
            "Solo puede haber una suscripción activa por organización",
            "Los usuarios deben verificar su email antes de acceder",
            "Las facturas se generan automáticamente según el ciclo de billing",
            "El acceso a funcionalidades se controla por el plan de suscripción",
            "Los datos se segregan por organización (multi-tenancy)",
            "Todas las acciones importantes se registran en auditoría",
            "Los pagos fallidos pausan la suscripción después de 3 intentos",
            "Los períodos de prueba son de 14 días",
            "Los datos se eliminan después de 30 días de cancelación"
        ]
    
    def _generate_security_requirements(self) -> List[str]:
        """Generar requisitos de seguridad"""
        return [
            "Autenticación JWT con refresh tokens",
            "Hashing de contraseñas con bcrypt",
            "Rate limiting en endpoints de autenticación",
            "Validación de entrada en todos los endpoints",
            "CORS configurado correctamente",
            "HTTPS obligatorio en producción",
            "Logs de seguridad y auditoría",
            "Segregación de datos por tenant",
            "Validación de autorización en cada request",
            "Tokens con expiración corta",
            "Protección contra ataques CSRF",
            "Sanitización de datos de entrada"
        ]
    
    def _generate_performance_requirements(self) -> Dict[str, Any]:
        """Generar requisitos de rendimiento"""
        return {
            "response_time": {
                "api_average": "< 200ms",
                "api_p95": "< 500ms",
                "database_queries": "< 100ms"
            },
            "throughput": {
                "requests_per_second": 1000,
                "concurrent_users": 500
            },
            "scalability": {
                "horizontal_scaling": True,
                "database_sharding": False,
                "caching_strategy": "Redis"
            },
            "availability": {
                "uptime_target": "99.9%",
                "max_downtime_monthly": "43 minutes"
            }
        }
    
    def _generate_deployment_config(self, stack: Dict[str, str]) -> Dict[str, Any]:
        """Generar configuración de despliegue"""
        return {
            "containers": {
                "backend": {
                    "image": "python:3.11-slim",
                    "port": 8000,
                    "environment": ["DATABASE_URL", "SECRET_KEY", "STRIPE_KEY"]
                },
                "frontend": {
                    "image": "node:18-alpine",
                    "port": 3000,
                    "environment": ["NEXT_PUBLIC_API_URL"]
                },
                "database": {
                    "image": "postgres:15",
                    "port": 5432,
                    "environment": ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "port": 6379
                }
            },
            "services": {
                "nginx": {
                    "enabled": True,
                    "config": "reverse_proxy"
                },
                "certbot": {
                    "enabled": True,
                    "email": "admin@example.com"
                }
            },
            "monitoring": {
                "prometheus": True,
                "grafana": True,
                "logs": "structured_json"
            },
            "backup": {
                "database": {
                    "frequency": "daily",
                    "retention": "30_days"
                },
                "files": {
                    "frequency": "weekly", 
                    "retention": "90_days"
                }
            }
        }
    
    def get_recommended_addons(self) -> List[Dict[str, Any]]:
        """Obtener addons recomendados para SaaS"""
        return [
            {
                "name": "Stripe Integration",
                "description": "Procesamiento de pagos con Stripe",
                "category": "billing",
                "essential": True
            },
            {
                "name": "Email Service",
                "description": "Servicio de email transaccional (SendGrid/Mailgun)",
                "category": "communication",
                "essential": True
            },
            {
                "name": "Error Tracking", 
                "description": "Monitoreo de errores (Sentry)",
                "category": "monitoring",
                "essential": False
            },
            {
                "name": "Analytics",
                "description": "Analytics de producto (Mixpanel/Amplitude)",
                "category": "analytics",
                "essential": False
            },
            {
                "name": "Search Engine",
                "description": "Búsqueda avanzada (Elasticsearch)",
                "category": "search",
                "essential": False
            },
            {
                "name": "File Storage",
                "description": "Almacenamiento de archivos (AWS S3)",
                "category": "storage",
                "essential": False
            }
        ]

# Instancia global del Golden Path SaaS
golden_path_saas = GoldenPathSaaS()