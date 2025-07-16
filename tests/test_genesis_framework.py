# test_genesis_framework.py
"""
Test Runner Final para validar todas las correcciones de Genesis Engine
Ejecuta tests críticos para asegurar que el framework funciona correctamente
"""
import logging
from typing import Dict, Any, List
import json
from datetime import datetime

import pytest

# Configurar logging para tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("genesis.tests")


class TestResult:
    """Resultado de un test"""
    __test__ = False
    
    def __init__(self, name: str, success: bool, error: str = None, details: Any = None):
        self.name = name
        self.success = success
        self.error = error
        self.details = details
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "success": self.success,
            "error": self.error,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class GenesisFrameworkTester:
    """Tester completo del framework Genesis"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def add_result(self, result: TestResult):
        """Agregar resultado de test"""
        self.results.append(result)
        self.total_tests += 1
        
        if result.success:
            self.passed_tests += 1
            print(f"✅ {result.name}")
        else:
            self.failed_tests += 1
            print(f"❌ {result.name}: {result.error}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Ejecutar todos los tests críticos"""
        print("🧪 EJECUTANDO TESTS CRÍTICOS DE GENESIS ENGINE")
        print("=" * 60)
        
        # Fase 1: Tests de Importación
        print("\n1. 🔗 Tests de Importación de Módulos")
        print("-" * 40)
        await self._test_imports()
        
        # Fase 2: Tests de Clases Base
        print("\n2. 🏗️ Tests de Clases Base")
        print("-" * 40)
        await self._test_base_classes()
        
        # Fase 3: Tests de Protocolo MCP
        print("\n3. 🔌 Tests de Protocolo MCP")
        print("-" * 40)
        await self._test_mcp_protocol()
        
        # Fase 4: Tests de Agentes
        print("\n4. 🤖 Tests de Agentes")
        print("-" * 40)
        await self._test_agents()
        
        # Fase 5: Tests de Orquestador
        print("\n5. 🎼 Tests de Orquestador")
        print("-" * 40)
        await self._test_orchestrator()
        
        # Fase 6: Tests de CLI
        print("\n6. 🖥️ Tests de CLI")
        print("-" * 40)
        await self._test_cli()
        
        # Fase 7: Test de Integración End-to-End
        print("\n7. 🚀 Test de Integración End-to-End")
        print("-" * 40)
        await self._test_end_to_end()
        
        # Generar reporte final
        return self._generate_final_report()
    
    async def _test_imports(self):
        """Test de importación de módulos críticos"""
        
        imports_to_test = [
            ("genesis_engine.mcp.agent_base", "GenesisAgent"),
            ("genesis_engine.mcp.protocol", "MCPProtocol"),
            ("genesis_engine.agents.architect", "ArchitectAgent"),
            ("genesis_engine.agents.backend", "BackendAgent"),
            ("genesis_engine.agents.frontend", "FrontendAgent"),
            ("genesis_core.orchestrator.core_orchestrator", "CoreOrchestrator"),
            ("genesis_engine.core.config", "setup_logging"),
            ("genesis_engine.core.project_manager", "ProjectManager"),
        ]
        
        for module_name, class_name in imports_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                
                self.add_result(TestResult(
                    name=f"Import {module_name}.{class_name}",
                    success=True,
                    details=f"Clase {class_name} importada correctamente"
                ))
                
            except ImportError as e:
                self.add_result(TestResult(
                    name=f"Import {module_name}.{class_name}",
                    success=False,
                    error=f"ImportError: {str(e)}"
                ))
            except Exception as e:
                self.add_result(TestResult(
                    name=f"Import {module_name}.{class_name}",
                    success=False,
                    error=f"Error: {str(e)}"
                ))
    
    async def _test_base_classes(self):
        """Test de clases base"""
        
        try:
            from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
            
            # Test de AgentTask
            task = AgentTask(name="test_task", description="Test task")
            self.add_result(TestResult(
                name="AgentTask Creation",
                success=task.name == "test_task",
                details=f"Task ID: {task.id}"
            ))
            
            # Test de TaskResult
            result = TaskResult(task_id="test", success=True, result={"test": "data"})
            self.add_result(TestResult(
                name="TaskResult Creation",
                success=result.success and result.result["test"] == "data",
                details="TaskResult creado correctamente"
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                name="Base Classes Test",
                success=False,
                error=str(e)
            ))
    
    async def _test_mcp_protocol(self):
        """Test del protocolo MCP"""
        
        try:
            from genesis_engine.mcp.protocol import MCPProtocol, MCPMessage
            from genesis_engine.mcp.agent_base import SimpleAgent
            
            # Crear protocolo
            protocol = MCPProtocol()
            
            # Test de inicialización
            self.add_result(TestResult(
                name="MCP Protocol Initialization",
                success=protocol is not None,
                details="Protocolo MCP inicializado"
            ))
            
            # Iniciar protocolo
            await protocol.start()
            
            # Test de registro de agente
            test_agent = SimpleAgent("test_agent", "TestAgent")
            protocol.register_agent(test_agent)
            
            registered = "test_agent" in protocol.agents
            self.add_result(TestResult(
                name="Agent Registration",
                success=registered,
                details=f"Agente registrado: {registered}"
            ))
            
            # Test de ping
            if registered:
                response = await protocol.send_request(
                    sender="test",
                    recipient="test_agent",
                    action="ping",
                    timeout=5
                )
                
                self.add_result(TestResult(
                    name="MCP Ping Test",
                    success=response.success,
                    details=f"Ping response: {response.data}"
                ))
            
            # Detener protocolo
            await protocol.stop()
            assert protocol.worker_task.done()
            assert protocol.metrics_task.done()
            assert protocol.circuit_task.done()
            
        except Exception as e:
            if 'protocol' in locals() and protocol.running:
                await protocol.stop()
            self.add_result(TestResult(
                name="MCP Protocol Test",
                success=False,
                error=str(e)
            ))
    
    async def _test_agents(self):
        """Test de agentes individuales"""
        
        agents_to_test = [
            ("ArchitectAgent", "genesis_engine.agents.architect"),
            ("BackendAgent", "genesis_engine.agents.backend"),
            ("FrontendAgent", "genesis_engine.agents.frontend"),
        ]
        
        for agent_name, module_name in agents_to_test:
            try:
                module = __import__(module_name, fromlist=[agent_name])
                agent_class = getattr(module, agent_name)
                
                # Crear agente
                agent = agent_class()
                
                # Test de inicialización
                self.add_result(TestResult(
                    name=f"{agent_name} Initialization",
                    success=agent.agent_id is not None,
                    details=f"Agent ID: {agent.agent_id}"
                ))
                
                # Test de capabilities
                has_capabilities = len(agent.capabilities) > 0
                self.add_result(TestResult(
                    name=f"{agent_name} Capabilities",
                    success=has_capabilities,
                    details=f"Capabilities: {agent.capabilities}"
                ))
                
                # Test de handlers críticos
                required_handlers = ["task.execute", "ping", "status"]
                missing_handlers = [h for h in required_handlers if h not in agent.handlers]
                
                self.add_result(TestResult(
                    name=f"{agent_name} Required Handlers",
                    success=len(missing_handlers) == 0,
                    error=f"Missing handlers: {missing_handlers}" if missing_handlers else None,
                    details=f"Available handlers: {list(agent.handlers.keys())}"
                ))
                
            except Exception as e:
                self.add_result(TestResult(
                    name=f"{agent_name} Test",
                    success=False,
                    error=str(e)
                ))
    
    async def _test_orchestrator(self):
        """Test del orquestador"""
        
        try:
            from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, ProjectGenerationRequest

            orchestrator = CoreOrchestrator()
            request = ProjectGenerationRequest(name="demo", template="saas-basic")
            result = await orchestrator.execute_project_generation(request)

            self.add_result(TestResult(
                name="Orchestrator Execution",
                success=result.success,
                details=result.data
            ))

        except Exception as e:
            self.add_result(TestResult(
                name="Orchestrator Test",
                success=False,
                error=str(e)
            ))
    
    async def _test_cli(self):
        """Test del CLI"""
        
        try:
            # Test de importación del CLI
            from genesis_engine.cli.main import app
            
            self.add_result(TestResult(
                name="CLI Import",
                success=app is not None,
                details="CLI Typer app importado"
            ))
            
            # Test de configuración
            from genesis_engine.core.config import validate_environment
            
            env_validation = validate_environment()

            failed_checks = [
                f"{name}: {info['message']}"
                for name, info in env_validation["checks"].items()
                if not info.get("success")
            ]

            self.add_result(TestResult(
                name="Environment Validation",
                success=env_validation["overall_success"],
                error="; ".join(failed_checks) if failed_checks else None,
                details=(
                    f"Checks passed: {env_validation['passed']}"
                    f"/{env_validation['total_checks']}"
                )
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                name="CLI Test",
                success=False,
                error=str(e)
            ))
    
    async def _test_end_to_end(self):
        """Test de integración end-to-end"""

        try:
            from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, ProjectGenerationRequest

            request = ProjectGenerationRequest(
                name="test_project_e2e",
                template="saas_basic",
                features=["authentication", "api", "frontend"],
            )

            orchestrator = CoreOrchestrator()
            result = await orchestrator.execute_project_generation(request)

            self.add_result(TestResult(
                name="End-to-End Workflow",
                success=result.success,
                details=result.data,
            ))

        except Exception as e:
            self.add_result(TestResult(
                name="End-to-End Test",
                success=False,
                error=str(e)
            ))
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generar reporte final de tests"""
        
        # Calcular estadísticas
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Categorizar errores
        critical_failures = []
        import_failures = []
        handler_failures = []
        
        for result in self.results:
            if not result.success:
                if "Import" in result.name:
                    import_failures.append(result)
                elif "Handler" in result.name or "task.execute" in result.name:
                    handler_failures.append(result)
                elif "CRITICAL" in result.name:
                    critical_failures.append(result)
        
        report = {
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "success_rate": success_rate,
                "status": "PASS" if success_rate >= 80 else "FAIL"
            },
            "categories": {
                "critical_failures": len(critical_failures),
                "import_failures": len(import_failures),
                "handler_failures": len(handler_failures)
            },
            "detailed_results": [r.to_dict() for r in self.results],
            "recommendations": self._generate_recommendations(critical_failures, import_failures, handler_failures)
        }
        
        return report
    
    def _generate_recommendations(self, critical_failures, import_failures, handler_failures) -> List[str]:
        """Generar recomendaciones basadas en fallos"""
        recommendations = []
        
        if import_failures:
            recommendations.append("🔧 Verificar que todos los archivos están en las ubicaciones correctas")
            recommendations.append("📦 Reinstalar Genesis Engine: pip install -e .")
        
        if handler_failures:
            recommendations.append("🤖 Actualizar implementación de agentes con handlers correctos")
            recommendations.append("🔌 Verificar que AgentBase tiene todos los handlers requeridos")
        
        if critical_failures:
            recommendations.append("🚨 CRÍTICO: Resolver fallos en task.execute handler inmediatamente")
            recommendations.append("🎯 Enfocar en ArchitectAgent y protocolo MCP")
        
        if not any([critical_failures, import_failures, handler_failures]):
            recommendations.append("✅ ¡Framework funcionando correctamente!")
            recommendations.append("🚀 Listo para crear proyectos con 'genesis init'")
        
        return recommendations
    
    def print_final_report(self, report: Dict[str, Any]):
        """Imprimir reporte final"""
        
        print("\n" + "=" * 60)
        print("📊 REPORTE FINAL DE TESTS")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"\n📈 Resumen:")
        print(f"   Total de tests: {summary['total_tests']}")
        print(f"   Pasaron: {summary['passed']} ✅")
        print(f"   Fallaron: {summary['failed']} ❌")
        print(f"   Tasa de éxito: {summary['success_rate']:.1f}%")
        print(f"   Estado general: {summary['status']}")
        
        categories = report["categories"]
        if categories["critical_failures"] > 0:
            print(f"\n🚨 Fallos críticos: {categories['critical_failures']}")
        if categories["import_failures"] > 0:
            print(f"🔗 Fallos de importación: {categories['import_failures']}")
        if categories["handler_failures"] > 0:
            print(f"🤖 Fallos de handlers: {categories['handler_failures']}")
        
        print(f"\n💡 Recomendaciones:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")
        
        # Resultado final
        if summary["status"] == "PASS":
            print(f"\n🎉 ¡GENESIS ENGINE ESTÁ FUNCIONANDO CORRECTAMENTE!")
            print(f"✅ Listo para usar: genesis init mi_proyecto")
        else:
            print(f"\n⚠️  GENESIS ENGINE REQUIERE CORRECCIONES")
            print(f"🔧 Revisar fallos antes de usar el framework")
        
        print("=" * 60)


# ------------------------- Pytest integration -------------------------

@pytest.fixture()
def tester():
    """Provide a fresh tester instance for each test."""
    return GenesisFrameworkTester()


@pytest.mark.asyncio
async def test_imports(tester):
    await tester._test_imports()
    assert tester.failed_tests == 0, tester.results


@pytest.mark.asyncio
async def test_base_classes(tester):
    await tester._test_base_classes()
    assert tester.failed_tests == 0, tester.results


@pytest.mark.asyncio
async def test_mcp_protocol(tester):
    await tester._test_mcp_protocol()
    assert tester.failed_tests == 0, tester.results


@pytest.mark.asyncio
async def test_agents(tester):
    await tester._test_agents()
    assert tester.failed_tests == 0, tester.results


@pytest.mark.asyncio
async def test_orchestrator(tester):
    await tester._test_orchestrator()
    assert tester.failed_tests == 0, tester.results


@pytest.mark.asyncio
async def test_cli(tester):
    await tester._test_cli()
    assert tester.failed_tests == 0, tester.results

@pytest.mark.asyncio
async def test_end_to_end(tester):
    await tester._test_end_to_end()
    assert tester.failed_tests == 0, tester.results
