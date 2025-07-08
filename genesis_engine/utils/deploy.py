from typing import Any, Dict, List
from subprocess import TimeoutExpired
import subprocess


def run_system_command(command: List[str], timeout: int = 30) -> Dict[str, Any]:
    """Ejecutar comando de sistema de manera segura"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout} seconds"}
    except Exception as e:  # pragma: no cover - unforeseen errors
        return {"success": False, "error": str(e)}


def check_docker_available() -> bool:
    """Verificar si Docker está disponible"""
    result = run_system_command(["docker", "--version"], timeout=5)
    return result.get("success", False)


def check_kubernetes_available() -> bool:
    """Verificar si kubectl está disponible"""
    result = run_system_command(["kubectl", "version", "--client"], timeout=5)
    return result.get("success", False)
