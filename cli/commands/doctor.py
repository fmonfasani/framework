"""
Genesis Doctor Command - Diagnóstico del entorno
"""

import sys
import subprocess
import platform
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

def doctor_command():
    """Comando para diagnosticar el entorno de desarrollo"""
    
    console.print(Panel.fit(
        "[bold cyan]🔍 Genesis Engine - Diagnóstico del Entorno[/bold cyan]",
        border_style="cyan"
    ))
    
    # Crear tabla de resultados
    table = Table(title="📋 Diagnóstico del Sistema")
    table.add_column("Componente", style="cyan", no_wrap=True)
    table.add_column("Estado", style="magenta")
    table.add_column("Versión", style="green")
    table.add_column("Notas", style="yellow")
    
    checks = []
    
    # 1. Verificar Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_status = "✅ OK" if sys.version_info >= (3, 8) else "❌ Muy antiguo"
    checks.append(("Python", python_status, python_version, "Mínimo requerido: 3.8+"))
    
    # 2. Verificar pip
    try:
        pip_result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
        if pip_result.returncode == 0:
            pip_version = pip_result.stdout.split()[1]
            checks.append(("pip", "✅ OK", pip_version, ""))
        else:
            checks.append(("pip", "❌ Error", "N/A", "No se puede ejecutar pip"))
    except Exception:
        checks.append(("pip", "❌ Error", "N/A", "No encontrado"))
    
    # 3. Verificar Node.js
    try:
        node_result = subprocess.run(["node", "--version"], 
                                   capture_output=True, text=True)
        if node_result.returncode == 0:
            node_version = node_result.stdout.strip()
            checks.append(("Node.js", "✅ OK", node_version, "Para proyectos frontend"))
        else:
            checks.append(("Node.js", "❌ Error", "N/A", "Requerido para frontend"))
    except FileNotFoundError:
        checks.append(("Node.js", "⚠️ No encontrado", "N/A", "Opcional para algunos templates"))
    
    # 4. Verificar Docker
    try:
        docker_result = subprocess.run(["docker", "--version"], 
                                     capture_output=True, text=True)
        if docker_result.returncode == 0:
            docker_version = docker_result.stdout.split()[2].rstrip(',')
            checks.append(("Docker", "✅ OK", docker_version, "Para despliegue"))
        else:
            checks.append(("Docker", "❌ Error", "N/A", "Requerido para deploy"))
    except FileNotFoundError:
        checks.append(("Docker", "⚠️ No encontrado", "N/A", "Necesario para contenedores"))
    
    # 5. Verificar Git
    try:
        git_result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True)
        if git_result.returncode == 0:
            git_version = git_result.stdout.split()[2]
            checks.append(("Git", "✅ OK", git_version, "Control de versiones"))
        else:
            checks.append(("Git", "❌ Error", "N/A", "Requerido"))
    except FileNotFoundError:
        checks.append(("Git", "❌ No encontrado", "N/A", "Instalar Git"))
    
    # 6. Verificar Genesis Engine
    try:
        import genesis_engine
        checks.append(("Genesis Engine", "✅ OK", genesis_engine.__version__, "¡Funcionando!"))
    except ImportError:
        checks.append(("Genesis Engine", "❌ Error", "N/A", "Problema de instalación"))
    
    # Agregar resultados a la tabla
    for check in checks:
        table.add_row(*check)
    
    console.print(table)
    
    # Verificar conectividad (opcional)
    console.print("\n[bold]🌐 Verificando Conectividad[/bold]")
    
    try:
        import requests
        response = requests.get("https://api.github.com", timeout=5)
        if response.status_code == 200:
            rprint("[green]✅ Conectividad a GitHub: OK[/green]")
        else:
            rprint("[yellow]⚠️ Conectividad a GitHub: Limitada[/yellow]")
    except Exception:
        rprint("[red]❌ Conectividad a GitHub: Sin conexión[/red]")
    
    # Información del sistema
    console.print(f"\n[bold]💻 Sistema Operativo:[/bold] {platform.system()} {platform.release()}")
    console.print(f"[bold]🏗️ Arquitectura:[/bold] {platform.machine()}")
    
    # Verificar proyecto actual
    console.print("\n[bold]📁 Proyecto Actual[/bold]")
    genesis_file = Path("genesis.json")
    if genesis_file.exists():
        rprint("[green]✅ Proyecto Genesis detectado[/green]")
        try:
            import json
            with open(genesis_file) as f:
                config = json.load(f)
            console.print(f"[cyan]📋 Nombre: {config.get('name', 'N/A')}[/cyan]")
            console.print(f"[cyan]🎯 Template: {config.get('template', 'N/A')}[/cyan]")
        except Exception:
            rprint("[yellow]⚠️ Archivo genesis.json corrupto[/yellow]")
    else:
        rprint("[yellow]ℹ️ No estás en un proyecto Genesis[/yellow]")
    
    # Resumen final
    errors = [check for check in checks if "❌" in check[1]]
    warnings = [check for check in checks if "⚠️" in check[1]]
    
    if errors:
        console.print(f"\n[bold red]❌ {len(errors)} errores encontrados[/bold red]")
        for error in errors:
            console.print(f"  • {error[0]}: {error[3]}")
    
    if warnings:
        console.print(f"\n[bold yellow]⚠️ {len(warnings)} advertencias[/bold yellow]")
        for warning in warnings:
            console.print(f"  • {warning[0]}: {warning[3]}")
    
    if not errors and not warnings:
        console.print("\n[bold green]🎉 ¡Todo está configurado correctamente![/bold green]")
    
    return len(errors) == 0