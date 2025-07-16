"""
Genesis Init Command - Inicializar proyectos
"""

import json
import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, ProjectGenerationRequest
from genesis_engine.templates.engine import TemplateEngine
import sys

# Export real module reference for tests
real_module = sys.modules[__name__]

console = Console()

def init_command(
    project_name: str,
    template: str = "saas-basic",
    no_interactive: bool = False,
    output_dir: Optional[str] = None
):
    """Comando para inicializar un nuevo proyecto Genesis"""
    
    # Banner de inicio
    console.print(Panel.fit(
        "[bold cyan]🚀 Genesis Engine - Inicializando Proyecto[/bold cyan]",
        border_style="cyan"
    ))
    
    # Configurar directorio de salida
    if output_dir:
        base_dir = Path(output_dir)
    else:
        base_dir = Path.cwd()
    
    project_dir = base_dir / project_name
    
    # Verificar si el directorio ya existe
    if project_dir.exists():
        if not no_interactive:
            overwrite = Confirm.ask(
                f"[yellow]⚠️ El directorio '{project_name}' ya existe. ¿Sobrescribir?[/yellow]"
            )
            if not overwrite:
                console.print("[red]❌ Operación cancelada[/red]")
                return
        else:
            console.print(f"[red]❌ El directorio '{project_name}' ya existe[/red]")
            return
    
    # Configuración del proyecto
    project_config = {
        "name": project_name,
        "template": template,
        "version": "1.0.0",
        "description": f"Aplicación {template} generada con Genesis Engine"
    }

    if template == "saas-basic" and no_interactive:
        project_config["backend"] = {
            "framework": "fastapi",
            "database": "postgresql"
        }
        project_config["frontend"] = {
            "framework": "nextjs",
            "styling": "tailwind"
        }
    
    if not no_interactive:
        console.print("\n[bold]📋 Configuración del Proyecto[/bold]")
        
        project_config["description"] = Prompt.ask(
            "Descripción del proyecto",
            default=project_config["description"]
        )
        
        # Configuraciones específicas por template
        if template == "saas-basic":
            project_config["backend"] = {
                "framework": Prompt.ask(
                    "Framework backend",
                    choices=["fastapi", "nestjs", "django"],
                    default="fastapi"
                ),
                "database": Prompt.ask(
                    "Base de datos",
                    choices=["postgresql", "mysql", "sqlite"],
                    default="postgresql"
                )
            }
            
            project_config["frontend"] = {
                "framework": Prompt.ask(
                    "Framework frontend", 
                    choices=["nextjs", "react", "vue"],
                    default="nextjs"
                ),
                "styling": Prompt.ask(
                    "Sistema de estilos",
                    choices=["tailwind", "styled-components", "css-modules"],
                    default="tailwind"
                )
            }
    
    # Inicializar orquestador y motores
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Tarea 1: Inicializar agentes
        task1 = progress.add_task("🤖 Inicializando agentes IA...", total=1)
        orchestrator = CoreOrchestrator()
        template_engine = TemplateEngine()
        progress.update(task1, completed=1)

        # Tarea 2: Generar arquitectura
        task2 = progress.add_task("🏗️ Generando arquitectura del proyecto...", total=1)

        request = ProjectGenerationRequest(
            name=project_name,
            template=template,
            options=project_config,
        )
        architect_result = asyncio.run(orchestrator.execute_project_generation(request))

        progress.update(task2, completed=1)
        
        # Tarea 3: Generar código
        task3 = progress.add_task("⚡ Generando código fuente...", total=1)
        
        # Crear directorio del proyecto
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Preparar contexto para las plantillas
        context = {
            **project_config,
            "project_name": project_config.get("name"),
            "backend_framework": project_config.get("backend", {}).get("framework", "fastapi"),
            "frontend_framework": project_config.get("frontend", {}).get("framework", "nextjs"),
            "database_type": project_config.get("backend", {}).get("database", "postgresql"),
        }

        # Generar archivos usando template engine
        template_engine.generate_project(
            template_name=template,
            output_dir=project_dir,
            context=context,
        )
        
        progress.update(task3, completed=1)
        
        # Tarea 4: Configurar DevOps
        task4 = progress.add_task("🐳 Configurando DevOps...", total=1)
        
        devops_result = architect_result
        
        progress.update(task4, completed=1)
        
        # Tarea 5: Guardar configuración
        task5 = progress.add_task("💾 Guardando configuración...", total=1)
        
        # Guardar genesis.json
        genesis_config_file = project_dir / "genesis.json"
        with open(genesis_config_file, 'w', encoding='utf-8') as f:
            json.dump(project_config, f, indent=2, ensure_ascii=False)
        
        progress.update(task5, completed=1)
    
    # Mensaje de éxito
    console.print(f"\n[bold green]✅ ¡Proyecto '{project_name}' creado exitosamente![/bold green]")
    console.print(f"[cyan]📁 Ubicación: {project_dir}[/cyan]")
    
    # Instrucciones siguientes
    console.print(Panel(
        f"""[bold]🚀 Próximos pasos:[/bold]

1. [cyan]cd {project_name}[/cyan]
2. [cyan]genesis doctor[/cyan] - Verificar entorno
3. [cyan]genesis deploy --env local[/cyan] - Desplegar localmente

[bold]📋 Comandos útiles:[/bold]
• [green]genesis status[/green] - Ver estado del proyecto
• [green]genesis generate model User[/green] - Generar componentes
• [green]genesis agents --list[/green] - Ver agentes disponibles""",
        title="[bold green]Proyecto Listo[/bold green]",
        border_style="green"
    ))