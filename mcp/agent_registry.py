"""
Registro de agentes para MCP
"""

from typing import Dict, List, Type
from genesis_engine.agents.base_agent import BaseAgent

class AgentRegistry:
    """Registro centralizado de agentes disponibles"""
    
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, agent_class: Type[BaseAgent]):
        """Registrar una clase de agente"""
        cls._agents[agent_class.agent_type] = agent_class
    
    @classmethod
    def get_agent_class(cls, agent_type: str) -> Type[BaseAgent]:
        """Obtener clase de agente por tipo"""
        return cls._agents.get(agent_type)
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """Listar tipos de agentes disponibles"""
        return list(cls._agents.keys())
    
    @classmethod
    def create_agent(cls, agent_type: str, **kwargs) -> BaseAgent:
        """Crear instancia de agente"""
        agent_class = cls.get_agent_class(agent_type)
        if not agent_class:
            raise ValueError(f"Tipo de agente no encontrado: {agent_type}")
        
        return agent_class(**kwargs)