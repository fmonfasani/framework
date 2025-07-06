"""
Validation Utilities - Utilidades de validación para Genesis Engine

Este módulo proporciona:
- Validación de configuraciones de proyecto
- Validación del entorno de desarrollo
- Validación de dependencias
- Validación de schemas y templates
- Diagnósticos del sistema
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re

class ValidationLevel(str, Enum):
    """Niveles de validación"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

@dataclass
class ValidationResult:
    """Resultado de una validación"""
    name: str
    level: ValidationLevel
    message: str
    suggestion: Optional[str] = None
    passed: bool = True
    
    def __post_init__(self):
        self.passed = self.level in [ValidationLevel.SUCCESS, ValidationLevel.INFO, ValidationLevel.WARNING]

class EnvironmentValidator:
    """
    Validador del entorno de desarrollo
    
    Verifica que el sistema tenga todas las dependencias y
    configuraciones necesarias para ejecutar Genesis Engine.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.results: List[ValidationResult] = []
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar logger"""
        logger = logging.getLogger("genesis.validation")
        logger.setLevel(logging.INFO)
        return logger
    
    def run_diagnostics(self) -> List[ValidationResult]:
        """
        Ejecutar diagnósticos completos del entorno
        
        Returns:
            Lista de resultados de validación
        """
        self.results = []
        
        # Validaciones básicas del sistema
        self._check_python_version()
        self._check_node_version()
        self._check_git_installation()
        self._check_docker_installation()
        
        # Validaciones de dependencias Python
        self._check_python_dependencies()
        
        # Validaciones de herramientas de desarrollo
        self._check_development_tools()
        
        # Validaciones de conectividad
        self._check_internet_connectivity()
        
        # Validaciones de permisos
        self._check_file_permissions()
        
        return self.results
    
    def _check_python_version(self):
        """Verificar versión de Python"""
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            if version.major == 3 and version.minor >= 9:
                self._add_result(
                    "Python Version",
                    ValidationLevel.SUCCESS,
                    f"Python {version_str} ✓"
                )
            elif version.major == 3 and version.minor >= 8:
                self._add_result(
                    "Python Version",
                    ValidationLevel.WARNING,
                    f"Python {version_str} (recomendado >= 3.9)",
                    "Considere actualizar a Python 3.9 o superior"
                )
            else:
                self._add_result(
                    "Python Version",
                    ValidationLevel.ERROR,
                    f"Python {version_str} no compatible",
                    "Instale Python 3.9 o superior"
                )
        except Exception as e:
            self._add_result(
                "Python Version",
                ValidationLevel.ERROR,
                f"Error verificando Python: {e}"
            )
    
    def _check_node_version(self):
        """Verificar versión de Node.js"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Extraer número de versión
                version_match = re.match(r'v(\d+)\.(\d+)\.(\d+)', version_str)
                if version_match:
                    major = int(version_match.group(1))
                    if major >= 18:
                        self._add_result(
                            "Node.js Version",
                            ValidationLevel.SUCCESS,
                            f"Node.js {version_str} ✓"
                        )
                    elif major >= 16:
                        self._add_result(
                            "Node.js Version",
                            ValidationLevel.WARNING,
                            f"Node.js {version_str} (recomendado >= 18)",
                            "Considere actualizar a Node.js 18 LTS o superior"
                        )
                    else:
                        self._add_result(
                            "Node.js Version",
                            ValidationLevel.ERROR,
                            f"Node.js {version_str} no compatible",
                            "Instale Node.js 18 LTS o superior"
                        )
                else:
                    self._add_result(
                        "Node.js Version",
                        ValidationLevel.WARNING,
                        f"Versión de Node.js no reconocida: {version_str}"
                    )
            else:
                self._add_result(
                    "Node.js Installation",
                    ValidationLevel.ERROR,
                    "Node.js no está instalado",
                    "Instale Node.js desde https://nodejs.org"
                )
        except FileNotFoundError:
            self._add_result(
                "Node.js Installation",
                ValidationLevel.ERROR,
                "Node.js no encontrado en PATH",
                "Instale Node.js y asegúrese de que esté en PATH"
            )
        except subprocess.TimeoutExpired:
            self._add_result(
                "Node.js Version",
                ValidationLevel.WARNING,
                "Timeout verificando versión de Node.js"
            )
        except Exception as e:
            self._add_result(
                "Node.js Version",
                ValidationLevel.ERROR,
                f"Error verificando Node.js: {e}"
            )
    
    def _check_git_installation(self):
        """Verificar instalación de Git"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_str = result.stdout.strip()
                self._add_result(
                    "Git Installation",
                    ValidationLevel.SUCCESS,
                    f"{version_str} ✓"
                )
            else:
                self._add_result(
                    "Git Installation",
                    ValidationLevel.ERROR,
                    "Git no está funcionando correctamente",
                    "Reinstale Git"
                )
        except FileNotFoundError:
            self._add_result(
                "Git Installation",
                ValidationLevel.ERROR,
                "Git no está instalado",
                "Instale Git desde https://git-scm.com"
            )
        except Exception as e:
            self._add_result(
                "Git Installation",
                ValidationLevel.ERROR,
                f"Error verificando Git: {e}"
            )
    
    def _check_docker_installation(self):
        """Verificar instalación de Docker"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_str = result.stdout.strip()
                self._add_result(
                    "Docker Installation",
                    ValidationLevel.SUCCESS,
                    f"{version_str} ✓"
                )
                
                # Verificar que Docker esté corriendo
                self._check_docker_daemon()
            else:
                self._add_result(
                    "Docker Installation",
                    ValidationLevel.WARNING,
                    "Docker no está funcionando",
                    "Docker es opcional pero recomendado para desarrollo"
                )
        except FileNotFoundError:
            self._add_result(
                "Docker Installation",
                ValidationLevel.WARNING,
                "Docker no está instalado",
                "Docker es opcional pero recomendado. Instale desde https://docker.com"
            )
        except Exception as e:
            self._add_result(
                "Docker Installation",
                ValidationLevel.WARNING,
                f"Error verificando Docker: {e}"
            )
    
    def _check_docker_daemon(self):
        """Verificar que el daemon de Docker esté corriendo"""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self._add_result(
                    "Docker Daemon",
                    ValidationLevel.SUCCESS,
                    "Docker daemon corriendo ✓"
                )
            else:
                self._add_result(
                    "Docker Daemon",
                    ValidationLevel.WARNING,
                    "Docker daemon no está corriendo",
                    "Inicie Docker Desktop o el servicio Docker"
                )
        except Exception as e:
            self._add_result(
                "Docker Daemon",
                ValidationLevel.WARNING,
                f"Error verificando Docker daemon: {e}"
            )
    
    def _check_python_dependencies(self):
        """Verificar dependencias Python críticas"""
        critical_packages = [
            ("typer", "0.9.0"),
            ("rich", "13.0.0"),
            ("jinja2", "3.0.0"),
            ("pydantic", "2.0.0"),
            ("fastapi", "0.100.0")
        ]
        
        for package, min_version in critical_packages:
            self._check_python_package(package, min_version)
    
    def _check_python_package(self, package: str, min_version: str):
        """Verificar un paquete Python específico"""
        try:
            import importlib.metadata
            
            try:
                version = importlib.metadata.version(package)
                self._add_result(
                    f"Python Package: {package}",
                    ValidationLevel.SUCCESS,
                    f"{package} {version} ✓"
                )
            except importlib.metadata.PackageNotFoundError:
                self._add_result(
                    f"Python Package: {package}",
                    ValidationLevel.WARNING,
                    f"{package} no está instalado",
                    f"Instale con: pip install {package}>={min_version}"
                )
        except Exception as e:
            self._add_result(
                f"Python Package: {package}",
                ValidationLevel.ERROR,
                f"Error verificando {package}: {e}"
            )
    
    def _check_development_tools(self):
        """Verificar herramientas de desarrollo"""
        tools = {
            "npm": "npm --version",
            "yarn": "yarn --version", 
            "pnpm": "pnpm --version"
        }
        
        package_manager_found = False
        
        for tool, command in tools.items():
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self._add_result(
                        f"{tool.upper()} Package Manager",
                        ValidationLevel.SUCCESS,
                        f"{tool} {version} ✓"
                    )
                    package_manager_found = True
                    break  # Solo necesitamos uno
            except:
                continue
        
        if not package_manager_found:
            self._add_result(
                "Package Manager",
                ValidationLevel.WARNING,
                "No se encontró npm, yarn o pnpm",
                "npm se instala con Node.js"
            )
    
    def _check_internet_connectivity(self):
        """Verificar conectividad a internet"""
        try:
            import urllib.request
            
            # Verificar conexión a PyPI
            try:
                urllib.request.urlopen('https://pypi.org', timeout=10)
                self._add_result(
                    "PyPI Connectivity",
                    ValidationLevel.SUCCESS,
                    "Conexión a PyPI ✓"
                )
            except:
                self._add_result(
                    "PyPI Connectivity",
                    ValidationLevel.WARNING,
                    "No se puede conectar a PyPI",
                    "Verifique su conexión a internet"
                )
            
            # Verificar conexión a npm registry
            try:
                urllib.request.urlopen('https://registry.npmjs.org', timeout=10)
                self._add_result(
                    "NPM Registry Connectivity",
                    ValidationLevel.SUCCESS,
                    "Conexión a npm registry ✓"
                )
            except:
                self._add_result(
                    "NPM Registry Connectivity",
                    ValidationLevel.WARNING,
                    "No se puede conectar al npm registry"
                )
                
        except Exception as e:
            self._add_result(
                "Internet Connectivity",
                ValidationLevel.ERROR,
                f"Error verificando conectividad: {e}"
            )
    
    def _check_file_permissions(self):
        """Verificar permisos de archivos"""
        try:
            # Verificar permisos de escritura en el directorio actual
            current_dir = Path.cwd()
            test_file = current_dir / ".genesis_test_write"
            
            try:
                test_file.write_text("test")
                test_file.unlink()
                
                self._add_result(
                    "Write Permissions",
                    ValidationLevel.SUCCESS,
                    "Permisos de escritura en directorio actual ✓"
                )
            except PermissionError:
                self._add_result(
                    "Write Permissions",
                    ValidationLevel.ERROR,
                    "No hay permisos de escritura en el directorio actual",
                    "Ejecute desde un directorio con permisos de escritura"
                )
            except Exception as e:
                self._add_result(
                    "Write Permissions",
                    ValidationLevel.WARNING,
                    f"Error verificando permisos: {e}"
                )
                
        except Exception as e:
            self._add_result(
                "File Permissions",
                ValidationLevel.ERROR,
                f"Error verificando permisos de archivos: {e}"
            )
    
    def _add_result(
        self,
        name: str,
        level: ValidationLevel,
        message: str,
        suggestion: Optional[str] = None
    ):
        """Agregar resultado de validación"""
        result = ValidationResult(
            name=name,
            level=level,
            message=message,
            suggestion=suggestion
        )
        self.results.append(result)
        
        # Log según el nivel
        if level == ValidationLevel.ERROR:
            self.logger.error(f"{name}: {message}")
        elif level == ValidationLevel.WARNING:
            self.logger.warning(f"{name}: {message}")
        elif level == ValidationLevel.SUCCESS:
            self.logger.info(f"{name}: {message}")

class ConfigValidator:
    """
    Validador de configuraciones de proyecto
    
    Valida que las configuraciones del proyecto sean válidas
    y consistentes entre sí.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("genesis.config_validator")
    
    def validate_project_config(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validar configuración de proyecto
        
        Args:
            config: Configuración del proyecto
            
        Returns:
            Lista de resultados de validación
        """
        results = []
        
        # Validar campos obligatorios
        required_fields = ["name", "template"]
        for field in required_fields:
            if field not in config:
                results.append(ValidationResult(
                    name=f"Required Field: {field}",
                    level=ValidationLevel.ERROR,
                    message=f"Campo obligatorio faltante: {field}",
                    passed=False
                ))
        
        # Validar nombre del proyecto
        if "name" in config:
            name = config["name"]
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
                results.append(ValidationResult(
                    name="Project Name",
                    level=ValidationLevel.ERROR,
                    message="Nombre del proyecto debe empezar con letra y contener solo letras, números, _ y -",
                    passed=False
                ))
            elif len(name) < 3:
                results.append(ValidationResult(
                    name="Project Name Length",
                    level=ValidationLevel.WARNING,
                    message="Nombre del proyecto muy corto (< 3 caracteres)"
                ))
        
        # Validar stack tecnológico
        if "stack" in config:
            stack_results = self._validate_stack_config(config["stack"])
            results.extend(stack_results)
        
        # Validar características
        if "features" in config:
            features_results = self._validate_features_config(config["features"])
            results.extend(features_results)
        
        return results
    
    def _validate_stack_config(self, stack: Dict[str, str]) -> List[ValidationResult]:
        """Validar configuración del stack"""
        results = []
        
        # Stacks válidos
        valid_stacks = {
            "backend": ["fastapi", "nestjs", "express", "django", "flask"],
            "frontend": ["nextjs", "react", "vue", "nuxt", "svelte", "angular"],
            "database": ["postgresql", "mysql", "mongodb", "sqlite"],
            "styling": ["tailwind", "styled_components", "sass", "css_modules"],
            "state_management": ["redux_toolkit", "zustand", "context_api", "pinia", "vuex"]
        }
        
        for key, value in stack.items():
            if key in valid_stacks:
                if value not in valid_stacks[key]:
                    results.append(ValidationResult(
                        name=f"Stack: {key}",
                        level=ValidationLevel.ERROR,
                        message=f"Valor inválido para {key}: {value}",
                        suggestion=f"Valores válidos: {', '.join(valid_stacks[key])}",
                        passed=False
                    ))
                else:
                    results.append(ValidationResult(
                        name=f"Stack: {key}",
                        level=ValidationLevel.SUCCESS,
                        message=f"{key}: {value} ✓"
                    ))
        
        # Validar compatibilidad entre tecnologías
        compatibility_results = self._validate_stack_compatibility(stack)
        results.extend(compatibility_results)
        
        return results
    
    def _validate_stack_compatibility(self, stack: Dict[str, str]) -> List[ValidationResult]:
        """Validar compatibilidad entre tecnologías del stack"""
        results = []
        
        backend = stack.get("backend")
        frontend = stack.get("frontend")
        state_mgmt = stack.get("state_management")
        
        # Validar compatibilidad state management con frontend
        if frontend and state_mgmt:
            incompatible_combinations = {
                "vue": ["redux_toolkit"],
                "nuxt": ["redux_toolkit"],
                "react": ["pinia", "vuex"],
                "nextjs": ["pinia", "vuex"],
                "angular": ["redux_toolkit", "zustand", "pinia", "vuex"]
            }
            
            if frontend in incompatible_combinations:
                if state_mgmt in incompatible_combinations[frontend]:
                    results.append(ValidationResult(
                        name="Stack Compatibility",
                        level=ValidationLevel.ERROR,
                        message=f"{state_mgmt} no es compatible con {frontend}",
                        passed=False
                    ))
        
        return results
    
    def _validate_features_config(self, features: List[str]) -> List[ValidationResult]:
        """Validar configuración de características"""
        results = []
        
        # Características válidas
        valid_features = [
            "authentication", "authorization", "billing", "notifications",
            "file_upload", "search", "analytics", "admin_panel",
            "api_documentation", "testing", "monitoring"
        ]
        
        for feature in features:
            if feature not in valid_features:
                results.append(ValidationResult(
                    name=f"Feature: {feature}",
                    level=ValidationLevel.WARNING,
                    message=f"Característica no reconocida: {feature}",
                    suggestion=f"Características válidas: {', '.join(valid_features)}"
                ))
        
        return results

class SchemaValidator:
    """
    Validador de schemas de proyecto
    
    Valida que los schemas generados por el ArchitectAgent
    sean válidos y consistentes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("genesis.schema_validator")
    
    def validate_project_schema(self, schema: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validar schema del proyecto
        
        Args:
            schema: Schema del proyecto
            
        Returns:
            Lista de resultados de validación
        """
        results = []
        
        # Validar estructura básica
        required_fields = ["project_name", "entities", "stack"]
        for field in required_fields:
            if field not in schema:
                results.append(ValidationResult(
                    name=f"Schema Field: {field}",
                    level=ValidationLevel.ERROR,
                    message=f"Campo obligatorio faltante en schema: {field}",
                    passed=False
                ))
        
        # Validar entidades
        if "entities" in schema:
            entities_results = self._validate_entities(schema["entities"])
            results.extend(entities_results)
        
        # Validar relaciones
        if "relationships" in schema:
            relations_results = self._validate_relationships(
                schema["relationships"], 
                schema.get("entities", [])
            )
            results.extend(relations_results)
        
        return results
    
    def _validate_entities(self, entities: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validar entidades del schema"""
        results = []
        
        entity_names = set()
        
        for entity in entities:
            # Verificar campos obligatorios
            if "name" not in entity:
                results.append(ValidationResult(
                    name="Entity Name",
                    level=ValidationLevel.ERROR,
                    message="Entidad sin nombre",
                    passed=False
                ))
                continue
            
            entity_name = entity["name"]
            
            # Verificar nombres únicos
            if entity_name in entity_names:
                results.append(ValidationResult(
                    name=f"Entity: {entity_name}",
                    level=ValidationLevel.ERROR,
                    message=f"Nombre de entidad duplicado: {entity_name}",
                    passed=False
                ))
            else:
                entity_names.add(entity_name)
            
            # Verificar atributos
            if "attributes" not in entity or not entity["attributes"]:
                results.append(ValidationResult(
                    name=f"Entity Attributes: {entity_name}",
                    level=ValidationLevel.WARNING,
                    message=f"Entidad {entity_name} sin atributos"
                ))
        
        return results
    
    def _validate_relationships(
        self, 
        relationships: List[Dict[str, Any]], 
        entities: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validar relaciones entre entidades"""
        results = []
        
        entity_names = {entity["name"] for entity in entities if "name" in entity}
        
        for relationship in relationships:
            # Verificar que las entidades existan
            from_entity = relationship.get("from")
            to_entity = relationship.get("to")
            
            if from_entity and from_entity not in entity_names:
                results.append(ValidationResult(
                    name="Relationship Validation",
                    level=ValidationLevel.ERROR,
                    message=f"Relación referencia entidad inexistente: {from_entity}",
                    passed=False
                ))
            
            if to_entity and to_entity not in entity_names:
                results.append(ValidationResult(
                    name="Relationship Validation",
                    level=ValidationLevel.ERROR,
                    message=f"Relación referencia entidad inexistente: {to_entity}",
                    passed=False
                ))
        
        return results