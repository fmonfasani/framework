#!/usr/bin/env python3
"""
Genesis Engine CLI - Entry Point Principal
"""

import sys
import asyncio
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import typer
from typer.main import get_command
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from concurrent.futures import ThreadPoolExecutor

# Importar componentes core
from genesis_engine.core.exceptions import GenesisException, ProjectCreationError
from genesis_engine.core.orchestrator import GenesisOrchestrator
from genesis_engine.core.config import initialize
from genesis_engine.core.logging import get_logger
from genesis_engine import __version__

# Configurar Rich Console
console = Console()
logger = get_logger("genesis.cli")

def version_callback(value: bool):
    """Callback para mostrar la versión y salir"""
    if value:
        console.print(f"[bold green]Genesis Engine v{__version__}[/bold green]")
        raise typer.Exit()

def show_banner():
    """Mostrar banner de Genesis Engine"""
    banner = """
    ██████╗ ███████╗███╗   ██╗███████╗███████╗██╗███████╗
    ██╔══╗  ██╔════╝████╗  ██║██╔════╝██╔════╝██║██╔════╝
    ██║███║ █████╗  ██╔██╗ ██║█████╗  ███████╗██║███████╗
    ██║ ██║ ██╔══╝  ██║╚██╗██║██╔══╝  ╚════██║██║╚════██║
    ██████╔╝███████╗██║ ╚████║███████╗███████║██║███████║
    ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝╚══════╝
    """
    console.print(Panel(
        banner,
        title="[INIT] Genesis Engine",
        subtitle="Sistema operativo para desarrollo full-stack",
        border_style="bright_blue"
    ))

def validate_project_name(name: str) -> bool:
    """Validar nombre de proyecto"""
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        console.print("[red][ERROR] Nombre de proyecto inválido. Use solo letras, números, _ y -[/red]")
        return False
    
    if len(name) < 2 or len(name) > 50:
        console.print("[red][ERROR] Nombre debe tener entre 2 y 50 caracteres[/red]")
        return False
    
    return True

def check_dependencies() -> bool:
    """Verificar dependencias del sistema"""
    import subprocess
    import shutil
    
    dependencies = [
        ("python", "python --version", "Python 3.9+"),
        ("node", "node --version", "Node.js 18+"),
        ("git", "git --version", "Git"),
        ("docker", "docker --version", "Docker (opcional)")
    ]
    
    all_ok = True
    table = Table(title="[CHECK] Verificación de Dependencias")
    table.add_column("Dependencia", style="cyan")
    table.add_column("Estado", style="green")
    table.add_column("Versión", style="yellow")
    
    for name, cmd, required in dependencies:
        try:
            result = subprocess.run(
                cmd.split(), 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                table.add_row(name, "[PASS] Instalado", version)
            else:
                table.add_row(name, "[ERROR] Error", "No disponible")
                if name != "docker":  # Docker es opcional
                    all_ok = False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            table.add_row(name, "[ERROR] No encontrado", required)
            if name != "docker":  # Docker es opcional
                all_ok = False
    
    console.print(table)
    return all_ok

# Crear aplicación Typer principal
app = typer.Typer(
    name="genesis",
    help="[INIT] Genesis Engine - Sistema operativo para desarrollo full-stack moderno",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True
)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Mostrar versión de Genesis Engine",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Mostrar información detallada"
    ),
    skip_project_check: bool = typer.Option(
        False,
        "--skip-project-check",
        help="Omitir verificación de genesis.json (solo pruebas)",
        envvar="GENESIS_SKIP_PROJECT_CHECK",
        hidden=True,
    )
):
    """
    [INIT] Genesis Engine - Sistema operativo para desarrollo full-stack moderno

    Genesis Engine te permite crear, optimizar y desplegar aplicaciones
    completas usando agentes IA especializados que se comunican via MCP.
    """
    if ctx.invoked_subcommand is None:
        show_banner()
        console.print("\n[bold yellow][INFO] Usa 'genesis --help' para ver comandos disponibles[/bold yellow]")
        console.print("[bold yellow][INFO] Usa 'genesis init <nombre>' para crear un proyecto[/bold yellow]")
        
    # Inicializar configuración
    try:
        initialize()
        if verbose:
            logger.info("Configuración inicializada en modo verbose")
    except Exception as e:
        console.print(f"[red][ERROR] Error inicializando configuración: {e}[/red]")
        raise typer.Exit(1)

    ctx.obj = {"skip_project_check": skip_project_check}

@app.command("init")
def init(
    project_name: str = typer.Argument(
        help="Nombre del proyecto a crear"
    ),
    template: str = typer.Option(
        "saas-basic",
        "--template",
        "-t",
        help="Plantilla a usar (disponible: saas-basic)"
    ),
    no_interactive: bool = typer.Option(
        False,
        "--no-interactive",
        help="Modo no interactivo, usar valores por defecto"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        "-o", 
        help="Directorio de salida (por defecto: directorio actual)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Sobrescribir proyecto existente"
    )
):
    """
    [TARGET] Inicializar un nuevo proyecto full-stack
    
    Crea un proyecto completo usando el Golden Path seleccionado.
    Los agentes IA trabajarán en conjunto para generar:
    
    • Backend (FastAPI, Node.js, etc.)
    • Frontend (Next.js, React, Vue, etc.) 
    • DevOps (Docker, CI/CD)
    • Base de datos y migraciones
    • Configuración completa
    """
    try:
        # Validar nombre del proyecto
        if not validate_project_name(project_name):
            raise typer.Exit(1)
        
        # Validar directorio de salida
        if output_dir:
            output_path = Path(output_dir)
            if not output_path.exists():
                console.print(f"[red][ERROR] Directorio de salida no existe: {output_dir}[/red]")
                raise typer.Exit(1)
        else:
            output_path = Path.cwd()
        
        project_path = output_path / project_name
        
        # Verificar si el proyecto ya existe
        if project_path.exists() and not force:
            if not no_interactive:
                if not Confirm.ask(f"[yellow][WARN] El directorio '{project_name}' ya existe. ¿Continuar?[/yellow]"):
                    console.print("[yellow]Operación cancelada[/yellow]")
                    raise typer.Exit(0)
            else:
                console.print(f"[red][ERROR] El directorio '{project_name}' ya existe. Use --force para sobrescribir[/red]")
                raise typer.Exit(1)
        
        # Verificar dependencias
        if not check_dependencies():
            console.print("[red][ERROR] Algunas dependencias no están disponibles[/red]")
            if not no_interactive:
                if not Confirm.ask("[yellow]¿Continuar de todos modos?[/yellow]"):
                    raise typer.Exit(1)
            else:
                raise typer.Exit(1)
        
        # Configurar proyecto
        config = {
            "name": project_name,
            "template": template,
            "output_path": str(output_path),
            "force": force,
            "interactive": not no_interactive
        }
        
        # Modo interactivo para configuración adicional
        if not no_interactive:
            config["description"] = Prompt.ask(
                "[cyan]Descripción del proyecto[/cyan]", 
                default="Aplicación generada con Genesis Engine"
            )
            
            # Seleccionar características
            features = []
            feature_options = [
                ("authentication", "[SECURE] Autenticación y autorización"),
                ("database", "[SAVE] Base de datos PostgreSQL"),
                ("api", "🔌 API REST completa"),
                ("frontend", "[UI] Frontend moderno"),
                ("docker", "[DOCKER] Containerización Docker"),
                ("ci_cd", "[INIT] CI/CD Pipeline")
            ]
            
            console.print("\n[bold cyan]Selecciona características (Enter para todas):[/bold cyan]")
            for key, desc in feature_options:
                features.append(key)
                console.print(f"  [PASS] {desc}")
            
            config["features"] = features
        else:
            config["description"] = "Aplicación generada con Genesis Engine"
            config["features"] = ["authentication", "database", "api", "frontend", "docker", "ci_cd"]
        
        # Ejecutar creación del proyecto
        console.print(f"\n[bold green][INIT] Creando proyecto '{project_name}'...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Inicializando orquestador...", total=None)
            
            # Crear y ejecutar orquestador
            result = asyncio.run(_create_project_async(config, progress, task))
            
            if result.success:
                console.print(f"\n[bold green][PASS] Proyecto '{project_name}' creado exitosamente![/bold green]")
                console.print(f"[green][DIR] Ubicación: {result.project_path}[/green]")
                
                if result.generated_files:
                    console.print(f"[green]📄 Archivos generados: {len(result.generated_files)}[/green]")
                
                # Mostrar siguientes pasos
                console.print("\n[bold cyan][TARGET] Siguientes pasos:[/bold cyan]")
                console.print(f"1. cd {project_name}")
                console.print("2. docker-compose up -d")
                console.print("3. Abrir http://localhost:3000")
                
            else:
                console.print(f"\n[red][ERROR] Error creando proyecto: {result.error}[/red]")
                raise typer.Exit(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow][WARN] Operación cancelada por el usuario[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Error en init: {e}", exc_info=True)
        console.print(f"[red][ERROR] Error inesperado: {e}[/red]")
        raise typer.Exit(1)

async def _create_project_async(config: Dict[str, Any], progress: Progress, task_id) -> Any:
    """Crear proyecto de forma asíncrona"""
    orchestrator = GenesisOrchestrator()
    
    try:
        progress.update(task_id, description="Inicializando orquestador...")
        await orchestrator.initialize()
        
        progress.update(task_id, description="Creando proyecto...")
        result = await orchestrator.create_project(config)
        
        return result
        
    except Exception as e:
        logger.error(f"Error en creación asíncrona: {e}", exc_info=True)
        from genesis_engine.core.orchestrator import ProjectCreationResult
        return ProjectCreationResult(
            success=False,
            error=str(e)
        )
    finally:
        try:
            await orchestrator.shutdown()
        except Exception as e:
            logger.warning(f"Error cerrando orquestador: {e}")

@app.command("doctor") 
def doctor():
    """
    [CHECK] Diagnosticar el entorno y verificar dependencias
    
    Ejecuta un diagnóstico completo del entorno de desarrollo:
    
    • Verifica instalación de Python, Node.js, Docker
    • Chequea conectividad de red
    • Valida configuración de agentes
    • Ejecuta tests de comunicación MCP
    """
    try:
        console.print("[bold blue][CHECK] Diagnóstico del Sistema Genesis[/bold blue]")
        
        # Verificar dependencias
        deps_ok = check_dependencies()
        
        # Verificar configuración
        console.print("\n[bold cyan]⚙️ Verificando configuración...[/bold cyan]")
        try:
            initialize()
            console.print("[green][PASS] Configuración OK[/green]")
        except Exception as e:
            console.print(f"[red][ERROR] Error en configuración: {e}[/red]")
            deps_ok = False
        
        # Verificar agentes
        console.print("\n[bold cyan]🤖 Verificando agentes...[/bold cyan]")
        try:
            # Test básico de importación de agentes
            from genesis_engine.agents.architect import ArchitectAgent
            from genesis_engine.agents.backend import BackendAgent
            from genesis_engine.agents.frontend import FrontendAgent
            
            console.print("[green][PASS] Agentes disponibles[/green]")
        except Exception as e:
            console.print(f"[red][ERROR] Error cargando agentes: {e}[/red]")
            deps_ok = False
        
        # Resultado final
        if deps_ok:
            console.print(f"\n[bold green][SUCCESS] Sistema OK - Listo para usar Genesis Engine[/bold green]")
            console.print("[green][INFO] Ejecuta 'genesis init <nombre>' para crear un proyecto[/green]")
        else:
            console.print(f"\n[bold red][ERROR] Sistema no está listo[/bold red]")
            console.print("[red][FIX] Instala las dependencias faltantes y vuelve a ejecutar[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en doctor: {e}", exc_info=True)
        console.print(f"[red][ERROR] Error inesperado: {e}[/red]")
        raise typer.Exit(1)

@app.command("deploy")
def deploy(
    ctx: typer.Context,
    environment: str = typer.Option(
        "local",
        "--env",
        "-e",
        help="Entorno de despliegue (local, staging, production)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Forzar despliegue sin confirmación"
    ),
    auto_migrate: bool = typer.Option(
        True,
        "--auto-migrate/--no-migrate",
        help="Ejecutar migraciones automáticamente"
    )
):
    """
    [INIT] Desplegar aplicación usando el DeployAgent
    
    Ejecuta el proceso de despliegue automático:
    
    • Construye contenedores Docker
    • Ejecuta tests automatizados  
    • Aplica migraciones de BD
    • Despliega en el entorno seleccionado
    • Configura monitoring y logs
    """
    try:
        skip_check = ctx.obj.get("skip_project_check") if ctx.obj else False
        # Verificar que estamos en un proyecto Genesis
        if not skip_check and not Path("genesis.json").exists():
            console.print("[red][ERROR] No estás en un proyecto Genesis[/red]")
            console.print("[yellow][INFO] Ejecuta 'genesis init <nombre>' para crear uno[/yellow]")
            raise typer.Exit(1)
        
        # Validar entorno
        valid_envs = ["local", "staging", "production"]
        if environment not in valid_envs:
            console.print(f"[red][ERROR] Entorno inválido: {environment}[/red]")
            console.print(f"[yellow][INFO] Entornos válidos: {', '.join(valid_envs)}[/yellow]")
            raise typer.Exit(1)
        
        console.print(f"[bold blue][INIT] Desplegando en entorno: {environment}[/bold blue]")
        
        # Confirmación para production
        if environment == "production" and not force:
            if not Confirm.ask("[yellow][WARN] ¿Confirmas despliegue en producción?[/yellow]"):
                console.print("[yellow]Despliegue cancelado[/yellow]")
                raise typer.Exit(0)
        
        # Ejecutar despliegue
        config = {
            "environment": environment,
            "force": force,
            "auto_migrate": auto_migrate
        }
        
        result = asyncio.run(_deploy_async(config))
        
        if result.get("success"):
            console.print(f"[bold green][PASS] Despliegue exitoso en {environment}[/bold green]")
            if result.get("url"):
                console.print(f"[green]🌐 URL: {result['url']}[/green]")
        else:
            console.print(f"[red][ERROR] Error en despliegue: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en deploy: {e}", exc_info=True)
        console.print(f"[red][ERROR] Error inesperado: {e}[/red]")
        raise typer.Exit(1)

async def _deploy_async(config: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar despliegue de forma asíncrona"""
    orchestrator = GenesisOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Crear tarea de despliegue
        from genesis_engine.tasking import AgentTask
        task = AgentTask(
            id="deploy_task",
            name="deploy_application",
            params=config
        )
        
        # Ejecutar con el deploy agent
        response = await orchestrator.mcp.send_request(
            sender_id="cli",
            target_id="deploy_agent",
            action="deploy",
            data=config
        )
        
        if response.success:
            return {"success": True, "result": response.result}
        else:
            return {"success": False, "error": response.error_message}
            
    except Exception as e:
        logger.error(f"Error en deploy async: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
    finally:
        try:
            await orchestrator.shutdown()
        except Exception as e:
            logger.warning(f"Error cerrando orquestador: {e}")

@app.command("generate")
def generate(
    ctx: typer.Context,
    component: str = typer.Argument(
        help="Tipo de componente a generar (model, endpoint, page, component)"
    ),
    name: str = typer.Argument(
        help="Nombre del componente"
    ),
    agent: Optional[str] = typer.Option(
        None,
        "--agent",
        "-a",
        help="Agente específico a usar (backend, frontend, devops)"
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Modo interactivo para configuración"
    )
):
    """
    [FAST] Generar componentes específicos usando agentes IA
    
    Genera componentes individuales de la aplicación:
    
    • Modelos de datos (SQLAlchemy, Prisma)
    • Endpoints API (FastAPI, Express)
    • Páginas y componentes frontend
    • Tests automatizados
    • Documentación
    """
    try:
        skip_check = ctx.obj.get("skip_project_check") if ctx.obj else False
        # Verificar que estamos en un proyecto Genesis
        if not skip_check and not Path("genesis.json").exists():
            console.print("[red][ERROR] No estás en un proyecto Genesis[/red]")
            console.print("[yellow][INFO] Ejecuta 'genesis init <nombre>' para crear uno[/yellow]")
            raise typer.Exit(1)
        
        # Validar tipo de componente
        valid_components = ["model", "endpoint", "page", "component", "test"]
        if component not in valid_components:
            console.print(f"[red][ERROR] Tipo de componente inválido: {component}[/red]")
            console.print(f"[yellow][INFO] Tipos válidos: {', '.join(valid_components)}[/yellow]")
            raise typer.Exit(1)
        
        # Validar nombre
        if not validate_project_name(name):
            raise typer.Exit(1)
        
        console.print(f"[bold blue][FAST] Generando {component}: {name}[/bold blue]")
        
        # Configurar generación
        config = {
            "component": component,
            "name": name,
            "agent": agent,
            "interactive": interactive
        }
        
        # Ejecutar generación
        result = asyncio.run(_generate_async(config))
        
        if result.get("success"):
            console.print(f"[bold green][PASS] {component.capitalize()} '{name}' generado exitosamente[/bold green]")
            if result.get("files"):
                console.print(f"[green]📄 Archivos creados: {len(result['files'])}[/green]")
                for file in result["files"]:
                    console.print(f"  • {file}")
        else:
            console.print(f"[red][ERROR] Error generando {component}: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en generate: {e}", exc_info=True)
        console.print(f"[red][ERROR] Error inesperado: {e}[/red]")
        raise typer.Exit(1)

async def _generate_async(config: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar generación de forma asíncrona"""
    orchestrator = GenesisOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Determinar agente apropiado
        agent_map = {
            "model": "backend_agent",
            "endpoint": "backend_agent", 
            "page": "frontend_agent",
            "component": "frontend_agent",
            "test": "backend_agent"
        }
        
        target_agent = config.get("agent") or agent_map.get(config["component"], "backend_agent")
        
        # Ejecutar generación
        response = await orchestrator.mcp.send_request(
            sender_id="cli",
            target_id=target_agent,
            action="generate_component",
            data=config
        )
        
        if response.success:
            return {"success": True, "result": response.result}
        else:
            return {"success": False, "error": response.error_message}
            
    except Exception as e:
        logger.error(f"Error en generate async: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
    finally:
        try:
            await orchestrator.shutdown()
        except Exception as e:
            logger.warning(f"Error cerrando orquestador: {e}")

@app.command("status")
def status(ctx: typer.Context):
    """
    [STATS] Mostrar estado del proyecto actual
    """
    try:
        console.print("[bold blue][STATS] Estado del Proyecto Genesis[/bold blue]")
        
        # Verificar si estamos en un proyecto Genesis
        project_file = Path("genesis.json")
        skip_check = ctx.obj.get("skip_project_check") if ctx.obj else False
        if not skip_check and not project_file.exists():
            console.print("[red][ERROR] No estás en un proyecto Genesis[/red]")
            console.print("[yellow][INFO] Ejecuta 'genesis init <nombre>' para crear uno[/yellow]")
            raise typer.Exit(1)
        
        # Leer metadata del proyecto
        try:
            with open(project_file, 'r') as f:
                metadata = json.load(f)
            
            console.print("[green][PASS] Proyecto Genesis detectado[/green]")
            
            # Mostrar información del proyecto
            table = Table(title="Información del Proyecto")
            table.add_column("Propiedad", style="cyan")
            table.add_column("Valor", style="green")
            
            table.add_row("Nombre", metadata.get("name", "N/A"))
            table.add_row("Versión Genesis", metadata.get("version", "N/A"))
            table.add_row("Generado en", metadata.get("generated_at", "N/A"))
            table.add_row("Archivos generados", str(len(metadata.get("generated_files", []))))
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red][ERROR] Error leyendo metadata: {e}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en status: {e}", exc_info=True)
        console.print(f"[red][ERROR] Error inesperado: {e}[/red]")
        raise typer.Exit(1)

@app.command("agents")
def agents(
    list_agents: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Listar todos los agentes disponibles"
    ),
    agent_info: Optional[str] = typer.Option(
        None,
        "--info",
        "-i",
        help="Información detallada de un agente específico"
    )
):
    """
    🤖 Gestionar agentes IA especializados
    
    Consulta información sobre los agentes disponibles:
    
    • ArchitectAgent: Diseño de arquitectura
    • BackendAgent: Generación de backend
    • FrontendAgent: Desarrollo frontend
    • DevOpsAgent: CI/CD y contenedores
    • DeployAgent: Despliegue automático
    • PerformanceAgent: Optimización
    • AIReadyAgent: Integración IA/LLMs
    """
    try:
        if list_agents:
            console.print("[bold cyan]🤖 Agentes Disponibles:[/bold cyan]")
            
            agents_info = [
                ("ArchitectAgent", "[BUILD]", "Diseño de arquitectura y esquemas"),
                ("BackendAgent", "⚙️", "Generación de APIs y servicios"),
                ("FrontendAgent", "[UI]", "Interfaces y experiencia usuario"),
                ("DevOpsAgent", "[DOCKER]", "CI/CD, Docker y automatización"),
                ("DeployAgent", "[INIT]", "Despliegue y configuración"),
                ("PerformanceAgent", "[FAST]", "Optimización y rendimiento"),
                ("AIReadyAgent", "🧠", "Integración IA y LLMs")
            ]
            
            table = Table(title="Agentes Especializados")
            table.add_column("Agente", style="cyan")
            table.add_column("Icono", style="yellow")
            table.add_column("Descripción", style="green")
            
            for name, icon, description in agents_info:
                table.add_row(name, icon, description)
            
            console.print(table)
            
        elif agent_info:
            console.print(f"[bold cyan][LIST] Información del agente: {agent_info}[/bold cyan]")
            
            # Información detallada de agentes
            agent_details = {
                "architect": {
                    "nombre": "ArchitectAgent",
                    "version": "1.0.0",
                    "descripcion": "Agente especializado en diseño de arquitectura y análisis de requisitos",
                    "capacidades": ["analyze_requirements", "design_architecture", "generate_schema"],
                    "dependencias": ["jinja2", "pydantic"]
                },
                "backend": {
                    "nombre": "BackendAgent", 
                    "version": "1.0.0",
                    "descripcion": "Agente para generación de APIs y servicios backend",
                    "capacidades": ["generate_api", "create_models", "setup_database"],
                    "dependencias": ["fastapi", "sqlalchemy", "alembic"]
                }
            }
            
            details = agent_details.get(agent_info.lower())
            if details:
                table = Table(title=f"Detalles de {details['nombre']}")
                table.add_column("Propiedad", style="cyan")
                table.add_column("Valor", style="green")
                
                table.add_row("Nombre", details["nombre"])
                table.add_row("Versión", details["version"])
                table.add_row("Descripción", details["descripcion"])
                table.add_row("Capacidades", ", ".join(details["capacidades"]))
                table.add_row("Dependencias", ", ".join(details["dependencias"]))
                
                console.print(table)
            else:
                console.print(f"[red][ERROR] Agente no encontrado: {agent_info}[/red]")
                console.print("[yellow][INFO] Usa --list para ver agentes disponibles[/yellow]")
                
        else:
            console.print("[yellow][INFO] Usa --list para ver agentes disponibles[/yellow]")
            console.print("[yellow][INFO] Usa --info <agente> para información detallada[/yellow]")
            
    except Exception as e:
        logger.error(f"Error en agents: {e}", exc_info=True)
        console.print(f"[red][ERROR] Error inesperado: {e}[/red]")
        raise typer.Exit(1)

@app.command("help")
def help_cmd():
    """Mostrar la ayuda completa de la CLI"""
    show_banner()
    command = get_command(app)
    ctx = typer.Context(command)
    console.print(command.get_help(ctx))

# Punto de entrada principal
def main_entry():
    """Entry point principal para el script de consola"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow][WARN] Operación cancelada por el usuario[/yellow]")
        sys.exit(1)
    except GenesisException as e:
        console.print(f"[red][ERROR] Error de Genesis: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado en main: {e}", exc_info=True)
        console.print(f"[red][ERROR] Error inesperado: {e}[/red]")
        sys.exit(1)

# Para compatibilidad con python -m
if __name__ == "__main__":    main_entry()