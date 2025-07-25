"""
Deploy Agent - Despliegue automático de aplicaciones

Este agente es responsable de:
- Despliegue local con Docker Compose
- Despliegue en cloud providers (AWS, GCP, Azure)
- Despliegue en Kubernetes
- Configuración de dominios y SSL
- Monitoreo post-despliegue
- Rollback automático en caso de fallos
- Gestión de environments (dev, staging, prod)
"""

import asyncio
import subprocess
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
import logging
import os
import shutil
import platform
import json
from pathlib import Path
from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult

class DeploymentTarget(str, Enum):
    """Objetivos de despliegue"""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    HEROKU = "heroku"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    DIGITALOCEAN = "digitalocean"

class DeploymentEnvironment(str, Enum):
    """Ambientes de despliegue"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DeploymentConfig:
    """Configuración de despliegue"""
    target: DeploymentTarget
    environment: DeploymentEnvironment
    domain: Optional[str] = None
    ssl_enabled: bool = True
    auto_scale: bool = False
    backup_enabled: bool = True
    monitoring_enabled: bool = True
    custom_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_config is None:
            self.custom_config = {}

@dataclass
class DeploymentResult:
    """Resultado del despliegue"""
    success: bool
    target: DeploymentTarget
    environment: DeploymentEnvironment
    urls: List[str]
    services: Dict[str, str]
    logs: List[str]
    error: Optional[str] = None
    rollback_available: bool = False

class DeployAgent(GenesisAgent):
    """
    Agente de Despliegue - Automatización de deployments
    
    Responsable de desplegar aplicaciones en diferentes entornos
    y plataformas de manera automática y segura.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="deploy_agent",
            name="DeployAgent",
            agent_type="deployment"
        )
        
        # Capacidades del agente
        self.add_capability("local_deployment")
        self.add_capability("docker_deployment") 
        self.add_capability("kubernetes_deployment")
        self.add_capability("cloud_deployment")
        self.add_capability("ssl_configuration")
        self.add_capability("domain_setup")
        self.add_capability("rollback_management")
        
        # Registrar handlers específicos
        self.register_handler("deploy_project", self._handle_deploy_project)
        self.register_handler("deploy_local", self._handle_deploy_local)
        self.register_handler("deploy_cloud", self._handle_deploy_cloud)
        self.register_handler("deploy_k8s", self._handle_deploy_k8s)
        self.register_handler("rollback", self._handle_rollback)
        self.register_handler("get_status", self._handle_get_status)
        
        # Estado de despliegues
        self.active_deployments: Dict[str, DeploymentResult] = {}
        self.deployment_history: List[DeploymentResult] = []
        
    async def initialize(self):
        """Inicialización del agente de despliegue"""
        self.logger.info("🚀 Inicializando Deploy Agent")
        
        # Verificar herramientas necesarias
        await self._check_deployment_tools()
        
        self.set_metadata("version", "1.0.0")
        self.set_metadata("specialization", "automated_deployment")
        
        self.logger.info("✅ Deploy Agent inicializado")
    
    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica de despliegue"""
        task_name = task.name.lower()
        
        if "deploy_project" in task_name:
            return await self._deploy_complete_project(task.params)
        elif "deploy_local" in task_name:
            return await self._deploy_to_local(task.params)
        elif "deploy_cloud" in task_name:
            return await self._deploy_to_cloud(task.params)
        elif "deploy_k8s" in task_name:
            return await self._deploy_to_kubernetes(task.params)
        elif "rollback" in task_name:
            return await self._perform_rollback(task.params)
        elif "get_status" in task_name:
            return await self._get_deployment_status(task.params)
        else:
            raise ValueError(f"Tarea no reconocida: {task.name}")
    
    async def _deploy_complete_project(self, params: Dict[str, Any]) -> DeploymentResult:
        """Desplegar proyecto completo"""
        self.logger.info("🚀 Iniciando despliegue completo")
        
        project_path = Path(params.get("project_path", "./"))
        config = self._extract_deployment_config(params)
        
        try:
            # Pre-deployment checks
            await self._pre_deployment_checks(project_path, config)
            
            # Ejecutar despliegue según el target
            if config.target == DeploymentTarget.LOCAL:
                result = await self._deploy_to_local({
                    "project_path": project_path,
                    "config": config
                })
            elif config.target == DeploymentTarget.DOCKER:
                result = await self._deploy_with_docker(project_path, config)
            elif config.target == DeploymentTarget.KUBERNETES:
                result = await self._deploy_to_kubernetes({
                    "project_path": project_path,
                    "config": config
                })
            elif config.target in [DeploymentTarget.AWS, DeploymentTarget.GCP, DeploymentTarget.AZURE]:
                result = await self._deploy_to_cloud({
                    "project_path": project_path,
                    "config": config
                })
            else:
                raise ValueError(f"Target de despliegue no soportado: {config.target}")
            
            # Post-deployment tasks
            if result.success:
                await self._post_deployment_tasks(project_path, config, result)
            
            # Guardar en historial
            self.deployment_history.append(result)
            if result.success:
                deployment_id = f"{config.target.value}_{config.environment.value}"
                self.active_deployments[deployment_id] = result
            
            return result
            

        except (OSError, FileNotFoundError, RuntimeError, ValueError, asyncio.TimeoutError) as e:
            self.logger.error(
                f"❌ Error en despliegue {config.target.value}/{config.environment.value}: {e}"
            )

            return DeploymentResult(
                success=False,
                target=config.target,
                environment=config.environment,
                urls=[],
                services={},
                logs=[f"Error: {str(e)}"],
                error=str(e)
            )
    
    def _extract_deployment_config(self, params: Dict[str, Any]) -> DeploymentConfig:
        """Extraer configuración de despliegue"""
        return DeploymentConfig(
            target=DeploymentTarget(params.get("target", "local")),
            environment=DeploymentEnvironment(params.get("environment", "development")),
            domain=params.get("domain"),
            ssl_enabled=params.get("ssl", True),
            auto_scale=params.get("auto_scale", False),
            backup_enabled=params.get("backup", True),
            monitoring_enabled=params.get("monitoring", True),
            custom_config=params.get("custom_config", {})
        )
    
    async def _pre_deployment_checks(self, project_path: Path, config: DeploymentConfig):
        """Verificaciones pre-despliegue"""
        self.logger.info("🔍 Ejecutando verificaciones pre-despliegue")
        
        # Verificar que existe genesis.json
        genesis_file = project_path / "genesis.json"
        if not genesis_file.exists():
            raise FileNotFoundError("Archivo genesis.json no encontrado")
        
        # Verificar estructura del proyecto
        required_dirs = []
        if (project_path / "backend").exists():
            required_dirs.append("backend")
        if (project_path / "frontend").exists():
            required_dirs.append("frontend")
        
        if not required_dirs:
            raise ValueError("No se encontraron directorios backend o frontend")
        
        # Verificar docker-compose.yml para despliegue local/docker
        if config.target in [DeploymentTarget.LOCAL, DeploymentTarget.DOCKER]:
            docker_compose = project_path / "docker-compose.yml"
            if not docker_compose.exists():
                raise FileNotFoundError("docker-compose.yml no encontrado")
        
        # Verificar manifests de Kubernetes
        if config.target == DeploymentTarget.KUBERNETES:
            k8s_dir = project_path / "k8s"
            if not k8s_dir.exists():
                raise FileNotFoundError("Directorio k8s/ no encontrado")
        
        self.logger.info("✅ Verificaciones pre-despliegue completadas")
    
    async def _deploy_to_local(self, params: Dict[str, Any]) -> DeploymentResult:
        """Desplegar localmente con Docker Compose"""
        self.logger.info("🏠 Desplegando localmente")
        
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")
        
        try:
            # Cambiar al directorio del proyecto
            original_cwd = Path.cwd()
            os.chdir(project_path)
            
            logs = []
            
            # Construir imágenes
            self.logger.info("🔨 Construyendo imágenes...")
            build_result = await self._run_command(
                ["docker-compose", "build"],
                capture_output=True
            )
            logs.extend(build_result["logs"])
            
            if not build_result["success"]:
                raise RuntimeError("Error construyendo imágenes Docker")
            
            # Iniciar servicios
            self.logger.info("▶️ Iniciando servicios...")
            up_result = await self._run_command(
                ["docker-compose", "up", "-d"],
                capture_output=True
            )
            logs.extend(up_result["logs"])
            
            if not up_result["success"]:
                raise RuntimeError("Error iniciando servicios")
            
            # Esperar que los servicios estén listos
            await self._wait_for_services_ready(project_path)
            
            # Obtener URLs de servicios
            urls = self._get_local_service_urls(project_path)
            
            # Información de servicios
            services = await self._get_running_services()
            
            return DeploymentResult(
                success=True,
                target=DeploymentTarget.LOCAL,
                environment=config.environment,
                urls=urls,
                services=services,
                logs=logs,
                rollback_available=True
            )
            

        except (OSError, RuntimeError, asyncio.TimeoutError, subprocess.SubprocessError) as e:
            self.logger.error(
                f"❌ Error en despliegue local en {project_path}: {e}"
            )

            return DeploymentResult(
                success=False,
                target=DeploymentTarget.LOCAL,
                environment=config.environment,
                urls=[],
                services={},
                logs=[f"Error: {str(e)}"],
                error=str(e)
            )
        finally:
            os.chdir(original_cwd)
    
    async def _deploy_to_cloud(self, params: Dict[str, Any]) -> DeploymentResult:
        """Desplegar en cloud provider"""
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")
        
        self.logger.info(f"☁️ Desplegando en {config.target.value}")
        
        if config.target == DeploymentTarget.HEROKU:
            return await self._deploy_to_heroku(project_path, config)
        elif config.target == DeploymentTarget.VERCEL:
            return await self._deploy_to_vercel(project_path, config)
        elif config.target == DeploymentTarget.AWS:
            return await self._deploy_to_aws(project_path, config)
        else:
            raise ValueError(f"Cloud provider no implementado: {config.target}")
    
    async def _deploy_to_kubernetes(self, params: Dict[str, Any]) -> DeploymentResult:
        """Desplegar en Kubernetes"""
        self.logger.info("☸️ Desplegando en Kubernetes")
        
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")
        
        try:
            logs = []
            
            # Aplicar manifests
            k8s_dir = project_path / "k8s"
            apply_result = await self._run_command(
                ["kubectl", "apply", "-f", str(k8s_dir)],
                capture_output=True
            )
            logs.extend(apply_result["logs"])
            
            if not apply_result["success"]:
                raise RuntimeError("Error aplicando manifests de Kubernetes")
            
            # Esperar que los pods estén listos
            await self._wait_for_k8s_pods_ready(project_path)
            
            # Obtener URLs de servicios
            urls = await self._get_k8s_service_urls(project_path)
            
            # Información de servicios
            services = await self._get_k8s_services()
            
            return DeploymentResult(
                success=True,
                target=DeploymentTarget.KUBERNETES,
                environment=config.environment,
                urls=urls,
                services=services,
                logs=logs,
                rollback_available=True
            )
            

        except (OSError, RuntimeError, asyncio.TimeoutError, subprocess.SubprocessError) as e:
            self.logger.error(
                f"❌ Error en despliegue K8s en {project_path}: {e}"
            )

            return DeploymentResult(
                success=False,
                target=DeploymentTarget.KUBERNETES,
                environment=config.environment,
                urls=[],
                services={},
                logs=[f"Error: {str(e)}"],
                error=str(e)
            )
    
    async def _run_command(
        self, 
        command: List[str], 
        capture_output: bool = True,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Ejecutar comando de sistema"""
        try:
            if capture_output:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                return {
                    "success": process.returncode == 0,
                    "returncode": process.returncode,
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "logs": [stdout.decode(), stderr.decode()] if stdout or stderr else []
                }
            else:
                process = await asyncio.create_subprocess_exec(*command)
                returncode = await asyncio.wait_for(
                    process.wait(), 
                    timeout=timeout
                )
                
                return {
                    "success": returncode == 0,
                    "returncode": returncode,
                    "logs": []
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "returncode": -1,
                "error": f"Comando excedió timeout de {timeout}s",
                "logs": [f"Timeout ejecutando: {' '.join(command)}"]
            }

        except (OSError, subprocess.SubprocessError) as e:

            return {
                "success": False,
                "returncode": -1,
                "error": str(e),
                "logs": [f"Error ejecutando comando {' '.join(command)}: {e}"]
            }
    
    async def _wait_for_services_ready(self, project_path: Path, max_wait: int = 120):
        """Esperar que los servicios estén listos"""
        self.logger.info("⏳ Esperando que los servicios estén listos...")
        
        wait_time = 0
        while wait_time < max_wait:
            try:
                # Verificar health check de backend
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8000/health") as response:
                        if response.status == 200:
                            self.logger.info("✅ Backend listo")
                            return

            except (aiohttp.ClientError, ImportError):
                pass

            
            await asyncio.sleep(5)
            wait_time += 5
        
        raise TimeoutError("Servicios no estuvieron listos a tiempo")
    
    def _get_local_service_urls(self, project_path: Path) -> List[str]:
        """Obtener URLs de servicios locales"""
        urls = []
        
        # URLs por defecto basadas en docker-compose
        if (project_path / "backend").exists():
            urls.append("http://localhost:8000")
            urls.append("http://localhost:8000/docs")  # API docs
        
        if (project_path / "frontend").exists():
            urls.append("http://localhost:3000")
        
        return urls
    
    async def _get_running_services(self) -> Dict[str, str]:
        """Obtener servicios corriendo"""
        try:
            result = await self._run_command(
                ["docker-compose", "ps", "--services", "--filter", "status=running"]
            )
            
            if result["success"]:
                services = {}
                for service in result["stdout"].strip().split('\n'):
                    if service:
                        services[service] = "running"
                return services
            

        except (OSError, subprocess.SubprocessError):
            pass

        
        return {}
    
    async def _post_deployment_tasks(
        self, 
        project_path: Path, 
        config: DeploymentConfig, 
        result: DeploymentResult
    ):
        """Tareas post-despliegue"""
        self.logger.info("🔧 Ejecutando tareas post-despliegue")
        
        # Ejecutar migraciones de base de datos si es necesario
        if config.environment == DeploymentEnvironment.PRODUCTION:
            await self._run_database_migrations(project_path)
        
        # Configurar monitoreo si está habilitado
        if config.monitoring_enabled:
            await self._setup_monitoring(project_path, config)
        
        # Configurar backup si está habilitado
        if config.backup_enabled:
            await self._setup_backup(project_path, config)
        
        # Configurar SSL si está habilitado y hay dominio
        if config.ssl_enabled and config.domain:
            await self._setup_ssl(config.domain)
    
    # Handlers MCP
    async def _handle_deploy_project(self, request) -> Dict[str, Any]:
        """Handler para despliegue completo"""
        result = await self._deploy_complete_project(request.params)
        return {
            "success": result.success,
            "target": result.target.value,
            "environment": result.environment.value,
            "urls": result.urls,
            "services": result.services,
            "error": result.error
        }
    
    async def _handle_deploy_local(self, request) -> Dict[str, Any]:
        """Handler para despliegue local"""
        result = await self._deploy_to_local(request.params)
        return {
            "success": result.success,
            "urls": result.urls,
            "services": result.services,
            "error": result.error
        }
    
    async def _handle_deploy_cloud(self, request) -> Dict[str, Any]:
        """Handler para despliegue en cloud"""
        result = await self._deploy_to_cloud(request.params)
        return {
            "success": result.success,
            "urls": result.urls,
            "error": result.error
        }
    
    async def _handle_deploy_k8s(self, request) -> Dict[str, Any]:
        """Handler para despliegue en Kubernetes"""
        result = await self._deploy_to_kubernetes(request.params)
        return {
            "success": result.success,
            "urls": result.urls,
            "services": result.services,
            "error": result.error
        }
    
    async def _handle_rollback(self, request) -> Dict[str, Any]:
        """Handler para rollback"""
        result = await self._perform_rollback(request.params)
        return {"success": result}
    
    async def _handle_get_status(self, request) -> Dict[str, Any]:
        """Handler para obtener estado"""
        status = await self._get_deployment_status(request.params)
        return status
    
    # Métodos auxiliares (implementación simplificada)
    async def _check_deployment_tools(self):
        """Verificar herramientas de despliegue"""
        tools = ["docker", "docker-compose", "kubectl"]
        for tool in tools:
            try:
                result = await self._run_command([tool, "--version"])
                if result["success"]:
                    self.logger.debug(f"✅ {tool} disponible")
                else:
                    self.logger.warning(f"⚠️ {tool} no disponible")

            except (OSError, subprocess.SubprocessError):
                self.logger.warning(f"⚠️ {tool} no encontrado")

    
    async def _deploy_with_docker(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Desplegar con Docker"""
        # Similar a deploy_to_local pero sin docker-compose
        return await self._deploy_to_local({"project_path": project_path, "config": config})
    
    async def _deploy_to_heroku(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Desplegar en Heroku utilizando la CLI de Heroku."""
        self.logger.info("🚀 Deploying to Heroku")

        app_name = config.custom_config.get("app_name", project_path.name.replace("_", "-"))
        logs: List[str] = []

        try:
            create_result = await self._run_command(["heroku", "create", app_name])
            logs.extend(create_result.get("logs", []))
            if not create_result.get("success"):
                raise RuntimeError("Error creating Heroku app")

            remote_result = await self._run_command(["heroku", "git:remote", "-a", app_name])
            logs.extend(remote_result.get("logs", []))
            if not remote_result.get("success"):
                raise RuntimeError("Error configuring Heroku git remote")

            push_result = await self._run_command(["git", "push", "heroku", "HEAD:main"])
            logs.extend(push_result.get("logs", []))
            if not push_result.get("success"):
                raise RuntimeError("Error pushing code to Heroku")

            url = f"https://{app_name}.herokuapp.com"

            return DeploymentResult(
                success=True,
                target=DeploymentTarget.HEROKU,
                environment=config.environment,
                urls=[url],
                services={},
                logs=logs,
                rollback_available=True
            )


        except (OSError, RuntimeError, subprocess.SubprocessError, asyncio.TimeoutError) as e:
            self.logger.error(
                f"❌ Error en despliegue Heroku para {app_name}: {e}"
            )

            return DeploymentResult(
                success=False,
                target=DeploymentTarget.HEROKU,
                environment=config.environment,
                urls=[],
                services={},
                logs=logs + [f"Error: {str(e)}"],
                error=str(e)
            )
    
    async def _deploy_to_vercel(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Desplegar utilizando la CLI de Vercel."""
        self.logger.info("🚀 Deploying to Vercel")

        logs: List[str] = []

        try:
            deploy_result = await self._run_command(
                ["vercel", "deploy", "--prod", "--yes"],
                capture_output=True,
            )
            logs.extend(deploy_result.get("logs", []))
            if not deploy_result.get("success"):
                raise RuntimeError("Vercel deployment failed")

            url = deploy_result.get("stdout", "").strip().splitlines()[-1] if deploy_result.get("stdout") else ""

            return DeploymentResult(
                success=True,
                target=DeploymentTarget.VERCEL,
                environment=config.environment,
                urls=[url] if url else [],
                services={},
                logs=logs,
                rollback_available=True
            )


        except (OSError, RuntimeError, subprocess.SubprocessError, asyncio.TimeoutError) as e:
            self.logger.error(
                f"❌ Error en despliegue Vercel: {e}"
            )

            return DeploymentResult(
                success=False,
                target=DeploymentTarget.VERCEL,
                environment=config.environment,
                urls=[],
                services={},
                logs=logs + [f"Error: {str(e)}"],
                error=str(e)
            )
    
    async def _deploy_to_aws(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Desplegar en AWS mediante AWS CLI."""
        self.logger.info("🚀 Deploying to AWS")

        app_name = config.custom_config.get("app_name", project_path.name)
        bucket = config.custom_config.get("bucket", f"{app_name}-deploy")
        region = config.custom_config.get("region", "us-east-1")

        logs: List[str] = []
        archive_path: Optional[str] = None

        try:
            archive_base = project_path / "deploy_package"
            archive_path = shutil.make_archive(str(archive_base), "zip", project_path)

            upload_result = await self._run_command(
                [
                    "aws", "s3", "cp", archive_path, f"s3://{bucket}/{Path(archive_path).name}", "--region", region
                ]
            )
            logs.extend(upload_result.get("logs", []))
            if not upload_result.get("success"):
                raise RuntimeError("Error uploading package to S3")

            deploy_result = await self._run_command(
                [
                    "aws", "deploy", "create-deployment",
                    "--application-name", app_name,
                    "--deployment-group-name", config.environment.value,
                    "--s3-location", f"bucket={bucket},key={Path(archive_path).name},bundleType=zip",
                    "--region", region,
                ]
            )
            logs.extend(deploy_result.get("logs", []))
            if not deploy_result.get("success"):
                raise RuntimeError("Error creating AWS deployment")

            url = f"https://{region}.console.aws.amazon.com/codedeploy/home"

            return DeploymentResult(
                success=True,
                target=DeploymentTarget.AWS,
                environment=config.environment,
                urls=[url],
                services={},
                logs=logs,
                rollback_available=True
            )


        except (OSError, RuntimeError, subprocess.SubprocessError, asyncio.TimeoutError) as e:
            self.logger.error(
                f"❌ Error en despliegue AWS para {app_name}: {e}"
            )

            return DeploymentResult(
                success=False,
                target=DeploymentTarget.AWS,
                environment=config.environment,
                urls=[],
                services={},
                logs=logs + [f"Error: {str(e)}"],
                error=str(e),
            )
        finally:
            if archive_path and os.path.exists(archive_path):
                try:
                    os.remove(archive_path)

                except OSError:
                    pass

    
    async def _wait_for_k8s_pods_ready(self, project_path: Path):
        """Esperar que los pods de K8s estén listos"""
        self.logger.info("⏳ Esperando pods de Kubernetes...")
        wait_time = 0
        max_wait = 300
        while wait_time < max_wait:
            result = await self._run_command([
                "kubectl",
                "get",
                "pods",
                "-o",
                "json",
            ])

            if result.get("success"):
                try:
                    data = json.loads(result.get("stdout", ""))
                    items = data.get("items", [])
                    if items:
                        all_ready = True
                        for pod in items:
                            statuses = pod.get("status", {}).get(
                                "containerStatuses", []
                            )
                            for st in statuses:
                                if not st.get("ready"):
                                    all_ready = False
                                    break
                            if not all_ready:
                                break
                        if all_ready:
                            self.logger.info("✅ Pods listos")
                            return
                except json.JSONDecodeError:
                    pass

            await asyncio.sleep(5)
            wait_time += 5

        raise TimeoutError("Pods de Kubernetes no estuvieron listos a tiempo")
    
    async def _get_k8s_service_urls(self, project_path: Path) -> List[str]:
        """Obtener URLs de servicios de K8s"""
        result = await self._run_command([
            "kubectl",
            "get",
            "svc",
            "-o",
            "json",
        ])
        urls: List[str] = []
        if result.get("success"):
            try:
                data = json.loads(result.get("stdout", ""))
                for svc in data.get("items", []):
                    host = None
                    ingress = (
                        svc.get("status", {})
                        .get("loadBalancer", {})
                        .get("ingress", [])
                    )
                    if ingress:
                        host = ingress[0].get("hostname") or ingress[0].get("ip")
                    if not host:
                        host = svc.get("spec", {}).get("clusterIP")

                    for port in svc.get("spec", {}).get("ports", []):
                        port_num = port.get("nodePort") or port.get("port")
                        if host and port_num:
                            protocol = (
                                "https" if port_num == 443 else "http"
                            )
                            urls.append(f"{protocol}://{host}:{port_num}")
            except json.JSONDecodeError:
                pass

        return urls
    
    async def _get_k8s_services(self) -> Dict[str, str]:
        """Obtener servicios de K8s"""
        result = await self._run_command([
            "kubectl",
            "get",
            "pods",
            "-o",
            "json",
        ])
        services: Dict[str, str] = {}
        if result.get("success"):
            try:
                data = json.loads(result.get("stdout", ""))
                for pod in data.get("items", []):
                    name = pod.get("metadata", {}).get("name")
                    status = pod.get("status", {}).get("phase")
                    if name and status:
                        services[name] = status
            except json.JSONDecodeError:
                pass

        return services
    
    async def _run_database_migrations(self, project_path: Path):
        """Ejecutar migraciones de base de datos"""
        self.logger.info("🔄 Ejecutando migraciones de base de datos")
        backend_path = project_path / "backend"
        if (backend_path / "alembic.ini").exists():
            original_cwd = Path.cwd()
            os.chdir(backend_path)
            try:
                await self._run_command(["alembic", "upgrade", "head"])
            finally:
                os.chdir(original_cwd)
    
    async def _setup_monitoring(self, project_path: Path, config: DeploymentConfig):
        """Configurar monitoreo"""
        self.logger.info("📈 Configurando monitoreo")
        compose_file = project_path / "monitoring" / "docker-compose.yml"
        if compose_file.exists():
            await self._run_command([
                "docker-compose",
                "-f",
                str(compose_file),
                "up",
                "-d",
            ])
    
    async def _setup_backup(self, project_path: Path, config: DeploymentConfig):
        """Configurar backup"""
        self.logger.info("💾 Configurando backup")
        backup_script = project_path / "backup" / "backup.sh"
        if backup_script.exists():
            await self._run_command(["bash", str(backup_script)])
    
    async def _setup_ssl(self, domain: str):
        """Configurar SSL"""
        self.logger.info(f"🔒 Configurando SSL para {domain}")
        await self._run_command(
            [
                "certbot",
                "certonly",
                "--standalone",
                "--non-interactive",
                "--agree-tos",
                "-m",
                f"admin@{domain}",
                "-d",
                domain,
            ]
        )
    
    async def _perform_rollback(self, params: Dict[str, Any]) -> bool:
        """Realizar rollback"""
        target = params.get("target")
        environment = params.get("environment")
        project_path = Path(params.get("project_path", "./"))

        if not target or not environment:
            return False

        try:
            target_enum = DeploymentTarget(target)
            env_enum = DeploymentEnvironment(environment)
        except ValueError:
            return False

        deployment_id = f"{target_enum.value}_{env_enum.value}"
        if deployment_id not in self.active_deployments:
            return False

        self.logger.info(f"↩️  Rollback de {deployment_id}")
        try:
            if target_enum in [DeploymentTarget.LOCAL, DeploymentTarget.DOCKER]:
                await self._run_command(["docker-compose", "down"])
            elif target_enum == DeploymentTarget.KUBERNETES:
                k8s_dir = project_path / "k8s"
                if k8s_dir.exists():
                    await self._run_command(["kubectl", "delete", "-f", str(k8s_dir)])
        except Exception as e:  # pragma: no cover - rollback best effort
            self.logger.error(f"Error en rollback: {e}")

        self.active_deployments.pop(deployment_id, None)
        return True
    
    async def _get_deployment_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener estado del despliegue"""
        return {
            "active_deployments": len(self.active_deployments),
            "total_deployments": len(self.deployment_history),
            "deployments": list(self.active_deployments.keys())        }
