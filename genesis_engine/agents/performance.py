"""
Performance Agent - Optimización de rendimiento y seguridad

Este agente es responsable de:
- Análisis de rendimiento de código generado
- Optimización de consultas de base de datos
- Configuración de cache (Redis, CDN)
- Implementación de rate limiting
- Optimización de imágenes y assets
- Configuración de compresión
- Auditoría de seguridad
- Implementación de mejores prácticas
- Monitoreo de métricas de rendimiento
"""

import ast
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import ast
import tokenize
import io
from typing import Generator, Tuple

from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult

class OptimizationType(str, Enum):
    """Tipos de optimización"""
    PERFORMANCE = "performance"
    SECURITY = "security"
    DATABASE = "database"
    FRONTEND = "frontend"
    CACHING = "caching"
    COMPRESSION = "compression"
    MONITORING = "monitoring"

class SeverityLevel(str, Enum):
    """Niveles de severidad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PerformanceIssue:
    """Issue de rendimiento detectado"""
    type: OptimizationType
    severity: SeverityLevel
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    estimated_impact: str = "medium"

@dataclass
class OptimizationResult:
    """Resultado de optimización"""
    applied_optimizations: List[str]
    detected_issues: List[PerformanceIssue]
    performance_score: float
    security_score: float
    files_modified: List[str]
    recommendations: List[str]

class PerformanceAgent(GenesisAgent):
    """
    Agente de Performance - Optimización y seguridad
    
    Analiza el código generado para identificar problemas de rendimiento
    y seguridad, aplicando optimizaciones automáticas cuando es posible.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="performance_agent",
            name="PerformanceAgent",
            agent_type="optimization"
        )
        
        # Capacidades del agente
        self.add_capability("performance_analysis")
        self.add_capability("security_audit")
        self.add_capability("database_optimization")
        self.add_capability("frontend_optimization")
        self.add_capability("caching_strategy")
        self.add_capability("monitoring_setup")
        self.add_capability("automated_fixes")
        
        # Registrar handlers específicos
        self.register_handler("analyze_performance", self._handle_analyze_performance)
        self.register_handler("optimize_project", self._handle_optimize_project)
        self.register_handler("security_audit", self._handle_security_audit)
        self.register_handler("optimize_database", self._handle_optimize_database)
        self.register_handler("setup_caching", self._handle_setup_caching)
        self.register_handler("setup_monitoring", self._handle_setup_monitoring)
        
        # Patrones de problemas
        self.performance_patterns = self._load_performance_patterns()
        self.security_patterns = self._load_security_patterns()
        
    async def initialize(self):
        """Inicialización del agente de performance"""
        self.logger.info("⚡ Inicializando Performance Agent")
        
        # Cargar reglas de optimización
        await self._load_optimization_rules()
        
        self.set_metadata("version", "1.0.0")
        self.set_metadata("specialization", "performance_and_security")
        
        self.logger.info("✅ Performance Agent inicializado")
    
    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica de performance"""
        task_name = task.name.lower()
        
        if "analyze_performance" in task_name:
            return await self._analyze_project_performance(task.params)
        elif "optimize_project" in task_name:
            return await self._optimize_complete_project(task.params)
        elif "security_audit" in task_name:
            return await self._perform_security_audit(task.params)
        elif "optimize_database" in task_name:
            return await self._optimize_database_queries(task.params)
        elif "setup_caching" in task_name:
            return await self._setup_caching_strategy(task.params)
        elif "setup_monitoring" in task_name:
            return await self._setup_performance_monitoring(task.params)
        else:
            raise ValueError(f"Tarea no reconocida: {task.name}")
    
    async def _optimize_complete_project(self, params: Dict[str, Any]) -> OptimizationResult:
        """Optimizar proyecto completo"""
        self.logger.info("⚡ Iniciando optimización completa del proyecto")
        
        project_path = Path(params.get("project_path", "./"))
        schema = params.get("schema", {})
        
        all_issues = []
        applied_optimizations = []
        files_modified = []
        
        # 1. Análisis de rendimiento general
        perf_analysis = await self._analyze_project_performance({
            "project_path": project_path,
            "include_security": True
        })
        all_issues.extend(perf_analysis["detected_issues"])
        
        # 2. Optimización de backend
        if (project_path / "backend").exists():
            backend_opts = await self._optimize_backend(project_path / "backend", schema)
            applied_optimizations.extend(backend_opts["optimizations"])
            files_modified.extend(backend_opts["files_modified"])
        
        # 3. Optimización de frontend
        if (project_path / "frontend").exists():
            frontend_opts = await self._optimize_frontend(project_path / "frontend", schema)
            applied_optimizations.extend(frontend_opts["optimizations"])
            files_modified.extend(frontend_opts["files_modified"])
        
        # 4. Optimización de base de datos
        db_opts = await self._optimize_database_queries({
            "project_path": project_path,
            "schema": schema
        })
        applied_optimizations.extend(db_opts["optimizations"])
        
        # 5. Configurar caching
        cache_setup = await self._setup_caching_strategy({
            "project_path": project_path,
            "schema": schema
        })
        applied_optimizations.extend(cache_setup["optimizations"])
        files_modified.extend(cache_setup["files_modified"])
        
        # 6. Configurar monitoreo
        monitoring_setup = await self._setup_performance_monitoring({
            "project_path": project_path
        })
        applied_optimizations.extend(monitoring_setup["optimizations"])
        files_modified.extend(monitoring_setup["files_modified"])
        
        # Calcular scores
        performance_score = self._calculate_performance_score(all_issues, applied_optimizations)
        security_score = self._calculate_security_score(all_issues)
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(all_issues, schema)
        
        result = OptimizationResult(
            applied_optimizations=applied_optimizations,
            detected_issues=all_issues,
            performance_score=performance_score,
            security_score=security_score,
            files_modified=files_modified,
            recommendations=recommendations
        )
        
        # Generar reporte de optimización
        await self._generate_optimization_report(project_path, result)
        
        self.logger.info(f"✅ Optimización completada - Score: {performance_score:.1f}/10")
        return result
    
    async def _analyze_project_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar rendimiento del proyecto"""
        self.logger.info("🔍 Analizando rendimiento del proyecto")
        
        project_path = Path(params.get("project_path", "./"))
        include_security = params.get("include_security", False)
        
        detected_issues = []
        
        # Analizar archivos Python (backend)
        python_files = list(project_path.glob("**/*.py"))
        for py_file in python_files:
            issues = await self._analyze_python_file(py_file)
            detected_issues.extend(issues)
        
        # Analizar archivos TypeScript/JavaScript (frontend)
        js_files = list(project_path.glob("**/*.ts")) + list(project_path.glob("**/*.tsx")) + \
                   list(project_path.glob("**/*.js")) + list(project_path.glob("**/*.jsx"))
        for js_file in js_files:
            issues = await self._analyze_js_file(js_file)
            detected_issues.extend(issues)
        
        # Analizar configuraciones
        config_issues = await self._analyze_configurations(project_path)
        detected_issues.extend(config_issues)
        
        # Análisis de seguridad si está habilitado
        if include_security:
            security_issues = await self._perform_security_audit({
                "project_path": project_path
            })
            detected_issues.extend(security_issues["issues"])
        
        return {
            "detected_issues": detected_issues,
            "total_issues": len(detected_issues),
            "critical_issues": len([i for i in detected_issues if i.severity == SeverityLevel.CRITICAL]),
            "files_analyzed": len(python_files) + len(js_files)
        }
    
    async def _analyze_python_file(self, file_path: Path) -> List[PerformanceIssue]:
        """Analizar archivo Python para issues de rendimiento"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Analizar el AST para problemas comunes
            issues.extend(self._check_python_performance_patterns(tree, file_path, content))
            issues.extend(self._check_python_security_patterns(tree, file_path, content))
            
        except Exception as e:
            self.logger.warning(f"Error analizando {file_path}: {e}")
        
        return issues
    
    def _check_python_performance_patterns(self, tree: ast.AST, file_path: Path, content: str) -> List[PerformanceIssue]:
        """Verificar patrones de rendimiento en Python"""
        issues = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            # Detectar bucles innecesarios
            if isinstance(node, ast.For):
                # Verificar si hay llamadas a len() en cada iteración
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == 'len':
                        issues.append(PerformanceIssue(
                            type=OptimizationType.PERFORMANCE,
                            severity=SeverityLevel.MEDIUM,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description="Llamada a len() dentro de bucle",
                            recommendation="Calcular len() una vez antes del bucle",
                            code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else ""
                        ))
            
            # Detectar concatenación de strings en bucles
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            issues.append(PerformanceIssue(
                                type=OptimizationType.PERFORMANCE,
                                severity=SeverityLevel.MEDIUM,
                                file_path=str(file_path),
                                line_number=child.lineno,
                                description="Concatenación de strings en bucle",
                                recommendation="Usar join() o lista + join() para mejor rendimiento",
                                code_snippet=lines[child.lineno-1] if child.lineno <= len(lines) else ""
                            ))
            
            # Detectar consultas N+1 (patrón común en ORMs)
            if isinstance(node, ast.For):
                for child in ast.walk(node.body[0] if node.body else node):
                    if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
                        if any(keyword in str(child.attr).lower() for keyword in ['query', 'filter', 'get']):
                            issues.append(PerformanceIssue(
                                type=OptimizationType.DATABASE,
                                severity=SeverityLevel.HIGH,
                                file_path=str(file_path),
                                line_number=child.lineno,
                                description="Posible problema N+1 en consultas de base de datos",
                                recommendation="Usar prefetch_related() o select_related() para optimizar consultas",
                                code_snippet=lines[child.lineno-1] if child.lineno <= len(lines) else ""
                            ))
        
        return issues
    
    def _check_python_security_patterns(self, tree: ast.AST, file_path: Path, content: str) -> List[PerformanceIssue]:
        """Verificar patrones de seguridad en Python"""
        issues = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            # Detectar eval() y exec()
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    issues.append(PerformanceIssue(
                        type=OptimizationType.SECURITY,
                        severity=SeverityLevel.CRITICAL,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Uso de {node.func.id}() - riesgo de seguridad",
                        recommendation="Evitar eval() y exec(), usar alternativas más seguras",
                        code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else ""
                    ))
            
            # Detectar SQL queries no parametrizadas
            if isinstance(node, ast.Str) or (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                value = node.value if isinstance(node, ast.Constant) else node.s
                if any(keyword in value.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                    if '%' in value or '.format(' in content[max(0, node.col_offset-50):node.col_offset+50]:
                        issues.append(PerformanceIssue(
                            type=OptimizationType.SECURITY,
                            severity=SeverityLevel.HIGH,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description="Posible SQL injection - query no parametrizada",
                            recommendation="Usar queries parametrizadas o ORMs seguros",
                            code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else ""
                        ))
        
        return issues
    
    async def _analyze_js_file(self, file_path: Path) -> List[PerformanceIssue]:
        """Analizar archivo JS/TS para issues de rendimiento"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Patrones de rendimiento en JavaScript/TypeScript
            for i, line in enumerate(lines, 1):
                # Detectar console.log en producción
                if 'console.log' in line and 'development' not in line:
                    issues.append(PerformanceIssue(
                        type=OptimizationType.PERFORMANCE,
                        severity=SeverityLevel.LOW,
                        file_path=str(file_path),
                        line_number=i,
                        description="console.log encontrado - puede afectar rendimiento en producción",
                        recommendation="Remover console.log o usar logger condicional",
                        code_snippet=line.strip()
                    ))
                
                # Detectar bucles innecesarios en DOM
                if re.search(r'for.*document\.querySelector|while.*document\.querySelector', line):
                    issues.append(PerformanceIssue(
                        type=OptimizationType.FRONTEND,
                        severity=SeverityLevel.MEDIUM,
                        file_path=str(file_path),
                        line_number=i,
                        description="Query DOM dentro de bucle",
                        recommendation="Cachear referencias DOM fuera del bucle",
                        code_snippet=line.strip()
                    ))
                
                # Detectar imágenes sin optimizar
                if re.search(r'<img.*src=.*\.(jpg|jpeg|png)', line):
                    if 'lazy' not in line.lower():
                        issues.append(PerformanceIssue(
                            type=OptimizationType.FRONTEND,
                            severity=SeverityLevel.MEDIUM,
                            file_path=str(file_path),
                            line_number=i,
                            description="Imagen sin lazy loading",
                            recommendation="Agregar loading='lazy' a las imágenes",
                            code_snippet=line.strip()
                        ))
                
                # Detectar useEffect sin dependencias
                if 'useEffect(' in line and i < len(lines) - 1:
                    next_lines = '\n'.join(lines[i:i+5])
                    if '},[])' not in next_lines and '},[' not in next_lines:
                        issues.append(PerformanceIssue(
                            type=OptimizationType.FRONTEND,
                            severity=SeverityLevel.MEDIUM,
                            file_path=str(file_path),
                            line_number=i,
                            description="useEffect sin array de dependencias",
                            recommendation="Agregar array de dependencias a useEffect",
                            code_snippet=line.strip()
                        ))
        
        except Exception as e:
            self.logger.warning(f"Error analizando {file_path}: {e}")
        
        return issues
    
    async def _optimize_backend(self, backend_path: Path, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar código backend"""
        optimizations = []
        files_modified = []
        
        # Optimizar modelos de base de datos
        models_dir = backend_path / "app" / "models"
        if models_dir.exists():
            for model_file in models_dir.glob("*.py"):
                if await self._optimize_database_model(model_file):
                    optimizations.append(f"Optimizado modelo: {model_file.name}")
                    files_modified.append(str(model_file))
        
        # Agregar índices de base de datos
        db_optimizations = await self._add_database_indexes(backend_path, schema)
        optimizations.extend(db_optimizations)
        
        # Configurar rate limiting
        if await self._setup_rate_limiting(backend_path):
            optimizations.append("Configurado rate limiting")
            files_modified.append(str(backend_path / "app" / "middleware" / "rate_limit.py"))
        
        # Configurar compresión
        if await self._setup_compression(backend_path):
            optimizations.append("Configurada compresión de respuestas")
            files_modified.append(str(backend_path / "app" / "main.py"))
        
        return {
            "optimizations": optimizations,
            "files_modified": files_modified
        }
    
    async def _optimize_frontend(self, frontend_path: Path, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar código frontend"""
        optimizations = []
        files_modified = []
        
        # Optimizar configuración de Next.js
        next_config = frontend_path / "next.config.js"
        if next_config.exists():
            if await self._optimize_next_config(next_config):
                optimizations.append("Optimizada configuración de Next.js")
                files_modified.append(str(next_config))
        
        # Agregar lazy loading a imágenes
        image_optimizations = await self._optimize_images(frontend_path)
        optimizations.extend(image_optimizations["optimizations"])
        files_modified.extend(image_optimizations["files_modified"])
        
        # Optimizar componentes React
        component_optimizations = await self._optimize_react_components(frontend_path)
        optimizations.extend(component_optimizations["optimizations"])
        files_modified.extend(component_optimizations["files_modified"])
        
        return {
            "optimizations": optimizations,
            "files_modified": files_modified
        }
    
    def analyze_python_complexity(code: str) -> Dict[str, Any]:
        """Analizar complejidad del código Python"""
        try:
             tree = ast.parse(code)
                
             complexity_visitor = ComplexityVisitor()
             complexity_visitor.visit(tree)
                
             return {
                "cyclomatic_complexity": complexity_visitor.complexity,
                "function_count": complexity_visitor.function_count,
                "class_count": complexity_visitor.class_count,
                "max_depth": complexity_visitor.max_depth
            }
        except SyntaxError:
             return {"error": "Syntax error in code"}

    class ComplexityVisitor(ast.NodeVisitor):
        """Visitor para calcular complejidad ciclomática"""
        
        def __init__(self):
            self.complexity = 1  # Base complexity
            self.function_count = 0
            self.class_count = 0
            self.max_depth = 0
            self.current_depth = 0
        
        def visit_FunctionDef(self, node):
            self.function_count += 1
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        
        def visit_ClassDef(self, node):
            self.class_count += 1
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        
        def visit_If(self, node):
            self.complexity += 1
            self.generic_visit(node)
        
        def visit_While(self, node):
            self.complexity += 1
            self.generic_visit(node)
        
        def visit_For(self, node):
            self.complexity += 1
            self.generic_visit(node)

    
    def _calculate_performance_score(self, issues: List[PerformanceIssue], optimizations: List[str]) -> float:
        """Calcular puntuación de rendimiento"""
        # Empezar con score perfecto
        score = 10.0
        
        # Restar puntos por issues
        for issue in issues:
            if issue.severity == SeverityLevel.CRITICAL:
                score -= 2.0
            elif issue.severity == SeverityLevel.HIGH:
                score -= 1.0
            elif issue.severity == SeverityLevel.MEDIUM:
                score -= 0.5
            elif issue.severity == SeverityLevel.LOW:
                score -= 0.2
        
        # Sumar puntos por optimizaciones aplicadas
        score += len(optimizations) * 0.1
        
        return max(0.0, min(10.0, score))
    
    def _calculate_security_score(self, issues: List[PerformanceIssue]) -> float:
        """Calcular puntuación de seguridad"""
        security_issues = [i for i in issues if i.type == OptimizationType.SECURITY]
        
        if not security_issues:
            return 10.0
        
        score = 10.0
        for issue in security_issues:
            if issue.severity == SeverityLevel.CRITICAL:
                score -= 3.0
            elif issue.severity == SeverityLevel.HIGH:
                score -= 2.0
            elif issue.severity == SeverityLevel.MEDIUM:
                score -= 1.0
            elif issue.severity == SeverityLevel.LOW:
                score -= 0.5
        
        return max(0.0, score)
    
    # Handlers MCP
    async def _handle_analyze_performance(self, request) -> Dict[str, Any]:
        """Handler para análisis de rendimiento"""
        result = await self._analyze_project_performance(request.params)
        return {
            "detected_issues": [
                {
                    "type": issue.type.value,
                    "severity": issue.severity.value,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "description": issue.description,
                    "recommendation": issue.recommendation
                }
                for issue in result["detected_issues"]
            ],
            "total_issues": result["total_issues"],
            "critical_issues": result["critical_issues"],
            "files_analyzed": result["files_analyzed"]
        }
    
    async def _handle_optimize_project(self, request) -> Dict[str, Any]:
        """Handler para optimización completa"""
        result = await self._optimize_complete_project(request.params)
        return {
            "applied_optimizations": result.applied_optimizations,
            "performance_score": result.performance_score,
            "security_score": result.security_score,
            "files_modified": result.files_modified,
            "recommendations": result.recommendations,
            "total_issues": len(result.detected_issues)
        }
    
    async def _handle_security_audit(self, request) -> Dict[str, Any]:
        """Handler para auditoría de seguridad"""
        result = await self._perform_security_audit(request.params)
        return result
    
    async def _handle_optimize_database(self, request) -> Dict[str, Any]:
        """Handler para optimización de base de datos"""
        result = await self._optimize_database_queries(request.params)
        return result
    
    async def _handle_setup_caching(self, request) -> Dict[str, Any]:
        """Handler para configuración de cache"""
        result = await self._setup_caching_strategy(request.params)
        return result
    
    async def _handle_setup_monitoring(self, request) -> Dict[str, Any]:
        """Handler para configuración de monitoreo"""
        result = await self._setup_performance_monitoring(request.params)
        return result
    
    # Métodos auxiliares (implementación simplificada)
    def _load_performance_patterns(self) -> Dict[str, Any]:
        """Cargar patrones de rendimiento"""
        return {}
    
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Cargar patrones de seguridad"""
        return {}
    
    async def _load_optimization_rules(self):
        """Cargar reglas de optimización"""
        pass
    
    async def _analyze_configurations(self, project_path: Path) -> List[PerformanceIssue]:
        """Analizar archivos de configuración"""
        return []
    
    async def _perform_security_audit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Realizar auditoría de seguridad"""
        return {"issues": []}
    
    async def _optimize_database_queries(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar consultas de base de datos"""
        return {"optimizations": []}
    
    async def _setup_caching_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configurar estrategia de cache"""
        return {"optimizations": [], "files_modified": []}
    
    async def _setup_performance_monitoring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configurar monitoreo de rendimiento"""
        return {"optimizations": [], "files_modified": []}
    
    async def _optimize_database_model(self, model_file: Path) -> bool:
        """Optimizar modelo de base de datos"""
        return False
    
    async def _add_database_indexes(self, backend_path: Path, schema: Dict[str, Any]) -> List[str]:
        """Agregar índices de base de datos"""
        return []
    
    async def _setup_rate_limiting(self, backend_path: Path) -> bool:
        """Configurar rate limiting"""
        return False
    
    async def _setup_compression(self, backend_path: Path) -> bool:
        """Configurar compresión"""
        return False
    
    async def _optimize_next_config(self, next_config: Path) -> bool:
        """Optimizar configuración de Next.js"""
        return False
    
    async def _optimize_images(self, frontend_path: Path) -> Dict[str, Any]:
        """Optimizar imágenes"""
        return {"optimizations": [], "files_modified": []}
    
    async def _optimize_react_components(self, frontend_path: Path) -> Dict[str, Any]:
        """Optimizar componentes React"""
        return {"optimizations": [], "files_modified": []}
    
    def _generate_recommendations(self, issues: List[PerformanceIssue], schema: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones"""
        recommendations = []
        
        # Agrupar por tipo
        issue_types = {}
        for issue in issues:
            if issue.type not in issue_types:
                issue_types[issue.type] = []
            issue_types[issue.type].append(issue)
        
        # Generar recomendaciones por tipo
        if OptimizationType.DATABASE in issue_types:
            recommendations.append("Considerar implementar connection pooling para la base de datos")
            recommendations.append("Revisar y optimizar índices de base de datos")
        
        if OptimizationType.FRONTEND in issue_types:
            recommendations.append("Implementar code splitting y lazy loading")
            recommendations.append("Optimizar imágenes y usar formatos modernos (WebP, AVIF)")
        
        if OptimizationType.SECURITY in issue_types:
            recommendations.append("Implementar Content Security Policy (CSP)")
            recommendations.append("Configurar HTTPS y headers de seguridad")
        
        return recommendations
    
    async def _generate_optimization_report(self, project_path: Path, result: OptimizationResult):
        """Generar reporte de optimización"""
        report_content = f"""# Reporte de Optimización

## Resumen
- **Performance Score**: {result.performance_score:.1f}/10
- **Security Score**: {result.security_score:.1f}/10
- **Optimizaciones Aplicadas**: {len(result.applied_optimizations)}
- **Issues Detectados**: {len(result.detected_issues)}
- **Archivos Modificados**: {len(result.files_modified)}

## Optimizaciones Aplicadas

"""
        
        for opt in result.applied_optimizations:
            report_content += f"- ✅ {opt}\n"
        
        report_content += "\n## Issues Detectados\n\n"
        
        for issue in result.detected_issues:
            severity_emoji = {
                SeverityLevel.CRITICAL: "🔴",
                SeverityLevel.HIGH: "🟠", 
                SeverityLevel.MEDIUM: "🟡",
                SeverityLevel.LOW: "🟢"
            }
            
            report_content += f"### {severity_emoji[issue.severity]} {issue.description}\n\n"
            report_content += f"- **Archivo**: {issue.file_path}\n"
            if issue.line_number:
                report_content += f"- **Línea**: {issue.line_number}\n"
            report_content += f"- **Recomendación**: {issue.recommendation}\n\n"
        
        report_content += "\n## Recomendaciones\n\n"
        
        for rec in result.recommendations:
            report_content += f"- 💡 {rec}\n"
        
        # Guardar reporte
        report_file = project_path / ".genesis" / "optimization_report.md"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report_content)
        
        self.logger.info(f"📄 Reporte de optimización generado: {report_file}")