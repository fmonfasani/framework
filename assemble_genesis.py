#!/usr/bin/env python3
"""
Script de ensamblaje automático para Genesis Engine
Copia todos los artefactos a sus ubicaciones correctas
"""

import os
import shutil
from pathlib import Path
import argparse

# Mapeo completo de artefactos a archivos
ARTIFACT_MAPPING = {
    # Archivos principales
    "genesis_main_readme": "README.md",
    "genesis_init_file": "genesis_engine/__init__.py",
    "genesis_config_core": "genesis_engine/core/config.py",
    
    # CLI
    "genesis_cli_main": "genesis_engine/cli/main.py", 
    "genesis_cli_commands": "genesis_engine/cli/commands/create.py",
    
    # MCP y Agentes
    "genesis_mcp_protocol": "genesis_engine/mcp/protocol.py",
    "genesis_agent_base": "genesis_engine/mcp/agent_base.py",
    "genesis_architect_agent": "genesis_engine/agents/architect.py",
    "genesis_backend_agent": "genesis_engine/agents/backend.py",
    "genesis_frontend_agent": "genesis_engine/agents/frontend.py",
    "genesis_devops_agent": "genesis_engine/agents/devops.py",
    "genesis_deploy_agent": "genesis_engine/agents/deploy.py",
    "genesis_performance_agent": "genesis_engine/agents/performance.py",
    "genesis_ai_ready_agent": "genesis_engine/agents/ai_ready.py",
    
    # Core
    "genesis_orchestrator": "genesis_core/orchestrator/core_orchestrator.py",
    "genesis_project_manager": "genesis_engine/core/project_manager.py",
    "genesis_template_engine": "genesis_templates/engine.py",

    # Golden Path
    "genesis_golden_path": "genesis_templates/golden_path/saas_basic.py",
    
    # Utilidades
    "genesis_validation_utils": "genesis_engine/utils/validation.py",
    
    # Ejemplos
    "genesis_example_demo": "examples/demo_complete.py",
}

def copy_artifacts(artifact_dir: str) -> None:
    """Copiar artefactos generados a su ubicación destino."""
    base = Path(artifact_dir)
    for name, destination in ARTIFACT_MAPPING.items():
        dest_path = Path(destination)
        src_path = base / f"{name}{dest_path.suffix}"
        if src_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            print(f"📄 Copiado {src_path} -> {dest_path}")
        else:
            print(f"⚠️  Artefacto no encontrado: {src_path}")

def create_file_from_artifact(artifact_content, file_path):
    """Crear archivo desde contenido de artefacto"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(artifact_content)
    
    print(f"✅ Creado: {file_path}")

def create_init_files():
    """Crear archivos __init__.py necesarios"""
    init_files = [
        "genesis_engine/__init__.py",  # Ya se crea desde artefacto
        "genesis_engine/cli/__init__.py",
        "genesis_engine/cli/commands/__init__.py", 
        "genesis_engine/cli/ui/__init__.py",
        "genesis_engine/core/__init__.py",
        "genesis_engine/mcp/__init__.py",
        "genesis_engine/agents/__init__.py",
        "genesis_templates/__init__.py",
        "genesis_templates/golden_path/__init__.py",
        "genesis_engine/utils/__init__.py",
    ]
    
    for init_file in init_files:
        if not Path(init_file).exists():
            Path(init_file).parent.mkdir(parents=True, exist_ok=True)
            Path(init_file).write_text('"""Genesis Engine module"""')
            print(f"📝 Creado: {init_file}")

def create_requirements_txt():
    """Crear requirements.txt"""
    requirements = """typer[all]==0.9.0
rich==13.7.0
jinja2==3.1.2
pydantic==2.5.0
click==8.1.7
GitPython==3.1.40
docker==6.1.3
kubernetes==28.1.0
fastapi>=0.115.14
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
isort==5.12.0
mypy==1.7.1
"""
    
    with open("requirements.txt", 'w') as f:
        f.write(requirements.strip())
    print("✅ Creado: requirements.txt")

def create_pyproject_toml():
    """Crear pyproject.toml"""
    pyproject = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "genesis-engine"
version = "1.0.0"
description = "Sistema operativo completo para desarrollo y despliegue de aplicaciones full-stack"
authors = [{name = "Genesis Team", email = "team@genesis-engine.dev"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.9"

dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.7.0", 
    "jinja2>=3.1.2",
    "pydantic>=2.5.0",
    "click>=8.1.7",
    "GitPython>=3.1.40",
    "docker>=6.1.3",
    "fastapi>=0.115.14",
    "sqlalchemy>=2.0.23",
]

[project.scripts]
genesis = "genesis_engine.cli.main:app"

[tool.setuptools.packages.find]
where = ["."]
include = ["genesis_engine*"]
exclude = ["tests*"]
"""
    
    with open("pyproject.toml", 'w') as f:
        f.write(pyproject.strip())
    print("✅ Creado: pyproject.toml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble Genesis Engine package from artifacts")
    parser.add_argument(
        "--artifacts",
        default="artifacts",
        help="Directorio donde se ubican los artefactos generados",
    )
    return parser.parse_args()


def main() -> None:
    """Función principal"""
    args = parse_args()
    print("🛠️  Ensamblando Genesis Engine...")
    print("=" * 50)

    copy_artifacts(args.artifacts)
    create_init_files()
    create_requirements_txt()
    create_pyproject_toml()

    print("\n✅ Ensamblaje completo. Ejecuta `pip install -e .` para instalar.")

if __name__ == "__main__":
    main()