"""
Orquestador Central - Coordinador de agentes y flujo de trabajo

Este módulo es responsable de:
- Coordinar la comunicación entre agentes
- Gestionar el flujo de trabajo de creación de proyectos
- Manejar dependencias entre tareas
- Monitorear el progreso y estado de los agentes
- Ejecutar el pipeline completo de generación
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from genesis_engine.core.logging import get_logger

from genesis_engine.mcp.protocol import mcp_protocol, MCPProtocol
from genesis_engine.mcp.agent_base import AgentTask, TaskResult
from genesis_engine.agents.architect import ArchitectAgent
from genesis_engine.agents.backend import BackendAgent
# FrontendAgent is not implemented yet
# from genesis_engine.agents.devops import DevOpsAgent
from genesis_engine.core.project_manager import ProjectManager
from genesis_engine.cli.ui.console import genesis_console

class WorkflowStatus(str, Enum):
    """Estados del flujo de trabajo"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(int, Enum):
    """Prioridades de tareas"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class WorkflowStep:
    """Paso del flujo de trabajo"""
    id: str
    name: str
    agent_id: str
    task_name: str
    params: Dict[str, Any]
    dependencies: List[str]
    priority: TaskPriority
    status: WorkflowStatus
    result: Optional[TaskResult] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class ProjectCreationResult:
    """Resultado de creación de proyecto"""
    success: bool
    project_path: Optional[Path] = None
    generated_files: List[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.generated_files is None:
            self.generated_files = []
        if self.metadata is None:
            self.metadata = {}

class GenesisOrchestrator:
    """
    Orquestador Central de Genesis Engine
    
    Coordina la ejecución de agentes especializados para crear
    proyectos completos según las especificaciones del usuario.
    """
    
    def __init__(self):
        self.mcp = mcp_protocol
        self.project_manager = ProjectManager()
        self.logger = get_logger("genesis.orchestrator")
        
        # Agentes registrados
        self.agents: Dict[str, Any] = {}
        
        # Estado del workflow
        self.current_workflow: Optional[str] = None
        self.workflow_steps: Dict[str, WorkflowStep] = {}
        self.workflow_results: Dict[str, Any] = {}
        
        # Control de ejecución
        self.running = False
        self.cancelled = False
        
    
    async def initialize(self):
        """Inicializar el orquestador"""
        self.logger.info("🎼 Inicializando Genesis Orchestrator")
        
        # Inicializar protocolo MCP
        if not self.mcp.running:
            await self.mcp.start()
        
        # Registrar agentes especializados
        await self._register_agents()
        
        # Configurar handlers de eventos
        self._setup_event_handlers()
        
        self.running = True
        self.logger.info("✅ Orchestrator inicializado")
    
    async def _register_agents(self):
        """Registrar agentes especializados"""
        agents_to_register = [
            ArchitectAgent(),
            BackendAgent(),
            # FrontendAgent(),
            # DevOpsAgent(),
            # DeployAgent(),
            # PerformanceAgent(),
            # AIReadyAgent()
        ]
        
        for agent in agents_to_register:
            self.agents[agent.agent_id] = agent
            
            # Inicializar agente en background
            asyncio.create_task(agent.start())
            
            self.logger.info(f"🤖 Agente registrado: {agent.name}")
        
        # Esperar un momento para que los agentes se inicialicen
        await asyncio.sleep(2)
    
    def _setup_event_handlers(self):
        """Configurar handlers de eventos MCP"""
        self.mcp.register_handler("task.completed", self._handle_task_completed)
        self.mcp.register_handler("task.failed", self._handle_task_failed)
        self.mcp.register_handler("agent.status_changed", self._handle_agent_status_changed)

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar una solicitud simple dirigida a un agente.

        Este método se usa principalmente por la CLI sin necesidad de
        inicializar por completo el orquestador. Permite enviar
        acciones directas a un agente y obtener la respuesta de forma
        síncrona.
        """
        agent_key = request.get("agent")
        action = request.get("type")
        data = request.get("data", {})

        if not agent_key or not action:
            return {"success": False, "error": "Invalid request"}

        agent_map = {
            "architect": ArchitectAgent,
            "backend": BackendAgent,
        }

        agent = self.agents.get(agent_key)
        if not agent:
            agent_cls = agent_map.get(agent_key)
            if not agent_cls:
                return {"success": False, "error": f"Unknown agent '{agent_key}'"}
            agent = agent_cls()
            self.agents[agent_key] = agent

        task = AgentTask(id=str(uuid.uuid4()), name=action, params=data)
        try:
            result = asyncio.run(agent.execute_task(task))
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_project(self, config: Dict[str, Any]) -> ProjectCreationResult:
        """
        Crear proyecto completo
        
        Args:
            config: Configuración del proyecto
            
        Returns:
            Resultado de la creación
        """
        self.logger.info(f"🚀 Iniciando creación de proyecto: {config.get('name', 'unknown')}")
        
        try:
            # Generar ID único para el workflow
            workflow_id = str(uuid.uuid4())
            self.current_workflow = workflow_id
            
            # Crear directorio del proyecto
            project_path = await self._setup_project_directory(config)
            
            # Definir flujo de trabajo
            workflow_steps = self._define_workflow_steps(config, project_path)
            
            # Ejecutar workflow
            result = await self._execute_workflow(workflow_steps, config)
            
            if result.success:
                # Finalizar proyecto
                await self._finalize_project(project_path, result)
                
                self.logger.info("✅ Proyecto creado exitosamente")
                return ProjectCreationResult(
                    success=True,
                    project_path=project_path,
                    generated_files=result.generated_files,
                    metadata=result.metadata
                )
            else:
                self.logger.error(f"❌ Error creando proyecto: {result.error}")
                return ProjectCreationResult(
                    success=False,
                    error=result.error
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {str(e)}")
            return ProjectCreationResult(
                success=False,
                error=f"Error inesperado: {str(e)}"
            )
        finally:
            self.current_workflow = None
            self.workflow_steps.clear()
            self.workflow_results.clear()
    
    async def _setup_project_directory(self, config: Dict[str, Any]) -> Path:
        """Configurar directorio del proyecto"""
        project_name = config.get("name", "genesis_project")
        base_path = Path.cwd() / project_name
        
        # Crear directorio si no existe
        base_path.mkdir(exist_ok=True)
        
        # Inicializar gestión del proyecto
        await self.project_manager.initialize_project(base_path, config)
        
        return base_path
    
    def _define_workflow_steps(
        self, 
        config: Dict[str, Any], 
        project_path: Path
    ) -> List[WorkflowStep]:
        """Definir pasos del flujo de trabajo"""
        steps = []
        
        # 1. Análisis de requisitos (Architect Agent)
        steps.append(WorkflowStep(
            id="analyze_requirements",
            name="Analizar Requisitos",
            agent_id="architect_agent",
            task_name="analyze_requirements",
            params={
                "description": config.get("description", ""),
                "type": config.get("template", "web_app"),
                "features": config.get("features", []),
                "constraints": config.get("constraints", {})
            },
            dependencies=[],
            priority=TaskPriority.CRITICAL,
            status=WorkflowStatus.PENDING
        ))
        
        # 2. Diseño de arquitectura (Architect Agent)
        steps.append(WorkflowStep(
            id="design_architecture",
            name="Diseñar Arquitectura",
            agent_id="architect_agent",
            task_name="design_architecture",
            params={
                "requirements": "{{analyze_requirements.result}}",
                "pattern": config.get("architecture_pattern", "layered"),
                "type": config.get("template", "web_app")
            },
            dependencies=["analyze_requirements"],
            priority=TaskPriority.CRITICAL,
            status=WorkflowStatus.PENDING
        ))
        
        # 3. Generación de schema (Architect Agent)
        steps.append(WorkflowStep(
            id="generate_schema",
            name="Generar Schema del Proyecto",
            agent_id="architect_agent",
            task_name="generate_schema",
            params={
                "name": config.get("name"),
                "description": config.get("description", ""),
                "requirements": "{{analyze_requirements.result}}",
                "architecture": "{{design_architecture.result}}",
                "stack": config.get("stack", {})
            },
            dependencies=["analyze_requirements", "design_architecture"],
            priority=TaskPriority.CRITICAL,
            status=WorkflowStatus.PENDING
        ))
        
        # 4. Generación de backend (Backend Agent)
        steps.append(WorkflowStep(
            id="generate_backend",
            name="Generar Backend",
            agent_id="backend_agent",
            task_name="generate_backend",
            params={
                "schema": "{{generate_schema.result}}",
                "stack": config.get("stack", {}),
                "output_path": str(project_path / "backend")
            },
            dependencies=["generate_schema"],
            priority=TaskPriority.HIGH,
            status=WorkflowStatus.PENDING
        ))
        
        # 5. Generación de frontend (Frontend Agent)
        steps.append(WorkflowStep(
            id="generate_frontend",
            name="Generar Frontend",
            agent_id="frontend_agent",
            task_name="generate_frontend",
            params={
                "schema": "{{generate_schema.result}}",
                "stack": config.get("stack", {}),
                "output_path": str(project_path / "frontend")
            },
            dependencies=["generate_schema"],
            priority=TaskPriority.HIGH,
            status=WorkflowStatus.PENDING
        ))
        
        # 6. Configuración DevOps (si está habilitado)
        if config.get("enable_devops", True):
            steps.append(WorkflowStep(
                id="setup_devops",
                name="Configurar DevOps",
                agent_id="devops_agent",
                task_name="setup_devops",
                params={
                    "schema": "{{generate_schema.result}}",
                    "backend_result": "{{generate_backend.result}}",
                    "frontend_result": "{{generate_frontend.result}}",
                    "output_path": str(project_path)
                },
                dependencies=["generate_backend", "generate_frontend"],
                priority=TaskPriority.NORMAL,
                status=WorkflowStatus.PENDING
            ))
        
        return steps
    
    async def _execute_workflow(
        self, 
        steps: List[WorkflowStep], 
        config: Dict[str, Any]
    ) -> ProjectCreationResult:
        """Ejecutar flujo de trabajo"""
        self.workflow_steps = {step.id: step for step in steps}
        
        # Mostrar progreso inicial
        genesis_console.print(f"📋 Ejecutando {len(steps)} pasos del workflow")
        
        completed_steps = set()
        all_generated_files = []
        
        while len(completed_steps) < len(steps) and not self.cancelled:
            # Encontrar pasos listos para ejecutar
            ready_steps = self._get_ready_steps(completed_steps)
            
            if not ready_steps:
                self.logger.error("❌ No hay pasos listos para ejecutar - posible dependencia circular")
                return ProjectCreationResult(
                    success=False,
                    error="Dependencia circular en workflow"
                )
            
            # Ejecutar pasos en paralelo (respetando prioridades)
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(self._execute_step(step))
                tasks.append((step.id, task))
            
            # Esperar completación de tareas
            for step_id, task in tasks:
                try:
                    result = await task
                    step = self.workflow_steps[step_id]
                    
                    if result.success:
                        step.status = WorkflowStatus.COMPLETED
                        step.result = result
                        step.end_time = datetime.utcnow()
                        completed_steps.add(step_id)
                        
                        # Agregar archivos generados
                        if hasattr(result, 'result') and isinstance(result.result, dict):
                            files = result.result.get('generated_files', [])
                            all_generated_files.extend(files)
                        
                        genesis_console.print(f"✅ {step.name} completado")
                    else:
                        step.status = WorkflowStatus.FAILED
                        step.end_time = datetime.utcnow()
                        
                        genesis_console.print(f"❌ {step.name} falló: {result.error}")
                        return ProjectCreationResult(
                            success=False,
                            error=f"Paso '{step.name}' falló: {result.error}"
                        )
                        
                except Exception as e:
                    self.logger.error(f"❌ Error ejecutando paso {step_id}: {e}")
                    return ProjectCreationResult(
                        success=False,
                        error=f"Error ejecutando paso '{step_id}': {str(e)}"
                    )
        
        if self.cancelled:
            return ProjectCreationResult(
                success=False,
                error="Workflow cancelado por el usuario"
            )
        
        return ProjectCreationResult(
            success=True,
            generated_files=all_generated_files,
            metadata={
                "workflow_id": self.current_workflow,
                "completed_steps": len(completed_steps),
                "total_steps": len(steps),
                "execution_time": self._calculate_execution_time()
            }
        )
    
    def _get_ready_steps(self, completed_steps: set) -> List[WorkflowStep]:
        """Obtener pasos listos para ejecutar"""
        ready_steps = []
        
        for step in self.workflow_steps.values():
            if (step.status == WorkflowStatus.PENDING and 
                all(dep in completed_steps for dep in step.dependencies)):
                ready_steps.append(step)
        
        # Ordenar por prioridad
        ready_steps.sort(key=lambda s: s.priority.value, reverse=True)
        
        return ready_steps
    
    async def _execute_step(self, step: WorkflowStep) -> TaskResult:
        """Ejecutar un paso del workflow"""
        step.status = WorkflowStatus.RUNNING
        step.start_time = datetime.utcnow()
        
        self.logger.info(f"🔄 Ejecutando: {step.name}")
        
        try:
            # Resolver parámetros con resultados de pasos anteriores
            resolved_params = self._resolve_step_parameters(step.params)
            
            # Crear tarea para el agente
            task = AgentTask(
                id=step.id,
                name=step.task_name,
                description=step.name,
                params=resolved_params,
                priority=step.priority.value
            )
            
            # Enviar solicitud al agente
            response = await self.mcp.send_request(
                sender_id="orchestrator",
                target_id=step.agent_id,
                action="task.execute",
                data={
                    "task_id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "params": task.params,
                    "priority": task.priority
                }
            )
            
            if response.success:
                return TaskResult(
                    task_id=step.id,
                    success=True,
                    result=response.result
                )
            else:
                return TaskResult(
                    task_id=step.id,
                    success=False,
                    error=response.error
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando paso {step.name}: {e}")
            return TaskResult(
                task_id=step.id,
                success=False,
                error=str(e)
            )
    
    def _resolve_step_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolver parámetros con resultados de pasos anteriores"""
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Extractar referencia a resultado anterior
                ref = value[2:-2].strip()  # Remover {{ }}
                
                if "." in ref:
                    step_id, result_key = ref.split(".", 1)
                    
                    if step_id in self.workflow_steps:
                        step = self.workflow_steps[step_id]
                        if step.result and step.result.success:
                            result_data = step.result.result
                            if isinstance(result_data, dict) and result_key in result_data:
                                resolved[key] = result_data[result_key]
                            else:
                                resolved[key] = result_data
                        else:
                            resolved[key] = None
                    else:
                        resolved[key] = value
                else:
                    # Referencia directa a resultado completo
                    if ref in self.workflow_steps:
                        step = self.workflow_steps[ref]
                        resolved[key] = step.result.result if step.result else None
                    else:
                        resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    async def _finalize_project(self, project_path: Path, result: ProjectCreationResult):
        """Finalizar configuración del proyecto"""
        # Generar archivo de metadata del proyecto
        metadata = {
            "name": project_path.name,
            "generated_at": datetime.utcnow().isoformat(),
            "generator": "Genesis Engine",
            "version": "1.0.0",
            "workflow_id": self.current_workflow,
            "generated_files": result.generated_files,
            "metadata": result.metadata
        }
        
        metadata_file = project_path / "genesis.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Generar README del proyecto
        readme_content = self._generate_project_readme(metadata)
        readme_file = project_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        self.logger.info(f"📝 Proyecto finalizado en: {project_path}")
    
    def _generate_project_readme(self, metadata: Dict[str, Any]) -> str:
        """Generar README del proyecto"""
        return f"""# {metadata['name']}

Proyecto generado por Genesis Engine el {metadata['generated_at']}

## Estructura del Proyecto

Este proyecto fue generado automáticamente e incluye:

- Backend completo con APIs REST
- Frontend moderno y responsivo  
- Configuración de base de datos
- Archivos de despliegue
- Documentación de API

## Siguientes Pasos

1. Revisar la configuración en cada directorio
2. Instalar dependencias según las instrucciones
3. Configurar variables de entorno
4. Ejecutar migraciones de base de datos
5. Iniciar los servicios en modo desarrollo

## Información Técnica

- **Generator**: Genesis Engine v1.0.0
- **Workflow ID**: {metadata['workflow_id']}
- **Archivos generados**: {len(metadata.get('generated_files', []))}

---

Generado con ❤️ por Genesis Engine
"""
    
    def _calculate_execution_time(self) -> float:
        """Calcular tiempo total de ejecución"""
        start_times = [step.start_time for step in self.workflow_steps.values() 
                      if step.start_time]
        end_times = [step.end_time for step in self.workflow_steps.values() 
                    if step.end_time]
        
        if start_times and end_times:
            return (max(end_times) - min(start_times)).total_seconds()
        
        return 0.0
    
    async def cancel_workflow(self):
        """Cancelar workflow en ejecución"""
        self.cancelled = True
        self.logger.info("🛑 Workflow cancelado")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Obtener estado del workflow"""
        if not self.current_workflow:
            return {"status": "idle", "workflow_id": None}
        
        total_steps = len(self.workflow_steps)
        completed_steps = sum(1 for step in self.workflow_steps.values() 
                            if step.status == WorkflowStatus.COMPLETED)
        
        return {
            "status": "running" if self.running else "idle",
            "workflow_id": self.current_workflow,
            "progress": {
                "completed": completed_steps,
                "total": total_steps,
                "percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0
            },
            "steps": {
                step_id: {
                    "name": step.name,
                    "status": step.status.value,
                    "agent": step.agent_id
                }
                for step_id, step in self.workflow_steps.items()
            }
        }
    
    # Event handlers
    async def _handle_task_completed(self, event: Dict[str, Any]):
        """Manejar tarea completada"""
        pass
    
    async def _handle_task_failed(self, event: Dict[str, Any]):
        """Manejar tarea fallida"""
        pass
    
    async def _handle_agent_status_changed(self, event: Dict[str, Any]):
        """Manejar cambio de estado de agente"""
        pass
    
    async def shutdown(self):
        """Detener el orquestador"""
        self.running = False
        
        # Detener agentes
        for agent in self.agents.values():
            await agent.stop()
        
        # Detener protocolo MCP
        await self.mcp.stop()
        
        self.logger.info("🛑 Orchestrator detenido")