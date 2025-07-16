"""
Genesis Engine CLI Commands

Implementación de todos los comandos de la CLI de Genesis Engine.
"""

import asyncio
import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, ProjectGenerationRequest
from genesis_engine.core.config import GenesisConfig, Features

try:
    from genesis_engine.utils.validation import validate_project_name, validate_stack_config
except Exception:  # pragma: no cover - fallback if validation utils missing
    def validate_project_name(name: str):
        return []

    def validate_stack_config(stack):
        return []

console = Console()

# ===== CREATE COMMAND =====

create_app = typer.Typer(name="create", help="🏗️ Crear nuevo proyecto Genesis")

@create_app.command("project")
def create_project(
    name: str = typer.Argument(..., help="Nombre del proyecto"),
    template: str = typer.Option("saas-basic", "--template", "-t", help="Template a usar"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Directorio de salida"),
    stack_backend: Optional[str] = typer.Option(None, "--backend", help="Framework backend"),
    stack_frontend: Optional[str] = typer.Option(None, "--frontend", help="Framework frontend"),
    stack_database: Optional[str] = typer.Option(None, "--database", help="Base de datos"),
    features: Optional[List[str]] = typer.Option(None, "--feature", help="Características a incluir"),
    ai_ready: bool = typer.Option(False, "--ai-ready", help="Preparar para IA"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Modo interactivo"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simular sin crear archivos")
):
    """Crear un nuevo proyecto Genesis"""
    
    console.print(Panel.fit(
        "🚀 Genesis Engine Project Creator",
        style="bold magenta"
    ))
    
    # Validar nombre del proyecto
    name_errors = validate_project_name(name)
    if name_errors:
        console.print("[red]❌ Errores en el nombre del proyecto:[/red]")
        for error in name_errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)
    
    # Configurar stack
    stack = {}
    if template in ["saas-basic", "golden-path"]:
        stack = GenesisConfig.get_stack_config("golden-path")
    elif template == "api-first":
        stack = GenesisConfig.get_stack_config("api-first") 
    elif template == "ecommerce":
        stack = GenesisConfig.get_stack_config("ecommerce")
    
    # Sobrescribir con opciones específicas
    if stack_backend:
        stack["backend"] = stack_backend
    if stack_frontend:
        stack["frontend"] = stack_frontend
    if stack_database:
        stack["database"] = stack_database
    
    # Validar configuración del stack
    stack_errors = validate_stack_config(stack)
    if stack_errors:
        console.print("[red]❌ Errores en configuración del stack:[/red]")
        for error in stack_errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)
    
    # Configurar características
    project_features = features or []
    if ai_ready:
        project_features.extend(["ai_chat", "ai_assistant"])
    
    # Modo interactivo
    if interactive and not dry_run:
        project_features = _interactive_feature_selection(project_features)
        stack = _interactive_stack_configuration(stack)
    
    # Configurar directorio de salida
    if output_dir is None:
        output_dir = Path.cwd() / name
    else:
        output_dir = output_dir / name
    
    # Configuración del proyecto
    project_config = {
        "name": name,
        "template": template,
        "description": f"Proyecto {name} generado con Genesis Engine",
        "stack": stack,
        "features": project_features,
        "output_path": str(output_dir),
        "ai_ready": ai_ready,
        "dry_run": dry_run
    }
    
    if dry_run:
        _show_dry_run_summary(project_config)
        return
    
    # Crear proyecto
    console.print(f"\n[green]🏗️ Creando proyecto '{name}'...[/green]")
    
    try:
        # Ejecutar creación asíncrona
        result = asyncio.run(_create_project_async(project_config))
        
        if result.success:
            _show_success_message(name, output_dir, stack, project_features)
        else:
            console.print(f"[red]❌ Error: {result.error}[/red]")
            raise typer.Exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Creación cancelada por el usuario[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
        raise typer.Exit(1)

async def _create_project_async(config):
    """Crear proyecto de manera asíncrona"""
    orchestrator = CoreOrchestrator()
    request = ProjectGenerationRequest(
        name=config.get("name", "project"),
        template=config.get("template", "default"),
        features=config.get("features", []),
        options=config,
    )
    return await orchestrator.execute_project_generation(request)

def _interactive_feature_selection(current_features: List[str]) -> List[str]:
    """Selección interactiva de características"""
    console.print("\n[bold]🎯 Seleccionar características:[/bold]")
    
    available_features = {
        Features.AUTHENTICATION: "Autenticación de usuarios (JWT, OAuth)",
        Features.AUTHORIZATION: "Sistema de roles y permisos", 
        Features.BILLING: "Facturación y subscripciones (Stripe)",
        Features.NOTIFICATIONS: "Sistema de notificaciones",
        Features.FILE_UPLOAD: "Subida y gestión de archivos",
        Features.SEARCH: "Búsqueda y filtros avanzados",
        Features.ANALYTICS: "Analytics y métricas",
        Features.ADMIN_PANEL: "Panel de administración",
        Features.AI_CHAT: "Chat con IA",
        Features.MONITORING: "Monitoreo y logs",
    }
    
    selected_features = list(current_features)
    
    for feature, description in available_features.items():
        default = feature in selected_features
        include = typer.confirm(
            f"  Incluir {description}?",
            default=default
        )
        
        if include and feature not in selected_features:
            selected_features.append(feature)
        elif not include and feature in selected_features:
            selected_features.remove(feature)
    
    return selected_features

def _interactive_stack_configuration(current_stack: dict) -> dict:
    """Configuración interactiva del stack"""
    console.print("\n[bold]⚙️ Configurar stack tecnológico:[/bold]")
    
    stack = dict(current_stack)
    
    # Backend
    backend_options = GenesisConfig.get_supported_frameworks("backend")
    if len(backend_options) > 1:
        console.print(f"Backend actual: [cyan]{stack.get('backend', 'ninguno')}[/cyan]")
        console.print("Opciones: " + ", ".join(backend_options))
        new_backend = typer.prompt("Backend", default=stack.get('backend', backend_options[0]))
        if new_backend in backend_options:
            stack['backend'] = new_backend
    
    # Frontend
    frontend_options = GenesisConfig.get_supported_frameworks("frontend")
    if len(frontend_options) > 1:
        console.print(f"Frontend actual: [cyan]{stack.get('frontend', 'ninguno')}[/cyan]")
        console.print("Opciones: " + ", ".join(frontend_options))
        new_frontend = typer.prompt("Frontend", default=stack.get('frontend', frontend_options[0]))
        if new_frontend in frontend_options:
            stack['frontend'] = new_frontend
    
    # Base de datos
    db_options = GenesisConfig.get_supported_frameworks("database")
    if len(db_options) > 1:
        console.print(f"Base de datos actual: [cyan]{stack.get('database', 'ninguno')}[/cyan]")
        console.print("Opciones: " + ", ".join(db_options))
        new_db = typer.prompt("Base de datos", default=stack.get('database', db_options[0]))
        if new_db in db_options:
            stack['database'] = new_db
    
    return stack

def _show_dry_run_summary(config: dict):
    """Mostrar resumen de dry run"""
    console.print("\n[bold yellow]🧪 Dry Run - Resumen del proyecto:[/bold yellow]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Configuración")
    table.add_column("Valor")
    
    table.add_row("Nombre", config['name'])
    table.add_row("Template", config['template'])
    table.add_row("Directorio", config['output_path'])
    table.add_row("Backend", config['stack'].get('backend', 'N/A'))
    table.add_row("Frontend", config['stack'].get('frontend', 'N/A'))
    table.add_row("Base de datos", config['stack'].get('database', 'N/A'))
    table.add_row("Características", ", ".join(config['features']) if config['features'] else "Ninguna")
    table.add_row("AI Ready", "Sí" if config['ai_ready'] else "No")
    
    console.print(table)

def _show_success_message(name: str, output_dir: Path, stack: dict, features: List[str]):
    """Mostrar mensaje de éxito"""
    console.print(f"\n[bold green]✅ Proyecto '{name}' creado exitosamente![/bold green]")
    console.print(f"📁 Ubicación: [cyan]{output_dir}[/cyan]")
    
    # Mostrar stack usado
    console.print(f"\n[bold]📋 Stack generado:[/bold]")
    for key, value in stack.items():
        console.print(f"  • {key.title()}: [cyan]{value}[/cyan]")
    
    # Mostrar características
    if features:
        console.print(f"\n[bold]🎯 Características incluidas:[/bold]")
        for feature in features:
            console.print(f"  • {feature}")
    
    # Siguientes pasos
    console.print(f"\n[bold yellow]🚀 Siguientes pasos:[/bold yellow]")
    console.print(f"1. [dim]cd {name}[/dim]")
    console.print("2. [dim]genesis deploy --local[/dim]")
    console.print("3. [dim]genesis status[/dim]")

# ===== DEPLOY COMMAND =====

deploy_app = typer.Typer(name="deploy", help="🚀 Desplegar proyecto")

@deploy_app.command("local")
def deploy_local(
    project_path: Optional[Path] = typer.Option(None, "--path", "-p", help="Ruta del proyecto"),
    dev_mode: bool = typer.Option(False, "--dev", help="Modo desarrollo"),
    detached: bool = typer.Option(True, "--detached/--attached", help="Ejecutar en background")
):
    """Desplegar proyecto localmente"""
    
    if project_path is None:
        project_path = Path.cwd()
    
    console.print(f"🚀 Desplegando proyecto local en: [cyan]{project_path}[/cyan]")
    
    # Verificar que existe genesis.json
    genesis_file = project_path / "genesis.json"
    if not genesis_file.exists():
        console.print("[red]❌ No se encontró genesis.json. ¿Estás en un proyecto Genesis?[/red]")
        raise typer.Exit(1)
    
    try:
        result = asyncio.run(_deploy_local_async(project_path, dev_mode, detached))
        
        if result['success']:
            console.print("[green]✅ Despliegue completado[/green]")
            
            for url in result.get('urls', []):
                console.print(f"🌐 Disponible en: [cyan]{url}[/cyan]")
        else:
            console.print(f"[red]❌ Error en despliegue: {result.get('error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)

async def _deploy_local_async(project_path: Path, dev_mode: bool, detached: bool):
    """Desplegar localmente de manera asíncrona"""
    from genesis_engine.agents.deploy import DeployAgent
    
    agent = DeployAgent()
    await agent.initialize()
    
    result = await agent.execute_task({
        "name": "deploy_local",
        "params": {
            "project_path": str(project_path),
            "target": "local",
            "environment": "development" if dev_mode else "production",
            "detached": detached
        }
    })
    
    return result

# ===== STATUS COMMAND =====

status_app = typer.Typer(name="status", help="📊 Estado del proyecto")

@status_app.command("project")
def status_project(
    project_path: Optional[Path] = typer.Option(None, "--path", "-p", help="Ruta del proyecto")
):
    """Mostrar estado del proyecto"""
    
    if project_path is None:
        project_path = Path.cwd()
    
    console.print(f"📊 Estado del proyecto en: [cyan]{project_path}[/cyan]")
    
    # Verificar que existe genesis.json
    genesis_file = project_path / "genesis.json"
    if not genesis_file.exists():
        console.print("[red]❌ No se encontró genesis.json[/red]")
        raise typer.Exit(1)
    
    try:
        # Cargar metadata del proyecto
        import json
        with open(genesis_file, 'r') as f:
            project_data = json.load(f)
        
        _show_project_status(project_data, project_path)
        
    except Exception as e:
        console.print(f"[red]❌ Error leyendo proyecto: {str(e)}[/red]")

def _show_project_status(project_data: dict, project_path: Path):
    """Mostrar estado detallado del proyecto"""
    
    # Información básica
    table = Table(title="📋 Información del Proyecto", show_header=True)
    table.add_column("Campo")
    table.add_column("Valor")
    
    table.add_row("Nombre", project_data.get('name', 'N/A'))
    table.add_row("Versión", project_data.get('version', 'N/A'))
    table.add_row("Generado", project_data.get('generated_at', 'N/A'))
    table.add_row("Generator", project_data.get('generator', 'N/A'))
    
    console.print(table)
    
    # Archivos generados
    generated_files = project_data.get('generated_files', [])
    if generated_files:
        console.print(f"\n[bold]📁 Archivos generados ({len(generated_files)}):[/bold]")
        for file_path in generated_files[:10]:  # Mostrar solo los primeros 10
            file_full_path = project_path / file_path
            status = "✅" if file_full_path.exists() else "❌"
            console.print(f"  {status} {file_path}")
        
        if len(generated_files) > 10:
            console.print(f"  ... y {len(generated_files) - 10} archivos más")
    
    # Verificar servicios corriendo
    _check_running_services(project_path)

def _check_running_services(project_path: Path):
    """Verificar servicios corriendo"""
    console.print("\n[bold]🔍 Verificando servicios:[/bold]")
    
    # Verificar Docker Compose
    docker_compose = project_path / "docker-compose.yml"
    if docker_compose.exists():
        try:
            import subprocess
            result = subprocess.run(
                ["docker-compose", "ps", "--services", "--filter", "status=running"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                services = result.stdout.strip().split('\n')
                console.print(f"  🐳 Docker Compose: [green]{len(services)} servicios corriendo[/green]")
                for service in services:
                    console.print(f"    • {service}")
            else:
                console.print("  🐳 Docker Compose: [yellow]No hay servicios corriendo[/yellow]")
                
        except FileNotFoundError:
            console.print("  🐳 Docker Compose: [red]Docker no encontrado[/red]")
    else:
        console.print("  🐳 Docker Compose: [dim]No configurado[/dim]")

# ===== OPTIMIZE COMMAND =====

optimize_app = typer.Typer(name="optimize", help="⚡ Optimizar proyecto")

@optimize_app.command("performance")
def optimize_performance(
    project_path: Optional[Path] = typer.Option(None, "--path", "-p", help="Ruta del proyecto"),
    include_security: bool = typer.Option(True, "--security", help="Incluir auditoría de seguridad"),
    auto_fix: bool = typer.Option(False, "--auto-fix", help="Aplicar correcciones automáticas")
):
    """Optimizar rendimiento del proyecto"""
    
    if project_path is None:
        project_path = Path.cwd()
    
    console.print(f"⚡ Optimizando proyecto en: [cyan]{project_path}[/cyan]")
    
    try:
        result = asyncio.run(_optimize_performance_async(
            project_path, include_security, auto_fix
        ))
        
        _show_optimization_results(result)
        
    except Exception as e:
        console.print(f"[red]❌ Error en optimización: {str(e)}[/red]")

async def _optimize_performance_async(project_path: Path, include_security: bool, auto_fix: bool):
    """Optimizar rendimiento de manera asíncrona"""
    from genesis_engine.agents.performance import PerformanceAgent
    
    agent = PerformanceAgent()
    await agent.initialize()
    
    result = await agent.execute_task({
        "name": "optimize_project",
        "params": {
            "project_path": str(project_path),
            "include_security": include_security,
            "auto_fix": auto_fix
        }
    })
    
    return result

def _show_optimization_results(result: dict):
    """Mostrar resultados de optimización"""
    console.print("\n[bold green]✅ Optimización completada[/bold green]")
    
    # Scores
    perf_score = result.get('performance_score', 0)
    sec_score = result.get('security_score', 0)
    
    console.print(f"📊 Performance Score: [cyan]{perf_score:.1f}/10[/cyan]")
    console.print(f"🔒 Security Score: [cyan]{sec_score:.1f}/10[/cyan]")
    
    # Optimizaciones aplicadas
    optimizations = result.get('applied_optimizations', [])
    if optimizations:
        console.print(f"\n[bold]🔧 Optimizaciones aplicadas ({len(optimizations)}):[/bold]")
        for opt in optimizations:
            console.print(f"  ✅ {opt}")
    
    # Recomendaciones
    recommendations = result.get('recommendations', [])
    if recommendations:
        console.print(f"\n[bold]💡 Recomendaciones:[/bold]")
        for rec in recommendations:
            console.print(f"  • {rec}")

# Exportar apps
__all__ = [
    "create_app",
    "deploy_app", 
    "status_app",
    "optimize_app"
]