# genesis_engine/agents/devops.py
"""
DevOps Agent - CORREGIDO - Configuración de DevOps y CI/CD

FIXES:
- Mejor coordinación con Frontend Agent para Dockerfiles
- Verificación de archivos antes de referencias en docker-compose
- Manejo de errores mejorado
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
    Agente DevOps - CORREGIDO
    
    Mejoras:
    - Verificación de Dockerfiles antes de referencias
    - Mejor coordinación con Frontend Agent
    - Manejo de errores robusto
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
        self.add_capability("dockerfile_verification")  # NUEVA CAPACIDAD
        
        # Registrar handlers específicos
        self.register_handler("setup_devops", self._handle_setup_devops)
        self.register_handler("generate_docker", self._handle_generate_docker)
        self.register_handler("setup_cicd", self._handle_setup_cicd)
        self.register_handler("generate_k8s", self._handle_generate_k8s)
        self.register_handler("setup_monitoring", self._handle_setup_monitoring)
        self.register_handler("verify_dockerfiles", self._handle_verify_dockerfiles)  # NUEVO HANDLER
        
        # Motor de templates
        self.template_engine = TemplateEngine()
        
    async def initialize(self):
        """Inicialización del agente DevOps"""
        self.logger.info("🐳 Inicializando DevOps Agent")
        
        # Cargar templates de DevOps
        try:
            await self._load_devops_templates()
        except NotImplementedError:
            self.logger.warning("DevOps templates loader not implemented")
        
        self.set_metadata("version", "1.0.1")  # Version actualizada
        self.set_metadata("specialization", "containerization_and_deployment")
        self.set_metadata("dockerfile_verification", True)  # NUEVA METADATA
        
        self.logger.info("✅ DevOps Agent inicializado con verificación de Dockerfiles")
    
    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica de DevOps"""
        task_name = task.name.lower()
        
        if "setup_devops" in task_name:
            return await self._setup_complete_devops(task.params)
        elif "generate_docker" in task_name:
            return await self._generate_docker_config(task.params)
        elif "verify_dockerfiles" in task_name:
            return await self._verify_dockerfiles(task.params)
        elif "setup_cicd" in task_name:
            return await self._setup_cicd_pipeline(task.params)
        elif "generate_k8s" in task_name:
            return await self._generate_kubernetes_config(task.params)
        elif "setup_monitoring" in task_name:
            return await self._setup_monitoring_stack(task.params)
        else:
            raise ValueError(f"Tarea no reconocida: {task.name}")
    
    async def _setup_complete_devops(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configurar DevOps completo - MEJORADO"""
        self.logger.info("🚀 Configurando DevOps completo")
        
        schema = params.get("schema", {})
        output_path = Path(params.get("output_path", "./"))
        config = self._extract_devops_config(params)
        
        generated_files = []
        warnings = []
        
        # 1. Verificar si existen Dockerfiles necesarios
        dockerfile_status = await self._verify_project_dockerfiles(output_path, schema)
        if not dockerfile_status["all_present"]:
            warnings.extend(dockerfile_status["warnings"])
            # Generar Dockerfiles faltantes
            missing_dockerfiles = await self._generate_missing_dockerfiles(output_path, schema, dockerfile_status)
            generated_files.extend(missing_dockerfiles)
        
        # 2. Configuración de Docker
        docker_files = await self._generate_docker_config({
            "schema": schema,
            "config": config,
            "output_path": output_path,
            "dockerfile_status": dockerfile_status
        })
        generated_files.extend(docker_files)
        
        # 3. CI/CD Pipeline
        cicd_files = await self._setup_cicd_pipeline({
            "schema": schema,
            "config": config,
            "output_path": output_path
        })
        generated_files.extend(cicd_files)
        
        # 4. Configuración de Nginx
        nginx_files = await self._generate_nginx_config(output_path, config, schema)
        generated_files.extend(nginx_files)
        
        # 5. Scripts de despliegue
        deploy_scripts = await self._generate_deployment_scripts(output_path, config)
        generated_files.extend(deploy_scripts)
        
        # 6. Monitoreo (si está habilitado)
        if config.monitoring_enabled:
            monitoring_files = await self._setup_monitoring_stack({
                "config": config,
                "output_path": output_path
            })
            generated_files.extend(monitoring_files)
        
        # 7. Configuración de backup
        if config.backup_enabled:
            backup_files = await self._generate_backup_scripts(output_path, config)
            generated_files.extend(backup_files)
        
        # 8. Configuración de seguridad
        security_files = await self._generate_security_config(output_path, config)
        generated_files.extend(security_files)
        
        result = {
            "ci_provider": config.ci_provider.value,
            "orchestrator": config.orchestrator.value,
            "generated_files": generated_files,
            "output_path": str(output_path),
            "warnings": warnings,  # NUEVO: Incluir warnings
            "dockerfile_status": dockerfile_status,  # NUEVO: Estado de Dockerfiles
            "next_steps": self._get_devops_next_steps(config),
            "commands": self._get_devops_commands(config)
        }
        
        self.logger.info(f"✅ DevOps configurado - {len(generated_files)} archivos generados")
        if warnings:
            self.logger.warning(f"⚠️ {len(warnings)} warnings encontrados")
        
        return result

    async def _verify_project_dockerfiles(self, project_path: Path, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        NUEVO MÉTODO: Verificar que existan los Dockerfiles necesarios
        """
        stack = schema.get("stack", {})
        backend_framework = stack.get("backend", "")
        frontend_framework = stack.get("frontend", "")
        
        status = {
            "all_present": True,
            "backend_dockerfile": False,
            "frontend_dockerfile": False,
            "warnings": [],
            "missing": []
        }
        
        # Verificar Dockerfile de backend
        backend_dockerfile = project_path / "backend" / "Dockerfile"
        status["backend_dockerfile"] = backend_dockerfile.exists()
        if not status["backend_dockerfile"]:
            status["warnings"].append(f"Dockerfile de backend faltante: {backend_dockerfile}")
            status["missing"].append("backend")
        
        # Verificar Dockerfile de frontend
        frontend_dockerfile = project_path / "frontend" / "Dockerfile"
        status["frontend_dockerfile"] = frontend_dockerfile.exists()
        if not status["frontend_dockerfile"]:
            status["warnings"].append(f"Dockerfile de frontend faltante: {frontend_dockerfile}")
            status["missing"].append("frontend")
        
        status["all_present"] = status["backend_dockerfile"] and status["frontend_dockerfile"]
        
        self.logger.info(f"📋 Verificación Dockerfiles: Backend={status['backend_dockerfile']}, Frontend={status['frontend_dockerfile']}")
        
        return status

    async def _generate_missing_dockerfiles(self, project_path: Path, schema: Dict[str, Any], dockerfile_status: Dict[str, Any]) -> List[str]:
        """
        NUEVO MÉTODO: Generar Dockerfiles faltantes
        """
        generated_files = []
        stack = schema.get("stack", {})
        
        # Generar Dockerfile de backend si falta
        if "backend" in dockerfile_status["missing"]:
            backend_framework = stack.get("backend", "fastapi")
            backend_dockerfile = await self._generate_backend_dockerfile(
                project_path / "backend", 
                backend_framework
            )
            if backend_dockerfile:
                generated_files.append(backend_dockerfile)
                self.logger.info(f"✅ Generado Dockerfile de backend: {backend_dockerfile}")
        
        # Generar Dockerfile de frontend si falta
        if "frontend" in dockerfile_status["missing"]:
            frontend_framework = stack.get("frontend", "nextjs")
            frontend_dockerfile = await self._generate_frontend_dockerfile_fallback(
                project_path / "frontend", 
                frontend_framework
            )
            if frontend_dockerfile:
                generated_files.append(frontend_dockerfile)
                self.logger.info(f"✅ Generado Dockerfile de frontend: {frontend_dockerfile}")
        
        return generated_files

    async def _generate_frontend_dockerfile_fallback(self, output_path: Path, framework: str) -> Optional[str]:
        """
        NUEVO MÉTODO: Generar Dockerfile de frontend como fallback
        """
        try:
            template_map = {
                "nextjs": "frontend/nextjs/Dockerfile.j2",
                "react": "frontend/react/Dockerfile.j2",
                "vue": "frontend/vue/Dockerfile.j2",
            }
            
            template_name = template_map.get(framework)
            if not template_name:
                self.logger.warning(f"No hay template de Dockerfile para frontend framework: {framework}")
                return None
            
            template_vars = {
                "framework": framework,
                "node_version": "18",
                "port": 3000 if framework == "nextjs" else 80,
            }
            
            content = self.template_engine.render_template(template_name, template_vars)
            
            output_path.mkdir(parents=True, exist_ok=True)
            dockerfile_path = output_path / "Dockerfile"
            dockerfile_path.write_text(content)
            
            return str(dockerfile_path)
            
        except Exception as e:
            self.logger.error(f"Error generando Dockerfile de frontend: {e}")
            return None

    async def _generate_backend_dockerfile(self, output_path: Path, framework: str) -> Optional[str]:
        """
        NUEVO MÉTODO: Generar Dockerfile de backend
        """
        try:
            template_map = {
                "fastapi": "backend/fastapi/Dockerfile.j2",
                "nestjs": "backend/nestjs/Dockerfile.j2",
                "express": "backend/express/Dockerfile.j2",
            }
            
            template_name = template_map.get(framework)
            if not template_name:
                self.logger.warning(f"No hay template de Dockerfile para backend framework: {framework}")
                return None
            
            template_vars = {
                "framework": framework,
                "project_name": "backend",
                "port": 8000 if framework == "fastapi" else 3000,
            }
            
            content = self.template_engine.render_template(template_name, template_vars)
            
            output_path.mkdir(parents=True, exist_ok=True)
            dockerfile_path = output_path / "Dockerfile"
            dockerfile_path.write_text(content)
            
            return str(dockerfile_path)
            
        except Exception as e:
            self.logger.error(f"Error generando Dockerfile de backend: {e}")
            return None

    async def _generate_docker_config(self, params: Dict[str, Any]) -> List[str]:
        """Generar configuración de Docker - MEJORADO"""
        self.logger.info("🐳 Generando configuración de Docker")
        
        schema = params.get("schema", {})
        config = params.get("config")
        output_path = Path(params.get("output_path", "./"))
        dockerfile_status = params.get("dockerfile_status", {})
        
        generated_files = []
        stack = schema.get("stack", {})
        
        # docker-compose.yml - MEJORADO con verificación
        compose_file = await self._generate_docker_compose_improved(output_path, schema, config, dockerfile_status)
        generated_files.append(compose_file)
        
        # .dockerignore files
        dockerignore_files = await self._generate_dockerignore_files(output_path, stack)
        generated_files.extend(dockerignore_files)
        
        return generated_files

    async def _generate_docker_compose_improved(
        self, 
        output_path: Path, 
        schema: Dict[str, Any], 
        config: DevOpsConfig,
        dockerfile_status: Dict[str, Any]
    ) -> str:
        """
        MÉTODO MEJORADO: Generar docker-compose.yml con verificaciones
        """
        stack = schema.get("stack", {})
        project_name = schema.get("project_name", "genesis_app")
        
        template_vars = {
            "project_name": project_name,
            "backend_framework": stack.get("backend", "fastapi"),
            "frontend_framework": stack.get("frontend", "nextjs"),
            "database_type": stack.get("database", "postgresql"),
            "redis_enabled": True,
            "monitoring_enabled": config.monitoring_enabled,
            "ssl_enabled": config.ssl_enabled,
            # NUEVAS VARIABLES para control condicional
            "backend_dockerfile_exists": dockerfile_status.get("backend_dockerfile", False),
            "frontend_dockerfile_exists": dockerfile_status.get("frontend_dockerfile", False),
            "include_backend": stack.get("backend") and dockerfile_status.get("backend_dockerfile", False),
            "include_frontend": stack.get("frontend") and dockerfile_status.get("frontend_dockerfile", False),
        }
        
        content = self.template_engine.render_template(
            "devops/docker-compose.yml.j2",
            template_vars
        )
        
        output_file = output_path / "docker-compose.yml"
        output_file.write_text(content)
        
        return str(output_file)

    # Handlers MCP - ACTUALIZADOS
    async def _handle_verify_dockerfiles(self, request) -> Dict[str, Any]:
        """NUEVO HANDLER: Verificar Dockerfiles"""
        return await self._verify_dockerfiles(request.data)

    async def _verify_dockerfiles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """NUEVO MÉTODO: Verificar estado de Dockerfiles"""
        project_path = Path(params.get("project_path", "./"))
        schema = params.get("schema", {})
        
        status = await self._verify_project_dockerfiles(project_path, schema)
        
        return {
            "verification_completed": True,
            "dockerfile_status": status,
            "recommendations": self._get_dockerfile_recommendations(status)
        }

    def _get_dockerfile_recommendations(self, dockerfile_status: Dict[str, Any]) -> List[str]:
        """NUEVO MÉTODO: Obtener recomendaciones sobre Dockerfiles"""
        recommendations = []
        
        if not dockerfile_status["all_present"]:
            recommendations.append("Algunos Dockerfiles están faltantes")
            
        if "backend" in dockerfile_status["missing"]:
            recommendations.append("Generar Dockerfile para backend: docker build -t backend ./backend")
            
        if "frontend" in dockerfile_status["missing"]:
            recommendations.append("Generar Dockerfile para frontend: docker build -t frontend ./frontend")
            
        if dockerfile_status["all_present"]:
            recommendations.append("Todos los Dockerfiles están presentes")
            recommendations.append("Ejecutar: docker-compose up -d")
        
        return recommendations

    # Resto de métodos anteriores (sin cambios significativos)...
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

    # Handlers MCP originales
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
            "9. Verificar que todos los Dockerfiles estén presentes",
            "10. Ejecutar despliegue inicial: docker-compose up -d",
            "11. Verificar health checks y monitoreo"
        ])
        
        return steps
    
    def _get_devops_commands(self, config: DevOpsConfig) -> Dict[str, str]:
        """Obtener comandos de DevOps"""
        commands = {
            "verify": "docker --version && docker-compose --version",
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

    # Resto de métodos auxiliares (sin cambios significativos)...
    async def _load_devops_templates(self):
        """Cargar templates de DevOps"""
        templates = self.template_engine.list_templates("devops/*")
        self.logger.debug(f"DevOps templates disponibles: {templates}")
        return templates

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

    # Métodos auxiliares simplificados (implementación básica)
    async def _generate_nginx_config(self, output_path: Path, config: DevOpsConfig, schema: Dict[str, Any]) -> List[str]:
        return []

    async def _generate_deployment_scripts(self, output_path: Path, config: DevOpsConfig) -> List[str]:
        scripts_dir = output_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        deploy_sh = scripts_dir / "deploy.sh"
        deploy_sh.write_text("#!/bin/bash\ndocker-compose up -d --build\n")
        deploy_sh.chmod(0o755)
        
        return [str(deploy_sh)]

    async def _generate_backup_scripts(self, output_path: Path, config: DevOpsConfig) -> List[str]:
        return []

    async def _generate_security_config(self, output_path: Path, config: DevOpsConfig) -> List[str]:
        return []

    async def _generate_dockerignore_files(self, output_path: Path, stack: Dict[str, str]) -> List[str]:
        files = []

        if stack.get("backend"):
            backend_ignore = output_path / "backend" / ".dockerignore"
            backend_ignore.parent.mkdir(parents=True, exist_ok=True)
            backend_ignore.write_text("__pycache__\n*.pyc\n.env\n")
            files.append(str(backend_ignore))

        if stack.get("frontend"):
            frontend_ignore = output_path / "frontend" / ".dockerignore"
            frontend_ignore.parent.mkdir(parents=True, exist_ok=True)
            frontend_ignore.write_text("node_modules\n.next\n.env\n")
            files.append(str(frontend_ignore))

        return files

    # Métodos auxiliares K8s (implementación simplificada)
    async def _generate_k8s_namespace(self, output_path: Path, schema: Dict[str, Any]) -> str:
        content = f"apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {schema.get('project_name', 'app')}\n"
        file = output_path / "namespace.yaml"
        file.write_text(content)
        return str(file)

    async def _generate_k8s_configmaps(self, output_path: Path, schema: Dict[str, Any]) -> str:
        content = f"apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: {schema.get('project_name', 'app')}-config\ndata:\n  EXAMPLE: value\n"
        file = output_path / "configmap.yaml"
        file.write_text(content)
        return str(file)

    async def _generate_k8s_secrets(self, output_path: Path, schema: Dict[str, Any]) -> str:
        content = f"apiVersion: v1\nkind: Secret\nmetadata:\n  name: {schema.get('project_name', 'app')}-secret\nstringData:\n  SECRET_KEY: changeme\n"
        file = output_path / "secret.yaml"
        file.write_text(content)
        return str(file)

    async def _generate_k8s_backend_deployment(self, output_path: Path, schema: Dict[str, Any]) -> str:
        name = f"{schema.get('project_name', 'app')}-backend"
        content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: backend
        image: {name}:latest
        ports:
        - containerPort: 8000
"""
        file = output_path / "backend-deployment.yaml"
        file.write_text(content)
        return str(file)

    async def _generate_k8s_frontend_deployment(self, output_path: Path, schema: Dict[str, Any]) -> str:
        name = f"{schema.get('project_name', 'app')}-frontend"
        content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: frontend
        image: {name}:latest
        ports:
        - containerPort: 3000
"""
        file = output_path / "frontend-deployment.yaml"
        file.write_text(content)
        return str(file)

    async def _generate_k8s_database_deployment(self, output_path: Path, schema: Dict[str, Any]) -> str:
        content = """apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          value: password
"""
        file = output_path / "database-statefulset.yaml"
        file.write_text(content)
        return str(file)

    async def _generate_k8s_services(self, output_path: Path, schema: Dict[str, Any]) -> str:
        project = schema.get("project_name", "app")
        content = f"""apiVersion: v1
kind: Service
metadata:
  name: {project}-backend
spec:
  selector:
    app: {project}-backend
  ports:
  - port: 8000
    targetPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: {project}-frontend
spec:
  selector:
    app: {project}-frontend
  ports:
  - port: 80
    targetPort: 3000
"""
        file = output_path / "services.yaml"
        file.write_text(content)
        return str(file)

    async def _generate_k8s_ingress(self, output_path: Path, schema: Dict[str, Any], config: DevOpsConfig) -> str:
        project = schema.get("project_name", "app")
        content = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {project}-ingress
spec:
  rules:
  - host: {project}.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {project}-frontend
            port:
              number: 80
"""
        file = output_path / "ingress.yaml"
        file.write_text(content)
        return str(file)

    # Métodos auxiliares CI/CD
    async def _generate_github_ci_workflow(self, workflows_dir: Path, schema: Dict[str, Any]) -> str:
        content = self.template_engine.render_template(
            "devops/github/ci.yml.j2",
            {
                "project_name": schema.get("project_name", "app"),
                "python_version": "3.11",
                "node_version": "18"
            }
        )
        workflow = workflows_dir / "ci.yml"
        workflow.write_text(content)
        return str(workflow)

    async def _generate_github_cd_workflow(self, workflows_dir: Path, schema: Dict[str, Any], config: DevOpsConfig) -> str:
        content = """name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: echo 'Deploying application'
"""
        workflow = workflows_dir / "deploy.yml"
        workflow.write_text(content)
        return str(workflow)

    async def _generate_gitlab_ci(self, output_path: Path, schema: Dict[str, Any], config: DevOpsConfig) -> str:
        content = """stages:
  - build
  - deploy
build:
  script:
    - echo 'Building'
  stage: build
deploy:
  script:
    - echo 'Deploying'
  stage: deploy
"""
        gitlab_ci = output_path / ".gitlab-ci.yml"
        gitlab_ci.write_text(content)
        return str(gitlab_ci)

    # Métodos auxiliares de monitoreo
    async def _generate_prometheus_config(self, output_path: Path) -> str:
        content = """global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
"""
        file = output_path / "prometheus.yml"
        file.write_text(content)
        return str(file)

    async def _generate_grafana_dashboards(self, output_path: Path) -> List[str]:
        dashboards_dir = output_path / "grafana"
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        dashboard = dashboards_dir / "sample.json"
        dashboard.write_text("{}\n")
        return [str(dashboard)]

    async def _generate_alertmanager_config(self, output_path: Path) -> str:
        content = """route:
  receiver: 'default'
receivers:
  - name: 'default'
"""
        file = output_path / "alertmanager.yml"
        file.write_text(content)
        return str(file)

    async def _generate_monitoring_compose(self, output_path: Path) -> str:
        content = """version: '3'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - '9090:9090'
  grafana:
    image: grafana/grafana
    ports:
      - '3001:3000'
"""
        file = output_path / "docker-compose.yml"
        file.write_text(content)
        return str(file)