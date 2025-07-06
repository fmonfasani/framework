"""
DevOps Agent - Configuración de DevOps y CI/CD

Este agente es responsable de:
- Generar Dockerfiles optimizados
- Configurar CI/CD pipelines (GitHub Actions, GitLab CI)
- Crear docker-compose.yml para desarrollo
- Configurar Kubernetes manifests
- Generar scripts de despliegue
- Configurar monitoreo y logging
- Implementar health checks
- Configurar nginx y reverse proxy
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
from genesis_engine.templates.engine import TemplateEngine

class CIProvider(str, Enum):
    """Proveedores de CI/CD"""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"
    CIRCLECI = "circleci"

class ContainerOrchestrator(str, Enum):
    """Orquestadores de contenedores"""
    DOCKER_COMPOSE = "docker_compose"
    KUBERNETES = "kubernetes"
    DOCKER_SWARM = "docker_swarm"

class CloudProvider(str, Enum):
    """Proveedores de cloud"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DIGITALOCEAN = "digitalocean"
    HEROKU = "heroku"

@dataclass
class DevOpsConfig:
    """Configuración de DevOps"""
    ci_provider: CIProvider
    orchestrator: ContainerOrchestrator
    cloud_provider: Optional[CloudProvider]
    monitoring_enabled: bool
    logging_enabled: bool
    ssl_enabled: bool
    backup_enabled: bool
    auto_scaling: bool

class DevOpsAgent(GenesisAgent):
    """
    Agente DevOps - Automatización de infraestructura
    
    Responsable de generar toda la configuración necesaria para
    CI/CD, contenedores, despliegue y monitoreo.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="devops_agent",
            name="DevOpsAgent",
            agent_type="devops"
        )
        
        # Capacidades del agente
        self.add_capability("docker_generation")
        self.add_capability("ci_cd_pipelines")
        self.add_capability("kubernetes_manifests")
        self.add_capability("nginx_configuration")
        self.add_capability("monitoring_setup")
        self.add_capability("backup_scripts")
        self.add_capability("security_hardening")
        
        # Registrar handlers específicos
        self.register_handler("setup_devops", self._handle_setup_devops)
        self.register_handler("generate_docker", self._handle_generate_docker)
        self.register_handler("setup_cicd", self._handle_setup_cicd)
        self.register_handler("generate_k8s", self._handle_generate_k8s)
        self.register_handler("setup_monitoring", self._handle_setup_monitoring)
        
        # Motor de templates
        self.template_engine = TemplateEngine()
        
    async def initialize(self):
        """Inicialización del agente DevOps"""
        self.logger.info("🐳 Inicializando DevOps Agent")
        
        # Cargar templates de DevOps
        await self._load_devops_templates()
        
        self.set_metadata("version", "1.0.0")
        self.set_metadata("specialization", "containerization_and_deployment")
        
        self.logger.info("✅ DevOps Agent inicializado")
    
    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica de DevOps"""
        task_name = task.name.lower()
        
        if "setup_devops" in task_name:
            return await self._setup_complete_devops(task.params)
        elif "generate_docker" in task_name:
            return await self._generate_docker_config(task.params)
        elif "setup_cicd" in task_name:
            return await self._setup_cicd_pipeline(task.params)
        elif "generate_k8s" in task_name:
            return await self._generate_kubernetes_config(task.params)
        elif "setup_monitoring" in task_name:
            return await self._setup_monitoring_stack(task.params)
        else:
            raise ValueError(f"Tarea no reconocida: {task.name}")
    
    async def _setup_complete_devops(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configurar DevOps completo"""
        self.logger.info("🚀 Configurando DevOps completo")
        
        schema = params.get("schema", {})
        output_path = Path(params.get("output_path", "./"))
        config = self._extract_devops_config(params)
        
        generated_files = []
        
        # 1. Configuración de Docker
        docker_files = await self._generate_docker_config({
            "schema": schema,
            "config": config,
            "output_path": output_path
        })
        generated_files.extend(docker_files)
        
        # 2. CI/CD Pipeline
        cicd_files = await self._setup_cicd_pipeline({
            "schema": schema,
            "config": config,
            "output_path": output_path
        })
        generated_files.extend(cicd_files)
        
        # 3. Configuración de Nginx
        nginx_files = await self._generate_nginx_config(output_path, config, schema)
        generated_files.extend(nginx_files)
        
        # 4. Scripts de despliegue
        deploy_scripts = await self._generate_deployment_scripts(output_path, config)
        generated_files.extend(deploy_scripts)
        
        # 5. Monitoreo (si está habilitado)
        if config.monitoring_enabled:
            monitoring_files = await self._setup_monitoring_stack({
                "config": config,
                "output_path": output_path
            })
            generated_files.extend(monitoring_files)
        
        # 6. Configuración de backup
        if config.backup_enabled:
            backup_files = await self._generate_backup_scripts(output_path, config)
            generated_files.extend(backup_files)
        
        # 7. Configuración de seguridad
        security_files = await self._generate_security_config(output_path, config)
        generated_files.extend(security_files)
        
        result = {
            "ci_provider": config.ci_provider.value,
            "orchestrator": config.orchestrator.value,
            "generated_files": generated_files,
            "output_path": str(output_path),
            "next_steps": self._get_devops_next_steps(config),
            "commands": self._get_devops_commands(config)
        }
        
        self.logger.info(f"✅ DevOps configurado - {len(generated_files)} archivos generados")
        return result
    
    def _extract_devops_config(self, params: Dict[str, Any]) -> DevOpsConfig:
        """Extraer configuración de DevOps"""
        return DevOpsConfig(
            ci_provider=CIProvider(params.get("ci_provider", "github_actions")),
            orchestrator=ContainerOrchestrator(params.get("orchestrator", "docker_compose")),
            cloud_provider=CloudProvider(params.get("cloud_provider")) if params.get("cloud_provider") else None,
            monitoring_enabled=params.get("monitoring", True),
            logging_enabled=params.get("logging", True),
            ssl_enabled=params.get("ssl", True),
            backup_enabled=params.get("backup", True),
            auto_scaling=params.get("auto_scaling", False)
        )
    
    async def _generate_docker_config(self, params: Dict[str, Any]) -> List[str]:
        """Generar configuración de Docker"""
        self.logger.info("🐳 Generando configuración de Docker")
        
        schema = params.get("schema", {})
        config = params.get("config")
        output_path = Path(params.get("output_path", "./"))
        
        generated_files = []
        stack = schema.get("stack", {})
        
        # Dockerfile para backend
        if stack.get("backend") == "fastapi":
            backend_dockerfile = await self._generate_python_dockerfile(
                output_path / "backend", "backend"
            )
            generated_files.append(backend_dockerfile)
        elif stack.get("backend") == "nestjs":
            backend_dockerfile = await self._generate_node_dockerfile(
                output_path / "backend", "backend"
            )
            generated_files.append(backend_dockerfile)
        
        # Dockerfile para frontend
        if stack.get("frontend") == "nextjs":
            frontend_dockerfile = await self._generate_nextjs_dockerfile(
                output_path / "frontend"
            )
            generated_files.append(frontend_dockerfile)
        
        # docker-compose.yml
        compose_file = await self._generate_docker_compose(output_path, schema, config)
        generated_files.append(compose_file)
        
        # .dockerignore files
        dockerignore_files = await self._generate_dockerignore_files(output_path, stack)
        generated_files.extend(dockerignore_files)
        
        return generated_files
    
    async def _setup_cicd_pipeline(self, params: Dict[str, Any]) -> List[str]:
        """Configurar pipeline CI/CD"""
        self.logger.info("⚙️ Configurando pipeline CI/CD")
        
        schema = params.get("schema", {})
        config = params.get("config")
        output_path = Path(params.get("output_path", "./"))
        
        generated_files = []
        
        if config.ci_provider == CIProvider.GITHUB_ACTIONS:
            # GitHub Actions workflows
            workflows_dir = output_path / ".github" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            # CI workflow
            ci_workflow = await self._generate_github_ci_workflow(workflows_dir, schema)
            generated_files.append(ci_workflow)
            
            # CD workflow
            cd_workflow = await self._generate_github_cd_workflow(workflows_dir, schema, config)
            generated_files.append(cd_workflow)
            
            # PR workflow
            pr_workflow = await self._generate_github_pr_workflow(workflows_dir, schema)
            generated_files.append(pr_workflow)
        
        elif config.ci_provider == CIProvider.GITLAB_CI:
            # GitLab CI configuration
            gitlab_ci_file = await self._generate_gitlab_ci(output_path, schema, config)
            generated_files.append(gitlab_ci_file)
        
        return generated_files
    
    async def _generate_kubernetes_config(self, params: Dict[str, Any]) -> List[str]:
        """Generar configuración de Kubernetes"""
        self.logger.info("☸️ Generando configuración de Kubernetes")
        
        schema = params.get("schema", {})
        config = params.get("config")
        output_path = Path(params.get("output_path", "./")) / "k8s"
        
        output_path.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        # Namespace
        namespace_file = await self._generate_k8s_namespace(output_path, schema)
        generated_files.append(namespace_file)
        
        # ConfigMaps
        configmap_file = await self._generate_k8s_configmaps(output_path, schema)
        generated_files.append(configmap_file)
        
        # Secrets
        secrets_file = await self._generate_k8s_secrets(output_path, schema)
        generated_files.append(secrets_file)
        
        # Backend deployment
        backend_deploy = await self._generate_k8s_backend_deployment(output_path, schema)
        generated_files.append(backend_deploy)
        
        # Frontend deployment
        frontend_deploy = await self._generate_k8s_frontend_deployment(output_path, schema)
        generated_files.append(frontend_deploy)
        
        # Database deployment
        db_deploy = await self._generate_k8s_database_deployment(output_path, schema)
        generated_files.append(db_deploy)
        
        # Services
        services_file = await self._generate_k8s_services(output_path, schema)
        generated_files.append(services_file)
        
        # Ingress
        ingress_file = await self._generate_k8s_ingress(output_path, schema, config)
        generated_files.append(ingress_file)
        
        # HPA (if auto-scaling enabled)
        if config.auto_scaling:
            hpa_file = await self._generate_k8s_hpa(output_path, schema)
            generated_files.append(hpa_file)
        
        return generated_files
    
    async def _setup_monitoring_stack(self, params: Dict[str, Any]) -> List[str]:
        """Configurar stack de monitoreo"""
        self.logger.info("📊 Configurando monitoreo")
        
        config = params.get("config")
        output_path = Path(params.get("output_path", "./")) / "monitoring"
        
        output_path.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        # Prometheus configuration
        prometheus_config = await self._generate_prometheus_config(output_path)
        generated_files.append(prometheus_config)
        
        # Grafana dashboards
        grafana_dashboards = await self._generate_grafana_dashboards(output_path)
        generated_files.extend(grafana_dashboards)
        
        # Alertmanager config
        alertmanager_config = await self._generate_alertmanager_config(output_path)
        generated_files.append(alertmanager_config)
        
        # Docker compose for monitoring
        monitoring_compose = await self._generate_monitoring_compose(output_path)
        generated_files.append(monitoring_compose)
        
        return generated_files
    
    async def _generate_docker_compose(
        self, 
        output_path: Path, 
        schema: Dict[str, Any], 
        config: DevOpsConfig
    ) -> str:
        """Generar docker-compose.yml"""
        
        stack = schema.get("stack", {})
        project_name = schema.get("project_name", "genesis_app")
        
        template_vars = {
            "project_name": project_name,
            "backend_framework": stack.get("backend", "fastapi"),
            "frontend_framework": stack.get("frontend", "nextjs"),
            "database_type": stack.get("database", "postgresql"),
            "redis_enabled": True,
            "monitoring_enabled": config.monitoring_enabled,
            "ssl_enabled": config.ssl_enabled
        }
        
        content = await self.template_engine.render_template(
            "devops/docker-compose.yml.j2",
            template_vars
        )
        
        output_file = output_path / "docker-compose.yml"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _generate_github_ci_workflow(
        self, 
        workflows_dir: Path, 
        schema: Dict[str, Any]
    ) -> str:
        """Generar workflow de CI para GitHub Actions"""
        
        stack = schema.get("stack", {})
        
        template_vars = {
            "project_name": schema.get("project_name", "genesis_app"),
            "backend_framework": stack.get("backend", "fastapi"),
            "frontend_framework": stack.get("frontend", "nextjs"),
            "typescript": stack.get("typescript", True),
            "python_version": "3.11",
            "node_version": "18"
        }
        
        content = await self.template_engine.render_template(
            "devops/github/ci.yml.j2",
            template_vars
        )
        
        output_file = workflows_dir / "ci.yml"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _generate_nginx_config(
        self, 
        output_path: Path, 
        config: DevOpsConfig, 
        schema: Dict[str, Any]
    ) -> List[str]:
        """Generar configuración de Nginx"""
        
        nginx_dir = output_path / "nginx"
        nginx_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # nginx.conf principal
        nginx_conf = await self._generate_main_nginx_conf(nginx_dir, config, schema)
        generated_files.append(nginx_conf)
        
        # Configuración del sitio
        site_conf = await self._generate_site_nginx_conf(nginx_dir, config, schema)
        generated_files.append(site_conf)
        
        # SSL configuration (si está habilitado)
        if config.ssl_enabled:
            ssl_conf = await self._generate_ssl_nginx_conf(nginx_dir)
            generated_files.append(ssl_conf)
        
        return generated_files
    
    def _get_devops_next_steps(self, config: DevOpsConfig) -> List[str]:
        """Obtener siguientes pasos para DevOps"""
        steps = [
            "1. Revisar y ajustar configuraciones según el entorno",
            "2. Configurar variables de entorno y secretos",
            "3. Configurar registros de contenedores (Docker Hub, ECR, etc.)",
        ]
        
        if config.ci_provider == CIProvider.GITHUB_ACTIONS:
            steps.append("4. Configurar GitHub Secrets para CI/CD")
            steps.append("5. Habilitar GitHub Actions en el repositorio")
        
        if config.orchestrator == ContainerOrchestrator.KUBERNETES:
            steps.append("6. Configurar cluster de Kubernetes")
            steps.append("7. Instalar cert-manager para SSL automático")
        
        if config.monitoring_enabled:
            steps.append("8. Configurar alertas en Prometheus/Grafana")
        
        steps.extend([
            "9. Ejecutar despliegue inicial: ./scripts/deploy.sh",
            "10. Verificar health checks y monitoreo"
        ])
        
        return steps
    
    def _get_devops_commands(self, config: DevOpsConfig) -> Dict[str, str]:
        """Obtener comandos de DevOps"""
        commands = {
            "build": "docker-compose build",
            "dev": "docker-compose up -d",
            "logs": "docker-compose logs -f",
            "stop": "docker-compose down",
            "clean": "docker-compose down -v --rmi all"
        }
        
        if config.orchestrator == ContainerOrchestrator.KUBERNETES:
            commands.update({
                "k8s_apply": "kubectl apply -f k8s/",
                "k8s_status": "kubectl get pods,svc,ingress",
                "k8s_logs": "kubectl logs -f deployment/backend",
                "k8s_delete": "kubectl delete -f k8s/"
            })
        
        return commands
    
    # Handlers MCP
    async def _handle_setup_devops(self, request) -> Dict[str, Any]:
        """Handler para configuración completa de DevOps"""
        return await self._setup_complete_devops(request.params)
    
    async def _handle_generate_docker(self, request) -> Dict[str, Any]:
        """Handler para generación de Docker"""
        files = await self._generate_docker_config(request.params)
        return {"generated_files": files}
    
    async def _handle_setup_cicd(self, request) -> Dict[str, Any]:
        """Handler para configuración de CI/CD"""
        files = await self._setup_cicd_pipeline(request.params)
        return {"generated_files": files}
    
    async def _handle_generate_k8s(self, request) -> Dict[str, Any]:
        """Handler para generación de Kubernetes"""
        files = await self._generate_kubernetes_config(request.params)
        return {"generated_files": files}
    
    async def _handle_setup_monitoring(self, request) -> Dict[str, Any]:
        """Handler para configuración de monitoreo"""
        files = await self._setup_monitoring_stack(request.params)
        return {"generated_files": files}
    
    # Métodos auxiliares (implementación completa en producción)
    async def _load_devops_templates(self):
        """Cargar templates de DevOps"""
        pass
    
    async def _generate_python_dockerfile(self, output_path: Path, service_name: str) -> str:
        """Generar Dockerfile para Python/FastAPI"""
        return ""
    
    async def _generate_node_dockerfile(self, output_path: Path, service_name: str) -> str:
        """Generar Dockerfile para Node.js"""
        return ""
    
    async def _generate_nextjs_dockerfile(self, output_path: Path) -> str:
        """Generar Dockerfile para Next.js"""
        return ""
    
    async def _generate_dockerignore_files(self, output_path: Path, stack: Dict[str, str]) -> List[str]:
        """Generar archivos .dockerignore"""
        return []
    
    async def _generate_github_cd_workflow(self, workflows_dir: Path, schema: Dict[str, Any], config: DevOpsConfig) -> str:
        """Generar workflow de CD para GitHub Actions"""
        return ""
    
    async def _generate_github_pr_workflow(self, workflows_dir: Path, schema: Dict[str, Any]) -> str:
        """Generar workflow de PR para GitHub Actions"""
        return ""
    
    async def _generate_gitlab_ci(self, output_path: Path, schema: Dict[str, Any], config: DevOpsConfig) -> str:
        """Generar configuración de GitLab CI"""
        return ""
    
    async def _generate_k8s_namespace(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar namespace de Kubernetes"""
        return ""
    
    async def _generate_k8s_configmaps(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar ConfigMaps de Kubernetes"""
        return ""
    
    async def _generate_k8s_secrets(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar Secrets de Kubernetes"""
        return ""
    
    async def _generate_k8s_backend_deployment(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar deployment del backend"""
        return ""
    
    async def _generate_k8s_frontend_deployment(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar deployment del frontend"""
        return ""
    
    async def _generate_k8s_database_deployment(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar deployment de la base de datos"""
        return ""
    
    async def _generate_k8s_services(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar Services de Kubernetes"""
        return ""
    
    async def _generate_k8s_ingress(self, output_path: Path, schema: Dict[str, Any], config: DevOpsConfig) -> str:
        """Generar Ingress de Kubernetes"""
        return ""
    
    async def _generate_k8s_hpa(self, output_path: Path, schema: Dict[str, Any]) -> str:
        """Generar HorizontalPodAutoscaler"""
        return ""
    
    async def _generate_deployment_scripts(self, output_path: Path, config: DevOpsConfig) -> List[str]:
        """Generar scripts de despliegue"""
        return []
    
    async def _generate_backup_scripts(self, output_path: Path, config: DevOpsConfig) -> List[str]:
        """Generar scripts de backup"""
        return []
    
    async def _generate_security_config(self, output_path: Path, config: DevOpsConfig) -> List[str]:
        """Generar configuración de seguridad"""
        return []
    
    async def _generate_prometheus_config(self, output_path: Path) -> str:
        """Generar configuración de Prometheus"""
        return ""
    
    async def _generate_grafana_dashboards(self, output_path: Path) -> List[str]:
        """Generar dashboards de Grafana"""
        return []
    
    async def _generate_alertmanager_config(self, output_path: Path) -> str:
        """Generar configuración de Alertmanager"""
        return ""
    
    async def _generate_monitoring_compose(self, output_path: Path) -> str:
        """Generar docker-compose para monitoreo"""
        return ""
    
    async def _generate_main_nginx_conf(self, nginx_dir: Path, config: DevOpsConfig, schema: Dict[str, Any]) -> str:
        """Generar nginx.conf principal"""
        return ""
    
    async def _generate_site_nginx_conf(self, nginx_dir: Path, config: DevOpsConfig, schema: Dict[str, Any]) -> str:
        """Generar configuración del sitio"""
        return ""
    
    async def _generate_ssl_nginx_conf(self, nginx_dir: Path) -> str:
        """Generar configuración SSL"""
        return ""