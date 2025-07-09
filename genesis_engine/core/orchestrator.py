"""
Orquestrador Central - Coordinador de agentes y flujo de trabajo

Este módulo es responsable de:
- Coordinar la comunicación entre agentes
- Gestionar el flujo de trabajo de creación de proyectos
- Manejar dependencias entre tareas
- Monitorear el progreso y estado de los agentes
- Ejecutar el pipeline completo de generación
- Implementar retry logic y circuit breakers
- Persistir estado del workflow
- Proporcionar rollback capabilities
"""

import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback
from collections import defaultdict

# Imports de Genesis Engine
from genesis_engine.core.logging import get_logger
from genesis_engine.core.exceptions import GenesisException, ProjectCreationError
from genesis_engine.mcp.protocol import mcp_protocol, MCPProtocol
from genesis_engine.mcp.agent_base import AgentTask, TaskResult

# Imports de agentes - con manejo de errores
try:
    from genesis_engine.agents.architect import ArchitectAgent
except ImportError as e:
    print(f"Warning: Could not import ArchitectAgent: {e}")
    ArchitectAgent = None

try:
    from genesis_engine.agents.backend import BackendAgent
except ImportError as e:
    print(f"Warning: Could not import BackendAgent: {e}")
    BackendAgent = None

try:
    from genesis_engine.agents.frontend import FrontendAgent
except ImportError as e:
    print(f"Warning: Could not import FrontendAgent: {e}")
    FrontendAgent = None

try:
    from genesis_engine.agents.devops import DevOpsAgent
except ImportError as e:
    print(f"Warning: Could not import DevOpsAgent: {e}")
    DevOpsAgent = None

try:
    from genesis_engine.agents.deploy import DeployAgent
except ImportError as e:
    print(f"Warning: Could not import DeployAgent: {e}")
    DeployAgent = None

try:
    from genesis_engine.agents.performance import PerformanceAgent
except ImportError as e:
    print(f"Warning: Could not import PerformanceAgent: {e}")
    PerformanceAgent = None

try:
    from genesis_engine.agents.ai_ready import AIReadyAgent
except ImportError as e:
    print(f"Warning: Could not import AIReadyAgent: {e}")
    AIReadyAgent = None

try:
    from genesis_engine.core.project_manager import ProjectManager
except ImportError as e:
    print(f"Warning: Could not import ProjectManager: {e}")
    ProjectManager = None

try:
    from genesis_engine.cli.ui.console import genesis_console
except ImportError as e:
    print(f"Warning: Could not import genesis_console: {e}")
    # Crear un console básico como fallback
    try:
        from rich.console import Console
        genesis_console = Console()
    except ImportError:
        # Fallback básico
        class BasicConsole:
            def print(self, *args, **kwargs):
                print(*args)
        genesis_console = BasicConsole()


class WorkflowStatus(str, Enum):
    """Estados del flujo de trabajo"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(int, Enum):
    """Prioridades de tareas"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class CircuitBreakerState(str, Enum):
    """Estados del circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryConfig:
    """Configuración de retry"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreaker:
    """Circuit breaker para agentes"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    
    def should_allow_request(self) -> bool:
        """Verificar si se debe permitir la solicitud"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and \
               datetime.utcnow() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False
    
    def record_success(self):
        """Registrar éxito"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = None
    
    def record_failure(self):
        """Registrar fallo"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


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
    retry_count: int = 0
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    timeout: int = 300  # 5 minutos por defecto
    rollback_actions: List[str] = field(default_factory=list)


@dataclass
class ProjectCreationResult:
    """Resultado de creación de proyecto"""
    success: bool
    project_path: Optional[Path] = None
    generated_files: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    rollback_data: Dict[str, Any] = field(default_factory=dict)


class GenesisOrchestrator:
    """
    Orquestrador Central de Genesis Engine
    
    Coordina la ejecución de agentes especializados para crear
    proyectos completos según las especificaciones del usuario.
    """
    
    def __init__(self):
        self.mcp = mcp_protocol
        
        # Inicializar ProjectManager solo si está disponible
        if ProjectManager is not None:
            self.project_manager = ProjectManager()
        else:
            self.project_manager = None
            
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
        
        # Circuit breakers por agente
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Configuración de timeouts
        self.default_timeout = 300  # 5 minutos
        self.max_concurrent_tasks = 3
        
        # Persistence
        self.state_file: Optional[Path] = None
        self.rollback_stack: List[Dict[str, Any]] = []
        
        # Métricas
        self.metrics = {
            "tasks_executed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "circuit_breaker_trips": 0,
            "average_execution_time": 0.0
        }

    async def start(self):
        """Wrapper asincrónico para inicializar el orquestador"""
        await self.initialize()

    async def stop(self):
        """Wrapper asincrónico para detener el orquestador"""
        await self.shutdown()
    
    async def initialize(self):
        """Inicializar el orquestador"""
        self.logger.info("🎼 Inicializando Genesis Orchestrator")
        
        try:
            # Inicializar protocolo MCP
            if not self.mcp.running:
                await self.mcp.start()
            
            # Registrar agentes especializados
            await self._register_agents()
            
            # Configurar handlers de eventos
            self._setup_event_handlers()
            
            # Configurar circuit breakers
            self._setup_circuit_breakers()
            
            self.running = True
            self.logger.info("✅ Orchestrator inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando orchestrator: {e}")
            raise GenesisException(f"Error inicializando orchestrator: {e}")
    
    async def _register_agents(self):
        """Registrar agentes especializados"""
        agents_to_register = []
        
        # Registrar solo agentes que se importaron correctamente
        if ArchitectAgent is not None:
            agents_to_register.append(ArchitectAgent())
        else:
            self.logger.warning("ArchitectAgent no disponible")
        
        if BackendAgent is not None:
            agents_to_register.append(BackendAgent())
        else:
            self.logger.warning("BackendAgent no disponible")
        
        if FrontendAgent is not None:
            agents_to_register.append(FrontendAgent())
        else:
            self.logger.warning("FrontendAgent no disponible")
        
        if DevOpsAgent is not None:
            agents_to_register.append(DevOpsAgent())
        else:
            self.logger.warning("DevOpsAgent no disponible")
        
        if DeployAgent is not None:
            agents_to_register.append(DeployAgent())
        else:
            self.logger.warning("DeployAgent no disponible")
        
        if PerformanceAgent is not None:
            agents_to_register.append(PerformanceAgent())
        else:
            self.logger.warning("PerformanceAgent no disponible")
        
        if AIReadyAgent is not None:
            agents_to_register.append(AIReadyAgent())
        else:
            self.logger.warning("AIReadyAgent no disponible")
        
        for agent in agents_to_register:
            try:
                self.agents[agent.agent_id] = agent
                
                # Registrar en MCP
                self.mcp.register_agent(agent)
                
                # Inicializar agente en background
                asyncio.create_task(agent.start())
                
                self.logger.info(f"🤖 Agente registrado: {agent.name}")
                
            except Exception as e:
                self.logger.error(f"❌ Error registrando agente {agent.name}: {e}")
                # No lanzar excepción, solo continuar con otros agentes
        
        # Esperar inicialización de agentes
        await asyncio.sleep(2)
        
        self.logger.info(f"✅ {len(agents_to_register)} agentes registrados")
    
    def _setup_event_handlers(self):
        """Configurar handlers de eventos MCP"""
        self.mcp.subscribe_to_broadcasts("task.completed", self._handle_task_completed)
        self.mcp.subscribe_to_broadcasts("task.failed", self._handle_task_failed)
        self.mcp.subscribe_to_broadcasts("agent.status_changed", self._handle_agent_status_changed)
        self.mcp.subscribe_to_broadcasts("workflow.cancelled", self._handle_workflow_cancelled)
    
    def _setup_circuit_breakers(self):
        """Configurar circuit breakers para agentes"""
        for agent_id in self.agents.keys():
            self.circuit_breakers[agent_id] = CircuitBreaker(
                failure_threshold=3,
                recovery_timeout=60
            )
    
    def _handle_orchestrator_error(self, error: Exception, context: str) -> None:
        """Manejar errores del orquestador de manera uniforme"""
        error_msg = f"Error en {context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        
        # Broadcast error event
        if self.mcp and self.mcp.running:
            try:
                self.mcp.broadcast(
                    sender_id="orchestrator",
                    event="error_occurred",
                    data={
                        "context": context,
                        "error": str(error),
                        "timestamp": datetime.utcnow().isoformat(),
                        "workflow_id": self.current_workflow
                    }
                )
            except Exception as broadcast_error:
                self.logger.error(f"Failed to broadcast error: {broadcast_error}")
    
    def _validate_project_config(self, config: Dict[str, Any]) -> bool:
        """Validar configuración del proyecto"""
        required_fields = ["name"]
        
        for field in required_fields:
            if field not in config:
                raise GenesisException(f"Campo requerido faltante: {field}")
        
        # Validar nombre del proyecto
        name = config["name"]
        if not isinstance(name, str) or len(name) < 1:
            raise GenesisException("Nombre del proyecto inválido")
        
        # Validar template
        template = config.get("template", "saas-basic")
        valid_templates = ["saas-basic", "microservices", "ai-ready"]
        if template not in valid_templates:
            raise GenesisException(f"Template inválido: {template}")
        
        # Validar features
        features = config.get("features", [])
        if not isinstance(features, list):
            raise GenesisException("Features debe ser una lista")
        
        return True
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar una solicitud simple dirigida a un agente"""
        agent_key = request.get("agent")
        action = request.get("type")
        data = request.get("data", {})

        if not agent_key or not action:
            return {"success": False, "error": "Invalid request format"}

        agent_map = {
            "architect": ArchitectAgent,
            "backend": BackendAgent,
            "frontend": FrontendAgent,
            "devops": DevOpsAgent,
            "deploy": DeployAgent,
            "performance": PerformanceAgent,
            "ai_ready": AIReadyAgent,
        }

        # Obtener o crear agente
        agent = self.agents.get(agent_key)
        if not agent:
            agent_cls = agent_map.get(agent_key)
            if not agent_cls:
                return {"success": False, "error": f"Unknown agent '{agent_key}'"}
            
            try:
                agent = agent_cls()
                self.agents[agent_key] = agent
            except Exception as e:
                return {"success": False, "error": f"Error creating agent: {e}"}

        # Ejecutar tarea
        task = AgentTask(id=str(uuid.uuid4()), name=action, params=data)
        try:
            result = agent.execute_task(task)
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"Error executing task {action} on {agent_key}: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_project(self, config: Dict[str, Any]) -> ProjectCreationResult:
        """
        Crear proyecto completo
        
        Args:
            config: Configuración del proyecto
            
        Returns:
            Resultado de la creación
        """
        start_time = time.time()
        self.logger.info(f"🚀 Iniciando creación de proyecto: {config.get('name', 'unknown')}")
        
        try:
            # Validar configuración
            self._validate_project_config(config)
            
            # Generar ID único para el workflow
            workflow_id = str(uuid.uuid4())
            self.current_workflow = workflow_id
            
            # Configurar persistence
            self._setup_persistence(config)
            
            # Crear directorio del proyecto
            project_path = await self._setup_project_directory(config)
            
            # Definir flujo de trabajo
            workflow_steps = self._define_workflow_steps(config, project_path)
            
            # Guardar estado inicial
            await self._save_workflow_state()
            
            # Ejecutar workflow
            result = await self._execute_workflow(workflow_steps, config)
            
            # Actualizar métricas
            execution_time = time.time() - start_time
            self.metrics["average_execution_time"] = execution_time
            
            if result.success:
                # Finalizar proyecto
                await self._finalize_project(project_path, result)
                
                # Limpiar estado de persistence
                await self._cleanup_persistence()
                
                self.logger.info(f"✅ Proyecto creado exitosamente en {execution_time:.2f}s")
                return ProjectCreationResult(
                    success=True,
                    project_path=project_path,
                    generated_files=result.generated_files,
                    metadata={
                        **result.metadata,
                        "execution_time": execution_time,
                        "workflow_id": workflow_id
                    }
                )
            else:
                self.logger.error(f"❌ Error creando proyecto: {result.error}")
                
                # Intentar rollback
                await self._rollback_workflow()
                
                return ProjectCreationResult(
                    success=False,
                    error=result.error,
                    rollback_data=result.rollback_data
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {str(e)}")
            
            # Intentar rollback
            await self._rollback_workflow()
            
            return ProjectCreationResult(
                success=False,
                error=f"Error inesperado: {str(e)}"
            )
        finally:
            self.current_workflow = None
            self.workflow_steps.clear()
            self.workflow_results.clear()
            self.rollback_stack.clear()
    
    def _setup_persistence(self, config: Dict[str, Any]):
        """Configurar persistence del workflow"""
        project_name = config.get("name", "unknown")
        temp_dir = Path.home() / ".genesis" / "workflows"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = temp_dir / f"{project_name}_{self.current_workflow}.json"
    
    async def _save_workflow_state(self):
        """Guardar estado del workflow"""
        if not self.state_file:
            return
        
        state = {
            "workflow_id": self.current_workflow,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "running",
            "steps": {
                step_id: {
                    "id": step.id,
                    "name": step.name,
                    "agent_id": step.agent_id,
                    "task_name": step.task_name,
                    "status": step.status.value,
                    "retry_count": step.retry_count,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None
                }
                for step_id, step in self.workflow_steps.items()
            },
            "results": self.workflow_results,
            "rollback_stack": self.rollback_stack
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Error guardando estado: {e}")
    
    async def _load_workflow_state(self) -> Optional[Dict[str, Any]]:
        """Cargar estado del workflow"""
        if not self.state_file or not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Error cargando estado: {e}")
            return None
    
    async def _cleanup_persistence(self):
        """Limpiar archivos de persistence"""
        if self.state_file and self.state_file.exists():
            try:
                self.state_file.unlink()
            except Exception as e:
                self.logger.warning(f"Error limpiando persistence: {e}")
    
    async def _rollback_workflow(self):
        """Realizar rollback del workflow"""
        self.logger.info("🔄 Iniciando rollback del workflow")
        
        # Ejecutar acciones de rollback en orden inverso
        for rollback_action in reversed(self.rollback_stack):
            try:
                await self._execute_rollback_action(rollback_action)
            except Exception as e:
                self.logger.error(f"Error en rollback: {e}")
        
        self.rollback_stack.clear()
        self.logger.info("✅ Rollback completado")
    
    async def _execute_rollback_action(self, action: Dict[str, Any]):
        """Ejecutar una acción de rollback"""
        action_type = action.get("type")
        
        if action_type == "delete_file":
            file_path = Path(action["path"])
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Rollback: Eliminado archivo {file_path}")
        
        elif action_type == "delete_directory":
            dir_path = Path(action["path"])
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
                self.logger.info(f"Rollback: Eliminado directorio {dir_path}")
        
        elif action_type == "restore_file":
            # Restaurar archivo desde backup
            backup_path = Path(action["backup_path"])
            original_path = Path(action["original_path"])
            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, original_path)
                self.logger.info(f"Rollback: Restaurado archivo {original_path}")
    
    async def _setup_project_directory(self, config: Dict[str, Any]) -> Path:
        """Configurar directorio del proyecto"""
        project_name = config.get("name", "genesis_project")
        output_path = Path(config.get("output_path", "."))
        project_path = output_path / project_name
        
        # Agregar acción de rollback
        if not project_path.exists():
            self.rollback_stack.append({
                "type": "delete_directory",
                "path": str(project_path)
            })
        
        # Crear directorio
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar gestión del proyecto si está disponible
        if self.project_manager is not None:
            await self.project_manager.initialize_project(project_path, config)
        else:
            self.logger.warning("ProjectManager no disponible, creando estructura básica")
            # Crear estructura básica manualmente
            (project_path / "backend").mkdir(exist_ok=True)
            (project_path / "frontend").mkdir(exist_ok=True)
            (project_path / "docs").mkdir(exist_ok=True)
        
        return project_path
    
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
            status=WorkflowStatus.PENDING,
            timeout=120,
            retry_config=RetryConfig(max_attempts=3, initial_delay=2.0)
        ))
        
        # 2. Diseño de arquitectura (Architect Agent)
        steps.append(WorkflowStep(
            id="design_architecture",
            name="Diseñar Arquitectura",
            agent_id="architect_agent",
            task_name="design_architecture",
            params={
                "requirements": "{{analyze_requirements}}",
                "pattern": config.get("architecture_pattern", "layered"),
                "type": config.get("template", "web_app")
            },
            dependencies=["analyze_requirements"],
            priority=TaskPriority.CRITICAL,
            status=WorkflowStatus.PENDING,
            timeout=180,
            retry_config=RetryConfig(max_attempts=2, initial_delay=3.0)
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
                "requirements": "{{analyze_requirements}}",
                "architecture": "{{design_architecture}}",
                "stack": config.get("stack", {})
            },
            dependencies=["analyze_requirements", "design_architecture"],
            priority=TaskPriority.CRITICAL,
            status=WorkflowStatus.PENDING,
            timeout=240,
            retry_config=RetryConfig(max_attempts=2, initial_delay=2.0)
        ))
        
        # 4. Generación de backend (Backend Agent)
        steps.append(WorkflowStep(
            id="generate_backend",
            name="Generar Backend",
            agent_id="backend_agent",
            task_name="generate_backend",
            params={
                "schema": "{{generate_schema}}",
                "stack": config.get("stack", {}),
                "output_path": str(project_path / "backend")
            },
            dependencies=["generate_schema"],
            priority=TaskPriority.HIGH,
            status=WorkflowStatus.PENDING,
            timeout=300,
            retry_config=RetryConfig(max_attempts=3, initial_delay=5.0)
        ))
        
        # 5. Generación de frontend (Frontend Agent)
        steps.append(WorkflowStep(
            id="generate_frontend",
            name="Generar Frontend",
            agent_id="frontend_agent",
            task_name="generate_frontend",
            params={
                "schema": "{{generate_schema}}",
                "stack": config.get("stack", {}),
                "output_path": str(project_path / "frontend")
            },
            dependencies=["generate_schema"],
            priority=TaskPriority.HIGH,
            status=WorkflowStatus.PENDING,
            timeout=300,
            retry_config=RetryConfig(max_attempts=3, initial_delay=5.0)
        ))
        
        # 6. Configuración DevOps (si está habilitado)
        if config.get("enable_devops", True):
            steps.append(WorkflowStep(
                id="setup_devops",
                name="Configurar DevOps",
                agent_id="devops_agent",
                task_name="setup_devops",
                params={
                    "schema": "{{generate_schema}}",
                    "backend_result": "{{generate_backend}}",
                    "frontend_result": "{{generate_frontend}}",
                    "output_path": str(project_path)
                },
                dependencies=["generate_backend", "generate_frontend"],
                priority=TaskPriority.NORMAL,
                status=WorkflowStatus.PENDING,
                timeout=240,
                retry_config=RetryConfig(max_attempts=2, initial_delay=3.0)
            ))
        
        return steps
    
    async def _execute_workflow(
        self, 
        steps: List[WorkflowStep], 
        config: Dict[str, Any]
    ) -> ProjectCreationResult:
        """Ejecutar flujo de trabajo con retry logic y circuit breakers"""
        self.workflow_steps = {step.id: step for step in steps}
        
        genesis_console.print(f"📋 Ejecutando {len(steps)} pasos del workflow")
        
        completed_steps = set()
        all_generated_files = []
        
        while len(completed_steps) < len(steps) and not self.cancelled:
            # Guardar estado
            await self._save_workflow_state()
            
            # Encontrar pasos listos para ejecutar
            ready_steps = self._get_ready_steps(completed_steps)
            
            if not ready_steps:
                if len(completed_steps) == 0:
                    self.logger.error("❌ No hay pasos listos para ejecutar")
                    return ProjectCreationResult(
                        success=False,
                        error="No hay pasos listos para ejecutar"
                    )
                else:
                    # Esperar a que se completen tareas en progreso
                    await asyncio.sleep(1)
                    continue
            
            # Ejecutar pasos en paralelo (limitado por max_concurrent_tasks)
            semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
            tasks = []
            
            for step in ready_steps:
                task = asyncio.create_task(
                    self._execute_step_with_retry(step, semaphore)
                )
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
                        
                        # Registrar éxito en circuit breaker
                        if step.agent_id in self.circuit_breakers:
                            self.circuit_breakers[step.agent_id].record_success()
                        
                        # Agregar archivos generados
                        if hasattr(result, 'result') and isinstance(result.result, dict):
                            files = result.result.get('generated_files', [])
                            all_generated_files.extend(files)
                        
                        # Actualizar métricas
                        self.metrics["tasks_executed"] += 1
                        
                        genesis_console.print(f"✅ {step.name} completado")
                        
                    else:
                        step.status = WorkflowStatus.FAILED
                        step.end_time = datetime.utcnow()
                        
                        # Registrar fallo en circuit breaker
                        if step.agent_id in self.circuit_breakers:
                            self.circuit_breakers[step.agent_id].record_failure()
                        
                        # Actualizar métricas
                        self.metrics["tasks_failed"] += 1
                        
                        genesis_console.print(f"❌ {step.name} falló: {result.error}")
                        
                        # Decidir si continuar o abortar
                        if step.priority == TaskPriority.CRITICAL:
                            return ProjectCreationResult(
                                success=False,
                                error=f"Paso crítico '{step.name}' falló: {result.error}"
                            )
                        else:
                            # Marcar como completado para continuar
                            completed_steps.add(step_id)
                            self.logger.warning(f"Paso opcional '{step.name}' falló, continuando")
                        
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
                "execution_time": self._calculate_execution_time(),
                "metrics": self.metrics
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
    
    async def _execute_step_with_retry(
        self, 
        step: WorkflowStep, 
        semaphore: asyncio.Semaphore
    ) -> TaskResult:
        """Ejecutar paso con retry logic"""
        async with semaphore:
            max_attempts = step.retry_config.max_attempts
            
            for attempt in range(max_attempts):
                # Verificar circuit breaker
                if step.agent_id in self.circuit_breakers:
                    circuit_breaker = self.circuit_breakers[step.agent_id]
                    if not circuit_breaker.should_allow_request():
                        return TaskResult(
                            task_id=step.id,
                            success=False,
                            error=f"Circuit breaker abierto para agente {step.agent_id}"
                        )
                
                try:
                    if attempt > 0:
                        step.status = WorkflowStatus.RETRYING
                        step.retry_count = attempt
                        
                        # Calcular delay con exponential backoff
                        delay = min(
                            step.retry_config.initial_delay * (step.retry_config.exponential_base ** attempt),
                            step.retry_config.max_delay
                        )
                        
                        if step.retry_config.jitter:
                            import random
                            delay *= (0.5 + random.random() * 0.5)
                        
                        genesis_console.print(f"🔄 Reintentando {step.name} (intento {attempt + 1}/{max_attempts})")
                        await asyncio.sleep(delay)
                        
                        # Actualizar métricas
                        self.metrics["tasks_retried"] += 1
                    
                    step.status = WorkflowStatus.RUNNING
                    result = await self._execute_step(step)
                    
                    if result.success:
                        return result
                    
                    # Si es el último intento, retornar el error
                    if attempt == max_attempts - 1:
                        return result
                    
                except Exception as e:
                    if attempt == max_attempts - 1:
                        return TaskResult(
                            task_id=step.id,
                            success=False,
                            error=f"Error después de {max_attempts} intentos: {str(e)}"
                        )
                    
            return TaskResult(
                task_id=step.id,
                success=False,
                error=f"Falló después de {max_attempts} intentos"
            )
    
    async def _execute_step(self, step: WorkflowStep) -> TaskResult:
        """Ejecutar un paso del workflow"""
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
            
            # Enviar solicitud al agente con timeout
            response = await asyncio.wait_for(
                self.mcp.send_request(
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
                ),
                timeout=step.timeout
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
                    error=response.error_message
                )
                
        except asyncio.TimeoutError:
            return TaskResult(
                task_id=step.id,
                success=False,
                error=f"Timeout después de {step.timeout}s"
            )
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando paso {step.name}: {e}")
            return TaskResult(
                task_id=step.id,
                success=False,
                error=str(e)
            )
    
    def _resolve_step_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolver parámetros con resultados de pasos anteriores - versión mejorada"""
        resolved = {}
        
        for key, value in params.items():
            resolved[key] = self._resolve_parameter_value(value)
        
        return resolved
    
    def _resolve_parameter_value(self, value: Any) -> Any:
        """Resolver valor de parámetro recursivamente"""
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            # Extraer referencia a resultado anterior
            ref = value[2:-2].strip()
            
            if "." in ref:
                step_id, *key_parts = ref.split(".")
                key_path = ".".join(key_parts)
                
                step = self.workflow_steps.get(step_id)
                if step and step.result and step.result.success:
                    return self._get_nested_value(step.result.result, key_path)
            else:
                # Referencia directa a resultado completo
                step = self.workflow_steps.get(ref)
                if step and step.result and step.result.success:
                    return step.result.result
            
            return None
        
        elif isinstance(value, dict):
            return {k: self._resolve_parameter_value(v) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._resolve_parameter_value(item) for item in value]
        
        return value
    
    def _get_nested_value(self, data: Any, key_path: str) -> Any:
        """Obtener valor anidado usando dot notation"""
        if not isinstance(data, dict):
            return data
        
        keys = key_path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
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
            "metadata": result.metadata,
            "metrics": self.metrics
        }
        
        metadata_file = project_path / "genesis.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Agregar a rollback stack
        self.rollback_stack.append({
            "type": "delete_file",
            "path": str(metadata_file)
        })
        
        # Generar README del proyecto
        readme_content = self._generate_project_readme(metadata)
        readme_file = project_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        # Agregar a rollback stack
        self.rollback_stack.append({
            "type": "delete_file",
            "path": str(readme_file)
        })
        
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
- **Tiempo de ejecución**: {metadata.get('metadata', {}).get('execution_time', 'N/A')}s

## Métricas de Generación

- **Tareas ejecutadas**: {metadata.get('metrics', {}).get('tasks_executed', 0)}
- **Tareas fallidas**: {metadata.get('metrics', {}).get('tasks_failed', 0)}
- **Tareas reintentadas**: {metadata.get('metrics', {}).get('tasks_retried', 0)}

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
        
        # Broadcast cancellation
        if self.mcp and self.mcp.running:
            self.mcp.broadcast(
                sender_id="orchestrator",
                event="workflow.cancelled",
                data={"workflow_id": self.current_workflow}
            )
        
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
                    "agent": step.agent_id,
                    "retry_count": step.retry_count,
                    "execution_time": self._calculate_step_execution_time(step)
                }
                for step_id, step in self.workflow_steps.items()
            },
            "circuit_breakers": {
                agent_id: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count
                }
                for agent_id, cb in self.circuit_breakers.items()
            },
            "metrics": self.metrics
        }
    
    def _calculate_step_execution_time(self, step: WorkflowStep) -> Optional[float]:
        """Calcular tiempo de ejecución de un paso"""
        if step.start_time and step.end_time:
            return (step.end_time - step.start_time).total_seconds()
        return None
    
    # Event handlers
    async def _handle_task_completed(self, event: Dict[str, Any]):
        """Manejar tarea completada"""
        try:
            step_id = event.get("task_id") or event.get("step_id")
            if not step_id:
                self.logger.warning("Evento task.completed sin task_id")
                return

            step = self.workflow_steps.get(step_id)
            if not step:
                self.logger.warning(f"Evento task.completed para paso desconocido: {step_id}")
                return

            step.status = WorkflowStatus.COMPLETED
            step.end_time = datetime.utcnow()
            step.result = TaskResult(
                task_id=step.id,
                success=True,
                result=event.get("result"),
            )

            self.workflow_results[step_id] = step.result.result

            genesis_console.print(f"✅ {step.name} completado")
            self.logger.info(f"✅ Paso {step.name} completado")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_task_completed")

    async def _handle_task_failed(self, event: Dict[str, Any]):
        """Manejar tarea fallida"""
        try:
            step_id = event.get("task_id") or event.get("step_id")
            if not step_id:
                self.logger.warning("Evento task.failed sin task_id")
                return

            step = self.workflow_steps.get(step_id)
            if not step:
                self.logger.warning(f"Evento task.failed para paso desconocido: {step_id}")
                return

            step.status = WorkflowStatus.FAILED
            step.end_time = datetime.utcnow()
            step.result = TaskResult(
                task_id=step.id,
                success=False,
                error=event.get("error"),
            )

            self.workflow_results[step_id] = {"error": step.result.error}

            genesis_console.print(f"❌ {step.name} falló: {step.result.error}")
            self.logger.error(f"❌ Paso {step.name} falló: {step.result.error}")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_task_failed")

    async def _handle_agent_status_changed(self, event: Dict[str, Any]):
        """Manejar cambio de estado de agente"""
        try:
            agent_id = event.get("agent_id")
            status = event.get("status")
            if not agent_id or status is None:
                self.logger.warning("Evento agent.status_changed incompleto")
                return

            agent = self.agents.get(agent_id)
            if agent:
                agent.status = status

            self.logger.info(f"📣 Estado del agente {agent_id} cambiado a {status}")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_agent_status_changed")
    
    async def _handle_workflow_cancelled(self, event: Dict[str, Any]):
        """Manejar cancelación de workflow"""
        try:
            workflow_id = event.get("workflow_id")
            if workflow_id == self.current_workflow:
                self.cancelled = True
                self.logger.info(f"🛑 Workflow {workflow_id} cancelado")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_workflow_cancelled")
    
    async def shutdown(self):
        """Detener el orquestador"""
        self.running = False
        
        # Cancelar workflow actual
        if self.current_workflow:
            await self.cancel_workflow()
        
        # Detener agentes
        for agent in self.agents.values():
            try:
                await agent.stop()
            except Exception as e:
                self.logger.warning(f"Error deteniendo agente {agent.agent_id}: {e}")
        
        # Detener protocolo MCP
        if self.mcp and self.mcp.running:
            await self.mcp.stop()
        
        # Limpiar persistence
        await self._cleanup_persistence()
        self.logger.info("🛑 Orchestrator detenido")


# Backwards compatibility alias
Orchestrator = GenesisOrchestrator
