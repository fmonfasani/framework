#!/usr/bin/env python3
"""
Genesis Engine CLI - Entry Point Principal
"""

import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Importar comandos
from genesis_engine.cli.commands.init import init_command
from genesis_engine.cli.commands.doctor import doctor_command
from genesis_engine.cli.commands.deploy import deploy_command
from genesis_engine.cli.commands.generate import generate_command
from genesis_engine.cli.utils import show_banner, check_dependencies
from genesis_engine import __version__

# Configurar Rich Console
console = Console()

# Crear aplicación Typer principal
app = typer.Typer(
    name="genesis",
    help="🚀 Genesis Engine - Sistema operativo para desarrollo full-stack moderno",
    add_completion=False,
    rich_markup_mode="rich"
)

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v",
        help="Mostrar versión de Genesis Engine"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Mostrar información detallada"
    )
):
    """
    🚀 Genesis Engine - Sistema operativo para desarrollo full-stack moderno
    
    Genesis Engine te permite crear, optimizar y desplegar aplicaciones
    completas usando agentes IA especializados que se comunican via MCP.
    """
    if version:
        console.print(f"[bold green]Genesis Engine v{__version__}[/bold green]")
        raise typer.Exit(0)
    
    if verbose:
        show_banner()

@app.command("init")
def init(
    project_name: str = typer.Argument(
        help="Nombre del proyecto a crear"
    ),
    template: str = typer.Option(
        "saas-basic",
        "--template", 
        "-t",
        help="Template a usar (saas-basic, api-rest, web-app)"
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
    )
):
    """
    🎯 Inicializar un nuevo proyecto full-stack
    
    Crea un proyecto completo usando el Golden Path seleccionado.
    Los agentes IA trabajarán en conjunto para generar:
    
    • Backend (FastAPI, Node.js, etc.)
    • Frontend (Next.js, React, Vue, etc.) 
    • DevOps (Docker, CI/CD)
    • Base de datos y migraciones
    • Configuración completa
    """
    init_command(project_name, template, no_interactive, output_dir)

@app.command("doctor") 
def doctor():
    """
    🔍 Diagnosticar el entorno y verificar dependencias
    
    Ejecuta un diagnóstico completo del entorno de desarrollo:
    
    • Verifica instalación de Python, Node.js, Docker
    • Chequea conectividad de red
    • Valida configuración de agentes
    • Ejecuta tests de comunicación MCP
    """
    doctor_command()

@app.command("deploy")
def deploy(
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
    🚀 Desplegar aplicación usando el DeployAgent
    
    Ejecuta el proceso de despliegue automático:
    
    • Construye contenedores Docker
    • Ejecuta tests automatizados  
    • Aplica migraciones de BD
    • Despliega en el entorno seleccionado
    • Configura monitoring y logs
    """
    deploy_command(environment, force, auto_migrate)

@app.command("generate")
def generate(
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
    ⚡ Generar componentes específicos usando agentes IA
    
    Genera componentes individuales de la aplicación:
    
    • Modelos de datos (SQLAlchemy, Prisma)
    • Endpoints API (FastAPI, Express)
    • Páginas y componentes frontend
    • Tests automatizados
    • Documentación
    """
    generate_command(component, name, agent, interactive)

@app.command("status")
def status():
    """
    📊 Mostrar estado del proyecto actual
    """
    console.print("[bold blue]Estado del Proyecto Genesis[/bold blue]")
    
    # Verificar si estamos en un proyecto Genesis
    project_file = Path("genesis.json")
    if not project_file.exists():
        console.print("[red]❌ No estás en un proyecto Genesis[/red]")
        console.print("[yellow]💡 Ejecuta 'genesis init <nombre>' para crear uno[/yellow]")
        raise typer.Exit(1)
    
    console.print("[green]✅ Proyecto Genesis detectado[/green]")
    # TODO: Implementar análisis de estado completo

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
    if list_agents:
        console.print("[bold cyan]🤖 Agentes Disponibles:[/bold cyan]")
        agents_info = [
            ("ArchitectAgent", "🏗️", "Diseño de arquitectura y esquemas"),
            ("BackendAgent", "⚙️", "Generación de APIs y servicios"),
            ("FrontendAgent", "🎨", "Interfaces y experiencia usuario"),
            ("DevOpsAgent", "🐳", "CI/CD, Docker y automatización"),
            ("DeployAgent", "🚀", "Despliegue y configuración"),
            ("PerformanceAgent", "⚡", "Optimización y rendimiento"),
            ("AIReadyAgent", "🧠", "Integración IA y LLMs")
        ]
        
        for name, icon, description in agents_info:
            console.print(f"  {icon} [bold]{name}[/bold]: {description}")
    
    elif agent_info:
        console.print(f"[bold cyan]📋 Información del agente: {agent_info}[/bold cyan]")
        # TODO: Implementar información detallada de agentes
        console.print("[yellow]🚧 Función en desarrollo[/yellow]")
    
    else:
        console.print("[yellow]💡 Usa --list para ver agentes disponibles[/yellow]")

def version_callback(value: bool):
    """Callback para mostrar versión"""
    if value:
        console.print(f"[bold green]Genesis Engine v{__version__}[/bold green]")
        raise typer.Exit(0)

# Punto de entrada principal
def main_entry():
    """Entry point principal para el script de consola"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Operación cancelada por el usuario[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        sys.exit(1)

# Para compatibilidad con python -m
if __name__ == "__main__":
    main_entry()