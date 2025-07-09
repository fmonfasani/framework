# genesis_engine/mcp/agent_base.py
"""
Clase base corregida para todos los agentes de Genesis Engine
Implementa los handlers necesarios para comunicación MCP
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Union
import uuid
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Estados de las tareas"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Representa una tarea para un agente"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    priority: int = 2  # 1=alta, 2=media, 3=baja
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def start(self):
        """Marcar tarea como iniciada"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self):
        """Marcar tarea como completada"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def fail(self):
        """Marcar tarea como fallida"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()


@dataclass
class TaskResult:
    """Resultado de la ejecución de una tarea"""
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir resultado a diccionario"""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }


class GenesisAgent(ABC):
    """
    Clase base para todos los agentes de Genesis Engine
    Implementa protocolo MCP y handlers básicos
    """
    
    def __init__(self, agent_id: str, name: str, agent_type: str = "generic"):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.status = "initialized"
        self.capabilities = []
        self.handlers: Dict[str, Callable] = {}
        self.version = "1.0.0"
        self.logger = logging.getLogger(f"agent.{self.agent_id}")
        self.metadata: Dict[str, Any] = {}
        
        # Registrar handlers básicos requeridos por MCP
        self._register_core_handlers()
    
    def _register_core_handlers(self):
        """Registrar handlers básicos requeridos"""
        self.register_handler("task.execute", self._handle_task_execute)
        self.register_handler("ping", self._handle_ping)
        self.register_handler("status", self._handle_status)
        self.register_handler("capabilities", self._handle_capabilities)
        self.register_handler("health", self._handle_health)
    
    def register_handler(self, action: str, handler: Callable):
        """Registrar handler para una acción específica"""
        self.handlers[action] = handler
        self.logger.debug(f"Registrado handler para acción: {action}")
    
    async def handle_request(self, request) -> Dict[str, Any]:
        """
        Punto de entrada principal para manejar solicitudes MCP
        Esta es la función que el protocolo MCP llama
        """
        try:
            action = getattr(request, 'action', None)
            if not action:
                raise ValueError("Request sin action especificada")
            
            self.logger.debug(f"Manejando request: {action}")
            
            if action not in self.handlers:
                available_actions = list(self.handlers.keys())
                raise ValueError(
                    f"Handler not found for action '{action}'. "
                    f"Available actions: {available_actions}"
                )
            
            handler = self.handlers[action]
            
            # Ejecutar handler (puede ser async o sync)
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request)
            else:
                result = handler(request)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error manejando request {action}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_task_execute(self, request) -> Dict[str, Any]:
        """
        Handler para task.execute - El más importante
        Este es el handler que está fallando actualmente
        """
        try:
            # Extraer datos del request
            data = getattr(request, 'data', {})
            
            # Crear tarea
            task = AgentTask(
                id=data.get("task_id", str(uuid.uuid4())),
                name=data.get("name", "unknown_task"),
                description=data.get("description", ""),
                params=data.get("params", {}),
                priority=data.get("priority", 2)
            )
            
            self.logger.info(f"Ejecutando tarea: {task.name} (ID: {task.id})")
            
            # Marcar como iniciada
            task.start()
            
            start_time = datetime.utcnow()
            
            # Ejecutar la tarea específica
            result = await self.execute_task(task)
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Procesar resultado
            if isinstance(result, TaskResult):
                task_result = result
                task_result.execution_time = execution_time
            else:
                # Si no es TaskResult, crear uno
                task_result = TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result,
                    execution_time=execution_time
                )
            
            # Marcar tarea como completada o fallida
            if task_result.success:
                task.complete()
                self.logger.info(f"Tarea {task.name} completada exitosamente")
            else:
                task.fail()
                self.logger.error(f"Tarea {task.name} falló: {task_result.error}")
            
            return task_result.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error ejecutando task.execute: {str(e)}")
            return {
                "task_id": data.get("task_id", "unknown"),
                "success": False,
                "error": str(e),
                "execution_time": None
            }
    
    async def _handle_ping(self, request) -> Dict[str, Any]:
        """Handler para ping - verificar que el agente está vivo"""
        return {
            "success": True,
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "timestamp": datetime.utcnow().isoformat(),
            "pong": True
        }
    
    async def _handle_status(self, request) -> Dict[str, Any]:
        """Handler para status - obtener estado del agente"""
        return {
            "success": True,
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities,
            "version": self.version,
            "handlers": list(self.handlers.keys())
        }
    
    async def _handle_capabilities(self, request) -> Dict[str, Any]:
        """Handler para capabilities - listar capacidades del agente"""
        return {
            "success": True,
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "handlers": list(self.handlers.keys())
        }
    
    async def _handle_health(self, request) -> Dict[str, Any]:
        """Handler para health - verificar salud del agente"""
        return {
            "success": True,
            "agent_id": self.agent_id,
            "healthy": self.status == "running",
            "status": self.status,
            "uptime": getattr(self, '_start_time', None)
        }
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Union[TaskResult, Any]:
        """
        Ejecutar una tarea específica del agente
        Debe ser implementado por cada agente especializado
        """
        pass
    
    async def start(self):
        """Iniciar el agente"""
        self.status = "running"
        self._start_time = datetime.utcnow()
        self.logger.info(f"Agente {self.name} iniciado")
    
    async def stop(self):
        """Detener el agente"""
        self.status = "stopped"
        self.logger.info(f"Agente {self.name} detenido")
    
    def add_capability(self, capability: str):
        """Agregar capacidad al agente"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.logger.debug(f"Capacidad agregada: {capability}")

    def remove_capability(self, capability: str):
        """Remover capacidad del agente"""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.logger.debug(f"Capacidad removida: {capability}")

    def has_capability(self, capability: str) -> bool:
        """Verificar si el agente tiene una capacidad específica"""
        return capability in self.capabilities

    def set_metadata(self, key: str, value: Any) -> None:

        """Guardar información arbitraria sobre el agente."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default=None) -> Any:
        """Obtener un valor de metadata almacenada."""

        return self.metadata.get(key, default)

    def get_info(self) -> Dict[str, Any]:
        """Obtener información completa del agente"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": self.status,
            "version": self.version,
            "capabilities": self.capabilities,
            "handlers": list(self.handlers.keys()),
            "metadata": self.metadata,
        }


class SimpleAgent(GenesisAgent):
    """
    Agente simple para testing y casos básicos
    Implementa execute_task con respuesta genérica
    """
    
    def __init__(self, agent_id: str, name: str, agent_type: str = "simple"):
        super().__init__(agent_id, name, agent_type)
        self.add_capability("simple_tasks")
    
    async def execute_task(self, task: AgentTask) -> TaskResult:
        """Ejecutar tarea simple"""
        await asyncio.sleep(0.1)  # Simular trabajo
        
        return TaskResult(
            task_id=task.id,
            success=True,
            result={
                "message": f"Tarea {task.name} completada por {self.name}",
                "task_name": task.name,
                "agent": self.name,
                "params": task.params
            }
        )


# Función utilitaria para crear agentes simples
def create_simple_agent(agent_id: str, name: str = None) -> SimpleAgent:
    """Crear un agente simple para testing"""
    if name is None:
        name = agent_id.replace("_", " ").title()
    
    return SimpleAgent(agent_id, name)


# Validación de la implementación
def validate_agent_implementation(agent: GenesisAgent) -> bool:
    """Validar que un agente tiene la implementación correcta"""
    required_handlers = ["task.execute", "ping", "status"]
    
    for handler in required_handlers:
        if handler not in agent.handlers:
            logger.error(f"Agente {agent.name} falta handler: {handler}")
            return False
    
    if not hasattr(agent, 'execute_task'):
        logger.error(f"Agente {agent.name} falta método execute_task")
        return False
    
    return True