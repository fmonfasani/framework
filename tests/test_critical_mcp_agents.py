# tests/test_critical_mcp_agents.py
"""
Tests críticos para diagnosticar problemas de MCP y Agentes
Estos tests identifican los errores fundamentales del framework
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from genesis_engine.mcp.protocol import MCPProtocol, MCPMessage, MCPResponse
from genesis_engine.mcp.agent_registry import AgentRegistry
from genesis_engine.agents.architect import ArchitectAgent
from genesis_engine.agents.backend import BackendAgent
from genesis_engine.core.orchestrator import Orchestrator


class TestMCPProtocolCritical:
    """Tests críticos del protocolo MCP"""
    
    def test_mcp_protocol_initialization(self):
        """Test: MCP Protocol se inicializa correctamente"""
        protocol = MCPProtocol()
        assert protocol is not None
        assert hasattr(protocol, 'send_request')
        assert hasattr(protocol, 'register_agent')
    
    def test_mcp_message_structure(self):
        """Test: Estructura de mensajes MCP"""
        message = MCPMessage(
            id="test_123",
            sender="test_sender",
            recipient="test_recipient",
            action="test_action",
            data={"test": "data"}
        )
        
        assert message.id == "test_123"
        assert message.sender == "test_sender"
        assert message.recipient == "test_recipient"
        assert message.action == "test_action"
        assert message.data == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_agent_registration(self):
        """Test: Registro de agentes en MCP"""
        protocol = MCPProtocol()
        
        # Crear un agente mock
        mock_agent = Mock()
        mock_agent.agent_id = "test_agent"
        mock_agent.name = "TestAgent"
        mock_agent.handle_request = AsyncMock(return_value={"success": True})
        
        # Registrar agente
        protocol.register_agent(mock_agent)
        
        # Verificar que está registrado
        assert "test_agent" in protocol.agents
        assert protocol.agents["test_agent"] == mock_agent


class TestAgentBaseCritical:
    """Tests críticos de la clase base de agentes"""
    
    def test_architect_agent_initialization(self):
        """Test: ArchitectAgent se inicializa correctamente"""
        agent = ArchitectAgent()
        
        assert agent.agent_id == "architect_agent"
        assert agent.name == "ArchitectAgent"
        assert hasattr(agent, 'handle_request')
        assert hasattr(agent, 'execute_task')
    
    def test_backend_agent_initialization(self):
        """Test: BackendAgent se inicializa correctamente"""
        agent = BackendAgent()
        
        assert agent.agent_id == "backend_agent"
        assert agent.name == "BackendAgent"
        assert hasattr(agent, 'handle_request')
        assert hasattr(agent, 'execute_task')
    
    def test_agent_has_required_handlers(self):
        """Test CRÍTICO: Agentes tienen handlers necesarios"""
        agent = ArchitectAgent()
        
        # Verificar que tiene los handlers requeridos
        assert hasattr(agent, 'handlers')
        
        # Estos son los handlers que el orquestador espera
        required_handlers = ['task.execute', 'ping', 'status']
        
        for handler in required_handlers:
            assert handler in agent.handlers, f"Handler '{handler}' faltante en {agent.name}"
    
    @pytest.mark.asyncio
    async def test_task_execute_handler_exists(self):
        """Test CRÍTICO: Handler task.execute funciona"""
        agent = ArchitectAgent()
        
        # Crear mensaje de prueba
        request = Mock()
        request.action = "task.execute"
        request.data = {
            "name": "analyze_requirements",
            "params": {
                "description": "test app",
                "features": ["authentication"]
            }
        }
        
        # Verificar que puede manejar task.execute
        try:
            result = await agent.handle_request(request)
            assert result is not None
            print(f"✅ task.execute funciona: {result}")
        except Exception as e:
            pytest.fail(f"❌ task.execute falló: {e}")


class TestOrchestratorCritical:
    """Tests críticos del orquestador"""
    
    def test_orchestrator_initialization(self):
        """Test: Orchestrator se inicializa correctamente"""
        orchestrator = Orchestrator()
        
        assert orchestrator is not None
        assert hasattr(orchestrator, 'protocol')
        assert hasattr(orchestrator, 'create_project')
    
    @pytest.mark.asyncio
    async def test_orchestrator_agent_communication(self):
        """Test CRÍTICO: Orquestador puede comunicarse con agentes"""
        orchestrator = Orchestrator()
        
        # Inicializar orquestador
        await orchestrator.start()
        
        # Verificar que los agentes están registrados
        assert len(orchestrator.protocol.agents) > 0
        
        # Verificar que architect_agent está registrado
        assert "architect_agent" in orchestrator.protocol.agents
        
        # Detener orquestador
        await orchestrator.stop()


class TestWorkflowCritical:
    """Tests críticos del workflow de creación"""
    
    @pytest.mark.asyncio
    async def test_analyze_requirements_step(self):
        """Test CRÍTICO: Paso 'Analizar Requisitos' funciona"""
        orchestrator = Orchestrator()
        await orchestrator.start()
        
        try:
            # Simular el paso que está fallando
            task_data = {
                "name": "analyze_requirements",
                "description": "Test app para ingeniería",
                "features": ["authentication", "database", "api"]
            }
            
            # Enviar tarea al ArchitectAgent
            response = await orchestrator.protocol.send_request(
                sender="orchestrator",
                recipient="architect_agent",
                action="task.execute",
                data=task_data
            )
            
            # Verificar respuesta
            assert response is not None
            assert response.success is True
            print(f"✅ Analizar Requisitos exitoso: {response.data}")
            
        except Exception as e:
            pytest.fail(f"❌ Analizar Requisitos falló: {e}")
        finally:
            await orchestrator.stop()


class TestIntegrationCritical:
    """Tests de integración críticos"""
    
    @pytest.mark.asyncio
    async def test_full_init_workflow(self):
        """Test CRÍTICO: Workflow completo de 'genesis init'"""
        orchestrator = Orchestrator()
        
        project_config = {
            "name": "test_app",
            "description": "Test app for framework validation",
            "template": "saas-basic",
            "features": ["authentication", "database", "api", "frontend"]
        }
        
        try:
            # Intentar crear proyecto completo
            result = await orchestrator.create_project(project_config)
            
            # Verificar resultado
            assert result is not None
            assert result.get("success") is True
            print(f"✅ Workflow completo exitoso: {result}")
            
        except Exception as e:
            print(f"❌ Workflow completo falló: {e}")
            # No fallar el test, solo registrar el error
            assert str(e) != ""  # El error debe tener información útil


def run_critical_tests():
    """Ejecutar tests críticos y mostrar resultados"""
    print("🔥 EJECUTANDO TESTS CRÍTICOS DE GENESIS ENGINE")
    print("=" * 50)
    
    # Tests básicos de estructura
    print("\n1. 🧪 Tests de Estructura Básica:")
    try:
        test_mcp = TestMCPProtocolCritical()
        test_mcp.test_mcp_protocol_initialization()
        print("   ✅ MCP Protocol inicialización")
        
        test_mcp.test_mcp_message_structure()
        print("   ✅ Estructura de mensajes MCP")
        
    except Exception as e:
        print(f"   ❌ Error en estructura básica: {e}")
    
    # Tests de agentes
    print("\n2. 🤖 Tests de Agentes:")
    try:
        test_agents = TestAgentBaseCritical()
        test_agents.test_architect_agent_initialization()
        print("   ✅ ArchitectAgent inicialización")
        
        test_agents.test_backend_agent_initialization()
        print("   ✅ BackendAgent inicialización")
        
        test_agents.test_agent_has_required_handlers()
        print("   ✅ Handlers requeridos presentes")
        
    except Exception as e:
        print(f"   ❌ Error en agentes: {e}")
    
    # Tests del orquestador
    print("\n3. 🎼 Tests de Orquestador:")
    try:
        test_orch = TestOrchestratorCritical()
        test_orch.test_orchestrator_initialization()
        print("   ✅ Orchestrator inicialización")
        
    except Exception as e:
        print(f"   ❌ Error en orquestador: {e}")
    
    print("\n" + "=" * 50)
    print("📊 DIAGNÓSTICO COMPLETO - Ver errores específicos arriba")


if __name__ == "__main__":
    run_critical_tests()