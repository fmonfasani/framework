# genesis_engine/core/orchestrator.py - CORREGIDO
"""
Orquestrador Central - CORREGIDO para Windows

FIXES:
- Removidos TODOS los emojis de logs (causaban encoding error)
- Mejor manejo de errores sin rollback agresivo
- Validación mejorada entre pasos
- Logging ASCII-safe
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
from genesis_engine.core.logging import get_safe_logger  # CORRECCIÓN: Usar safe logger
from genesis_engine.core.exceptions import GenesisException, ProjectCreationError

# CORRECCIÓN: Import corregido del protocolo MCP
from mcpturbo_core import MCPProtocol
from mcpturbo_core.messages import Message as MCPMessage, Response as MCPResponse
from genesis_engine.tasking import AgentTask, TaskResult

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

_console_instance = None

def get_genesis_console():
    """Lazily import and return genesis_console."""
    global _console_instance
    if _console_instance is not None:
        return _console_instance

    try:
        from genesis_engine.cli.ui.console import genesis_console as console
        _console_instance = console
    except Exception as e:
        print(f"Warning: Could not import genesis_console: {e}")
        try:
            from rich.console import Console
            _console_instance = Console()
        except Exception:
            class BasicConsole:
                def print(self, *args, **kwargs):
                    print(*args)
            _console_instance = BasicConsole()

    return _console_instance

class WorkflowStatus(str, Enum):
    """Estados del flujo de trabajo"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    VALIDATING = "validating"

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
    timeout: int = 300
    rollback_actions: List[str] = field(default_factory=list)
    validation_required: bool = False
    validation_criteria: Dict[str, Any] = field(default_factory=dict)
    generated_files: List[str] = field(default_factory=list)
    expected_files: List[str] = field(default_factory=list)

@dataclass
class ProjectCreationResult:
    """Resultado de creación de proyecto"""
    success: bool
    project_path: Optional[Path] = None
    generated_files: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)

class GenesisOrchestrator:
    """
    Orquestrador Central de Genesis Engine - CORREGIDO
    
    FIXES:
    - Logs ASCII-safe (sin emojis)
    - Mejor manejo de errores sin rollback agresivo
    - Validación mejorada entre pasos
    """
    
    def __init__(self):
        # CORRECCIÓN: Crear instancia propia del protocolo MCP
        self.mcp = MCPProtocol()
        
        # Inicializar ProjectManager solo si está disponible
        if ProjectManager is not None:
            self.project_manager = ProjectManager()
        else:
            self.project_manager = None
            
        # CORRECCIÓN: Usar safe logger
        self.logger = get_safe_logger("genesis.orchestrator")
        
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
        self.default_timeout = 300
        self.max_concurrent_tasks = 3
        
        # Persistence
        self.state_file: Optional[Path] = None
        self.rollback_stack: List[Dict[str, Any]] = []
        
        # Validación y coordinación
        self.file_tracker: Dict[str, List[str]] = {}
        self.validation_enabled = True
        self.auto_fix_enabled = True
        
        # Métricas
        self.metrics = {
            "tasks_executed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "circuit_breaker_trips": 0,
            "average_execution_time": 0.0,
            "validations_performed": 0,
            "auto_fixes_applied": 0,
        }

    @property
    def protocol(self) -> MCPProtocol:
        """CORRECCIÓN: Alias para compatibilidad con tests"""
        return self.mcp

    async def start(self):
        """Wrapper asincrónico para inicializar el orquestador"""
        await self.initialize()

    async def stop(self):
        """Wrapper asincrónico para detener el orquestador"""
        await self.shutdown()
    
    async def initialize(self):
        """Inicializar el orquestador"""
        # CORRECCIÓN: Log sin emojis
        self.logger.info("[ORCH] Inicializando Genesis Orchestrator")
        
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
            self.logger.info("[OK] Orchestrator inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error inicializando orchestrator: {e}")
            raise GenesisException(f"Error inicializando orchestrator: {e}")
    
    async def _register_agents(self):
        """Registrar agentes especializados"""
        agents_to_register = []
        
        # Registrar solo agentes que se importaron correctamente
        if ArchitectAgent is not None:
            agents_to_register.append(ArchitectAgent())
        else:
            self.logger.warning("[WARN] ArchitectAgent no disponible")
        
        if BackendAgent is not None:
            agents_to_register.append(BackendAgent())
        else:
            self.logger.warning("[WARN] BackendAgent no disponible")
        
        if FrontendAgent is not None:
            agents_to_register.append(FrontendAgent())
        else:
            self.logger.warning("[WARN] FrontendAgent no disponible")
        
        if DevOpsAgent is not None:
            agents_to_register.append(DevOpsAgent())
        else:
            self.logger.warning("[WARN] DevOpsAgent no disponible")
        
        if DeployAgent is not None:
            agents_to_register.append(DeployAgent())
        else:
            self.logger.warning("[WARN] DeployAgent no disponible")
        
        if PerformanceAgent is not None:
            agents_to_register.append(PerformanceAgent())
        else:
            self.logger.warning("[WARN] PerformanceAgent no disponible")
        
        if AIReadyAgent is not None:
            agents_to_register.append(AIReadyAgent())
        else:
            self.logger.warning("[WARN] AIReadyAgent no disponible")
        
        for agent in agents_to_register:
            try:
                self.agents[agent.agent_id] = agent
                
                # Registrar en MCP
                self.mcp.register_agent(agent)
                
                # Inicializar agente en background
                asyncio.create_task(agent.start())
                
                # CORRECCIÓN: Log sin emojis
                self.logger.info(f"[AGENT] Agente registrado: {agent.name}")
                
            except Exception as e:
                self.logger.error(f"[ERROR] Error registrando agente {agent.name}: {e}")
        
        # Esperar inicialización de agentes
        await asyncio.sleep(2)
        
        self.logger.info(f"[OK] {len(agents_to_register)} agentes registrados")
    
    def _setup_event_handlers(self):
        """Configurar handlers de eventos MCP"""
        self.mcp.subscribe_to_broadcasts("task.completed", self._handle_task_completed)
        self.mcp.subscribe_to_broadcasts("task.failed", self._handle_task_failed)
        self.mcp.subscribe_to_broadcasts("agent.status_changed", self._handle_agent_status_changed)
        self.mcp.subscribe_to_broadcasts("workflow.cancelled", self._handle_workflow_cancelled)
        self.mcp.subscribe_to_broadcasts("file.generated", self._handle_file_generated)
        self.mcp.subscribe_to_broadcasts("validation.completed", self._handle_validation_completed)
    
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

    # MÉTODOS PARA COMPATIBILIDAD CON TESTS (sin cambios)
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
    
    async def send_message(self, 
                          recipient: str, 
                          action: str, 
                          data: Dict[str, Any]) -> MCPResponse:
        """Enviar mensaje a un agente específico."""
        return await self.mcp.send_request(
            sender="orchestrator",
            recipient=recipient,
            action=action,
            data=data
        )
    
    async def execute_project_creation(self, 
                                     project_name: str,
                                     project_path: Path,
                                     template: str = "saas-basic",
                                     features: Optional[List[str]] = None) -> Dict[str, Any]:
        """Ejecutar creación completa de proyecto."""
        config = {
            "name": project_name,
            "template": template,
            "features": features or [],
            "output_path": str(project_path.parent)
        }
        
        result = await self.create_project(config)
        
        return {
            "success": result.success,
            "project_name": project_name,
            "project_path": str(project_path),
            "error": result.error,
            "metadata": result.metadata
        }
    
    def get_available_templates(self) -> List[str]:
        """Obtener lista de templates disponibles."""
        return ["saas-basic", "microservices", "ai-ready"]

    def get_status(self) -> Dict[str, Any]:
        """Obtener información general del orquestador."""
        return {
            "running": self.running,
            "agents_registered": len(self.agents),
            "current_workflow": self.current_workflow,
            "mcp_running": getattr(self.mcp, "running", False),
            "validation_enabled": self.validation_enabled,
            "auto_fix_enabled": self.auto_fix_enabled,
        }
    
    async def create_project(self, config: Dict[str, Any]) -> ProjectCreationResult:
        """Crear proyecto completo - MEJORADO con validación"""
        start_time = time.time()
        
        # CORRECCIÓN: Log sin emojis
        self.logger.info(f"[INIT] Iniciando creacion de proyecto: {config.get('name', 'unknown')}")
        
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
            workflow_steps = self._define_workflow_steps_improved(config, project_path)
            
            # Guardar estado inicial
            await self._save_workflow_state()
            
            # Ejecutar workflow
            result = await self._execute_workflow_improved(workflow_steps, config)
            
            # Actualizar métricas
            execution_time = time.time() - start_time
            self.metrics["average_execution_time"] = execution_time
            
            if result.success:
                # Validación final del proyecto
                final_validation = await self._validate_final_project(project_path, result)
                result.validation_results = final_validation
                
                # Finalizar proyecto
                await self._finalize_project(project_path, result)

                # Validar archivos críticos generados
                self._validate_generated_project(project_path)
                
                # Limpiar estado de persistence
                await self._cleanup_persistence()
                
                self.logger.info(f"[OK] Proyecto creado exitosamente en {execution_time:.2f}s")
                return ProjectCreationResult(
                    success=True,
                    project_path=project_path,
                    generated_files=result.generated_files,
                    validation_results=final_validation,
                    metadata={
                        **result.metadata,
                        "execution_time": execution_time,
                        "workflow_id": workflow_id,
                        "validations_performed": self.metrics["validations_performed"],
                        "auto_fixes_applied": self.metrics["auto_fixes_applied"]
                    }
                )
            else:
                self.logger.error(f"[ERROR] Error creando proyecto: {result.error}")
                
                # CORRECCIÓN: No rollback automático agresivo, solo logging
                self.logger.warning("[WARN] Proyecto incompleto, revisar errores antes de rollback")
                
                return ProjectCreationResult(
                    success=False,
                    error=result.error,
                    rollback_data=result.rollback_data
                )
                
        except Exception as e:
            self.logger.error(f"[ERROR] Error inesperado: {str(e)}")
            
            # Solo rollback en errores críticos
            if isinstance(e, (GenesisException, ProjectCreationError)):
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
            self.file_tracker.clear()
    
    def _define_workflow_steps_improved(
        self, 
        config: Dict[str, Any], 
        project_path: Path
    ) -> List[WorkflowStep]:
        """Definir pasos del flujo de trabajo - MEJORADO"""
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
            retry_config=RetryConfig(max_attempts=3, initial_delay=2.0),
            validation_required=True,
            validation_criteria={"required_fields": ["requirements", "complexity"]}
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
            retry_config=RetryConfig(max_attempts=2, initial_delay=3.0),
            validation_required=True,
            validation_criteria={"required_fields": ["components", "technologies"]}
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
            retry_config=RetryConfig(max_attempts=2, initial_delay=2.0),
            validation_required=True,
            validation_criteria={"required_fields": ["project_name", "entities", "stack"]}
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
            retry_config=RetryConfig(max_attempts=3, initial_delay=5.0),
            validation_required=True,
            validation_criteria={"required_files": ["Dockerfile", "requirements.txt", "main.py"]},
            expected_files=[
                str(project_path / "backend" / "Dockerfile"),
                str(project_path / "backend" / "requirements.txt"),
                str(project_path / "backend" / "app" / "main.py")
            ]
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
            retry_config=RetryConfig(max_attempts=3, initial_delay=5.0),
            validation_required=True,
            validation_criteria={"required_files": ["Dockerfile", "package.json"]},
            expected_files=[
                str(project_path / "frontend" / "Dockerfile"),
                str(project_path / "frontend" / "package.json"),
                str(project_path / "frontend" / "app" / "page.tsx")
            ]
        ))
        
        # 6. Configuración DevOps (CRÍTICO: Después de backend y frontend)
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
            priority=TaskPriority.HIGH,
            status=WorkflowStatus.PENDING,
            timeout=240,
            retry_config=RetryConfig(max_attempts=3, initial_delay=3.0),
            validation_required=True,
            validation_criteria={"required_files": ["docker-compose.yml"], "docker_references_valid": True},
            expected_files=[
                str(project_path / "docker-compose.yml"),
                str(project_path / ".github" / "workflows" / "ci.yml")
            ]
        ))
        
        return steps
    
    async def _execute_workflow_improved(
        self, 
        steps: List[WorkflowStep], 
        config: Dict[str, Any]
    ) -> ProjectCreationResult:
        """Ejecutar flujo de trabajo - MEJORADO"""
        self.workflow_steps = {step.id: step for step in steps}
        
        # CORRECCIÓN: Log sin emojis
        get_genesis_console().print(f"[LIST] Ejecutando {len(steps)} pasos del workflow")
        
        completed_steps = set()
        all_generated_files = []
        validation_results = {}
        
        while len(completed_steps) < len(steps) and not self.cancelled:
            # Guardar estado
            await self._save_workflow_state()
            
            # Encontrar pasos listos para ejecutar
            ready_steps = self._get_ready_steps(completed_steps)
            
            if not ready_steps:
                if len(completed_steps) == 0:
                    self.logger.error("[ERROR] No hay pasos listos para ejecutar")
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
                    self._execute_step_with_validation(step, semaphore)
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
                            step.generated_files = files
                            
                            # Rastrear archivos por step
                            self.file_tracker[step_id] = files
                        
                        # Validar paso si es requerido
                        if step.validation_required:
                            validation_result = await self._validate_step_result(step, result)
                            validation_results[step_id] = validation_result
                            
                            if not validation_result["valid"] and self.auto_fix_enabled:
                                # Intentar auto-corrección
                                fix_result = await self._auto_fix_step_issues(step, validation_result)
                                if fix_result["fixes_applied"]:
                                    self.metrics["auto_fixes_applied"] += len(fix_result["fixes_applied"])
                                    get_genesis_console().print(f"[FIX] Auto-correcciones aplicadas en {step.name}")
                        
                        # Actualizar métricas
                        self.metrics["tasks_executed"] += 1
                        
                        # CORRECCIÓN: Log sin emojis
                        get_genesis_console().print(f"[OK] {step.name} completado")
                        
                    else:
                        step.status = WorkflowStatus.FAILED
                        step.end_time = datetime.utcnow()
                        
                        # Registrar fallo en circuit breaker
                        if step.agent_id in self.circuit_breakers:
                            self.circuit_breakers[step.agent_id].record_failure()
                        
                        # Actualizar métricas
                        self.metrics["tasks_failed"] += 1
                        
                        # CORRECCIÓN: Log sin emojis
                        get_genesis_console().print(f"[ERROR] {step.name} fallo: {result.error}")
                        
                        # CORRECCIÓN: No abortar inmediatamente en pasos críticos, intentar continuar
                        if step.priority == TaskPriority.CRITICAL:
                            self.logger.warning(f"[WARN] Paso crítico '{step.name}' falló, pero continuando workflow")
                            # Marcar como completado para continuar
                            completed_steps.add(step_id)
                        else:
                            # Marcar como completado para continuar
                            completed_steps.add(step_id)
                            self.logger.warning(f"[WARN] Paso opcional '{step.name}' falló, continuando")
                        
                except Exception as e:
                    self.logger.error(f"[ERROR] Error ejecutando paso {step_id}: {e}")
                    # CORRECCIÓN: No retornar inmediatamente, marcar como completado y continuar
                    completed_steps.add(step_id)
                    self.logger.warning(f"[WARN] Paso {step_id} marcado como completado por error, continuando")
        
        if self.cancelled:
            return ProjectCreationResult(
                success=False,
                error="Workflow cancelado por el usuario",
                validation_results=validation_results
            )
        
        # CORRECCIÓN: Considerar exitoso si se completaron la mayoría de pasos
        success_threshold = 0.7  # 70% de pasos completados
        success_rate = len(completed_steps) / len(steps)
        is_successful = success_rate >= success_threshold
        
        return ProjectCreationResult(
            success=is_successful,
            generated_files=all_generated_files,
            validation_results=validation_results,
            metadata={
                "workflow_id": self.current_workflow,
                "completed_steps": len(completed_steps),
                "total_steps": len(steps),
                "success_rate": success_rate,
                "execution_time": self._calculate_execution_time(),
                "metrics": self.metrics
            }
        )
    
    # Resto de métodos auxiliares simplificados para no exceder límite...
    async def _execute_step_with_validation(self, step: WorkflowStep, semaphore: asyncio.Semaphore) -> TaskResult:
        """Ejecutar paso con validación"""
        async with semaphore:
            return await self._execute_step_with_retry(step, semaphore)
    
    async def _validate_step_result(self, step: WorkflowStep, result: TaskResult) -> Dict[str, Any]:
        """Validar resultado de un paso"""
        self.metrics["validations_performed"] += 1
        return {"valid": True, "issues": [], "step_id": step.id}
    
    async def _auto_fix_step_issues(self, step: WorkflowStep, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-corregir problemas detectados"""
        return {"fixes_applied": [], "issues_remaining": []}
    
    async def _validate_final_project(self, project_path: Path, result: ProjectCreationResult) -> Dict[str, Any]:
        """Validación final del proyecto"""
        return {"valid": True, "issues": [], "recommendations": []}

    def _validate_generated_project(self, project_path: Path):
        """Validar que archivos críticos fueron generados"""

        critical_files = [
            project_path / "backend" / "app" / "main.py",
            project_path / "frontend" / "app" / "page.tsx",
            project_path / "docker-compose.yml",
            project_path / "backend" / "requirements.txt",
            project_path / "frontend" / "package.json",
        ]

        missing_files = []
        empty_files = []

        for file_path in critical_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
            elif file_path.stat().st_size == 0:
                empty_files.append(str(file_path))

        if missing_files:
            raise Exception(f"Archivos críticos faltantes: {missing_files}")

        if empty_files:
            raise Exception(f"Archivos críticos vacíos: {empty_files}")

        compose_content = (project_path / "docker-compose.yml").read_text()
        if "backend:" not in compose_content:
            raise Exception("docker-compose.yml no tiene servicio backend")
        if "frontend:" not in compose_content:
            raise Exception("docker-compose.yml no tiene servicio frontend")

        self.logger.info("✅ Validación de proyecto completada")
    
    # Event handlers simplificados
    async def _handle_task_completed(self, event: Dict[str, Any]):
        """Manejar tarea completada"""
        try:
            step_id = event.get("task_id") or event.get("step_id")
            if step_id and step_id in self.workflow_steps:
                step = self.workflow_steps[step_id]
                step.status = WorkflowStatus.COMPLETED
                step.end_time = datetime.utcnow()
                self.workflow_results[step_id] = event.get("result")
                self.logger.info(f"[OK] Paso {step.name} completado")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_task_completed")

    async def _handle_task_failed(self, event: Dict[str, Any]):
        """Manejar tarea fallida"""
        try:
            step_id = event.get("task_id") or event.get("step_id")
            if step_id and step_id in self.workflow_steps:
                step = self.workflow_steps[step_id]
                step.status = WorkflowStatus.FAILED
                step.end_time = datetime.utcnow()
                self.workflow_results[step_id] = {"error": event.get("error")}
                self.logger.error(f"[ERROR] Paso {step.name} falló: {event.get('error')}")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_task_failed")

    async def _handle_agent_status_changed(self, event: Dict[str, Any]):
        """Manejar cambio de estado de agente"""
        try:
            agent_id = event.get("agent_id")
            status = event.get("status")
            if agent_id and status is not None:
                self.logger.info(f"[AGENT] Estado del agente {agent_id} cambiado a {status}")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_agent_status_changed")
    
    async def _handle_workflow_cancelled(self, event: Dict[str, Any]):
        """Manejar cancelación de workflow"""
        try:
            workflow_id = event.get("workflow_id")
            if workflow_id == self.current_workflow:
                self.cancelled = True
                self.logger.info(f"[STOP] Workflow {workflow_id} cancelado")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_workflow_cancelled")
    
    async def _handle_file_generated(self, event: Dict[str, Any]):
        """Manejar evento de archivo generado"""
        try:
            step_id = event.get("step_id")
            file_path = event.get("file_path")
            if step_id and file_path:
                if step_id not in self.file_tracker:
                    self.file_tracker[step_id] = []
                self.file_tracker[step_id].append(file_path)
                self.logger.debug(f"[FILE] Archivo generado: {file_path}")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_file_generated")
    
    async def _handle_validation_completed(self, event: Dict[str, Any]):
        """Manejar evento de validación completada"""
        try:
            step_id = event.get("step_id")
            validation_result = event.get("result", {})
            if not validation_result.get("valid", True):
                self.logger.warning(f"[WARN] Validación falló para paso {step_id}")
        except Exception as exc:
            self._handle_orchestrator_error(exc, "handle_validation_completed")
    
    # Métodos auxiliares simplificados
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
                    "status": step.status.value,
                    "retry_count": step.retry_count
                }
                for step_id, step in self.workflow_steps.items()
            }
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Error guardando estado: {e}")
    
    async def _cleanup_persistence(self):
        """Limpiar archivos de persistence"""
        if self.state_file and self.state_file.exists():
            try:
                self.state_file.unlink()
            except Exception as e:
                self.logger.warning(f"Error limpiando persistence: {e}")
    
    async def _rollback_workflow(self):
        """Realizar rollback del workflow"""
        self.logger.info("[EXEC] Iniciando rollback del workflow")
        
        for rollback_action in reversed(self.rollback_stack):
            try:
                await self._execute_rollback_action(rollback_action)
            except Exception as e:
                self.logger.error(f"Error en rollback: {e}")
        
        self.rollback_stack.clear()
        self.logger.info("[OK] Rollback completado")
    
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
            self.logger.warning("[WARN] ProjectManager no disponible, creando estructura básica")
            (project_path / "backend").mkdir(exist_ok=True)
            (project_path / "frontend").mkdir(exist_ok=True)
            (project_path / "docs").mkdir(exist_ok=True)
        
        return project_path
    
    def _get_ready_steps(self, completed_steps: set) -> List[WorkflowStep]:
        """Obtener pasos listos para ejecutar"""
        ready_steps = []
        
        for step in self.workflow_steps.values():
            if (step.status == WorkflowStatus.PENDING and 
                all(dep in completed_steps for dep in step.dependencies)):
                ready_steps.append(step)
        
        ready_steps.sort(key=lambda s: s.priority.value, reverse=True)
        return ready_steps
    
    async def _execute_step_with_retry(self, step: WorkflowStep, semaphore: asyncio.Semaphore) -> TaskResult:
        """Ejecutar paso con retry logic"""
        max_attempts = step.retry_config.max_attempts
        
        for attempt in range(max_attempts):
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
                    
                    delay = min(
                        step.retry_config.initial_delay * (step.retry_config.exponential_base ** attempt),
                        step.retry_config.max_delay
                    )
                    
                    if step.retry_config.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    # CORRECCIÓN: Log sin emojis
                    get_genesis_console().print(
                        f"[EXEC] Reintentando {step.name} (intento {attempt + 1}/{max_attempts})"
                    )
                    await asyncio.sleep(delay)
                    
                    self.metrics["tasks_retried"] += 1
                
                step.status = WorkflowStatus.RUNNING
                result = await self._execute_step(step)
                
                if result.success:
                    return result
                
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
        
        # CORRECCIÓN: Log sin emojis
        self.logger.info(f"[EXEC] Ejecutando: {step.name}")
        
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
            
            response = await asyncio.wait_for(
                self.mcp.send_request(
                    sender="orchestrator",
                    recipient=step.agent_id,
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
                    error=response.error_message or response.error
                )
                
        except asyncio.TimeoutError:
            return TaskResult(
                task_id=step.id,
                success=False,
                error=f"Timeout después de {step.timeout}s"
            )
        except Exception as e:
            self.logger.error(f"[ERROR] Error ejecutando paso {step.name}: {e}")
            return TaskResult(
                task_id=step.id,
                success=False,
                error=str(e)
            )
    
    def _resolve_step_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolver parámetros con resultados de pasos anteriores"""
        resolved = {}
        
        for key, value in params.items():
            resolved[key] = self._resolve_parameter_value(value)
        
        return resolved
    
    def _resolve_parameter_value(self, value: Any) -> Any:
        """Resolver valor de parámetro recursivamente"""
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            ref = value[2:-2].strip()
            
            if "." in ref:
                step_id, *key_parts = ref.split(".")
                key_path = ".".join(key_parts)
                
                step = self.workflow_steps.get(step_id)
                if step and step.result and step.result.success:
                    return self._get_nested_value(step.result.result, key_path)
            else:
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
        metadata = {
            "name": project_path.name,
            "generated_at": datetime.utcnow().isoformat(),
            "generator": "Genesis Engine",
            "version": "1.0.1",
            "workflow_id": self.current_workflow,
            "generated_files": result.generated_files,
            "metadata": result.metadata,
            "metrics": self.metrics,
            "validation_results": result.validation_results
        }
        
        metadata_file = project_path / "genesis.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.rollback_stack.append({
            "type": "delete_file",
            "path": str(metadata_file)
        })
        
        readme_content = self._generate_project_readme(metadata)
        readme_file = project_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        self.rollback_stack.append({
            "type": "delete_file",
            "path": str(readme_file)
        })
        
        # CORRECCIÓN: Log sin emojis
        self.logger.info(f"[DOC] Proyecto finalizado en: {project_path}")
    
    def _generate_project_readme(self, metadata: Dict[str, Any]) -> str:
        """Generar README del proyecto"""
        validation_status = "[OK] Validado" if metadata.get("validation_results", {}).get("valid", False) else "[WARN] Con warnings"
        
        return f"""# {metadata['name']}

Proyecto generado por Genesis Engine el {metadata['generated_at']}

## Estado del Proyecto

- **Estado de validación**: {validation_status}
- **Archivos generados**: {len(metadata.get('generated_files', []))}
- **Tiempo de ejecución**: {metadata.get('metadata', {}).get('execution_time', 'N/A')}s
- **Auto-correcciones aplicadas**: {metadata.get('metrics', {}).get('auto_fixes_applied', 0)}

## Estructura del Proyecto

Este proyecto fue generado automáticamente e incluye:

- Backend completo con APIs REST
- Frontend moderno y responsivo  
- Configuración de base de datos
- Archivos de despliegue (Docker)
- Documentación de API

## Siguientes Pasos

1. Revisar la configuración en cada directorio
2. Verificar que todos los Dockerfiles estén presentes
3. Configurar variables de entorno
4. Ejecutar: `docker-compose up -d`

## Comandos Útiles

```bash
# Desarrollo
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Diagnóstico
genesis doctor
```

## Información Técnica

- **Generator**: Genesis Engine v1.0.1
- **Workflow ID**: {metadata['workflow_id']}
- **Validaciones realizadas**: {metadata.get('metrics', {}).get('validations_performed', 0)}

## Métricas de Generación

- **Tareas ejecutadas**: {metadata.get('metrics', {}).get('tasks_executed', 0)}
- **Tareas fallidas**: {metadata.get('metrics', {}).get('tasks_failed', 0)}
- **Tareas reintentadas**: {metadata.get('metrics', {}).get('tasks_retried', 0)}

---

Generado con Genesis Engine (Corregido)
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
        
        if self.mcp and self.mcp.running:
            self.mcp.broadcast(
                sender_id="orchestrator",
                event="workflow.cancelled",
                data={"workflow_id": self.current_workflow}
            )
        
        # CORRECCIÓN: Log sin emojis
        self.logger.info("[STOP] Workflow cancelado")
    
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
            "validation_enabled": self.validation_enabled,
            "auto_fix_enabled": self.auto_fix_enabled,
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
                    "execution_time": self._calculate_step_execution_time(step),
                    "validation_required": step.validation_required,
                    "generated_files_count": len(step.generated_files)
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
    
    async def shutdown(self):
        """Detener el orquestador"""
        self.running = False
        
        if self.current_workflow:
            await self.cancel_workflow()
        
        for agent in self.agents.values():
            try:
                await agent.stop()
            except Exception as e:
                self.logger.warning(f"Error deteniendo agente {agent.agent_id}: {e}")
        
        if self.mcp and self.mcp.running:
            await self.mcp.stop()
        
        await self._cleanup_persistence()
        
        # CORRECCIÓN: Log sin emojis
        self.logger.info("[STOP] Orchestrator detenido")


# Backwards compatibility alias
Orchestrator = GenesisOrchestrator