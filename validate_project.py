#!/usr/bin/env python3
"""
Script de validación para proyectos Genesis
"""

import sys
from pathlib import Path

def validate_project_structure(project_path: Path) -> Dict[str, bool]:
    """Validar estructura del proyecto"""
    checks = {
        "backend_dir": (project_path / "backend").exists(),
        "frontend_dir": (project_path / "frontend").exists(),
        "backend_dockerfile": (project_path / "backend" / "Dockerfile").exists(),
        "frontend_dockerfile": (project_path / "frontend" / "Dockerfile").exists(),
        "docker_compose": (project_path / "docker-compose.yml").exists(),
        "requirements": (project_path / "backend" / "requirements.txt").exists(),
        "package_json": (project_path / "frontend" / "package.json").exists(),
    }
    
    return checks

def main():
    if len(sys.argv) != 2:
        print("Uso: python validate_project.py <project_path>")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    if not project_path.exists():
        print(f"Proyecto no encontrado: {project_path}")
        sys.exit(1)
    
    print(f"Validando proyecto: {project_path}")
    print("=" * 40)
    
    checks = validate_project_structure(project_path)
    all_good = True
    
    for check, passed in checks.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {check}")
        if not passed:
            all_good = False
    
    print("=" * 40)
    if all_good:
        print("[PASS] Proyecto válido!")
        print("\nSiguientes pasos:")
        print("1. cd", project_path.name)
        print("2. docker-compose up -d")
        print("3. Abrir http://localhost:3000")
    else:
        print("[FAIL] Proyecto tiene problemas")
        print("\nEjecutar: python fix_remaining_issues.py")
    
    sys.exit(0 if all_good else 1)

if __name__ == "__main__":
    main()
