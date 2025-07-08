"""
Project Manager - Gestión de estado y configuración del proyecto

Este módulo es responsable de:
- Gestionar el estado del proyecto durante la generación
- Mantener metadata del proyecto
- Coordinar la creación de archivos y directorios
- Validar consistencia del proyecto
- Manejar configuraciones globales
- Generar reportes de progreso
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from genesis_engine.core.logging import get_logger
from genesis_engine.core.config import GenesisConfig
import hashlib
import threading
from genesis_engine.core.config import GenesisConfig

@dataclass
class ProjectMetadata:
    """Metadata del proyecto"""
    name: str
    description: str
    template: str
    version: str
    created_at: datetime
    last_modified: datetime
    generator_version: str
    stack: Dict[str, str]
    features: List[str]
    agents_used: List[str]
    generated_files: List[str]
    total_files: int
    project_size: int  # in bytes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_modified'] = self.last_modified.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """Crear desde diccionario"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_modified'] = datetime.fromisoformat(data['last_modified'])
        return cls(**data)

@dataclass
class FileTracker:
    """Rastreador de archivos generados"""
    path: str
    size: int
    created_at: datetime
    generator_agent: str
    template_used: Optional[str] = None
    checksum: Optional[str] = None

class ProjectManager:
    """
    Gestor de proyectos Genesis
    
    Mantiene el estado del proyecto durante todo el proceso de generación,
    coordina la creación de archivos y proporciona validación y reporting.
    """
    
    def __init__(self):
        self.project_path: Optional[Path] = None
        self.metadata: Optional[ProjectMetadata] = None
        self.file_trackers: Dict[str, FileTracker] = {}
        self.config_files: Set[str] = set()
        self.generated_directories: Set[str] = set()
        
        # Estado de generación
        self.generation_started: bool = False
        self.generation_completed: bool = False
        self.current_phase: Optional[str] = None
        
        # Logging
        self.logger = get_logger("genesis.project_manager")
        
        # Validaciones
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
    
    
    async def initialize_project(
        self, 
        project_path: Path, 
        config: Dict[str, Any]
    ):
        """
        Inicializar un nuevo proyecto
        
        Args:
            project_path: Ruta del proyecto
            config: Configuración del proyecto
        """
        self.project_path = project_path
        self.generation_started = True
        self.current_phase = "initialization"
        
        # Crear metadata inicial
        self.metadata = ProjectMetadata(
            name=config.get("name", project_path.name),
            description=config.get("description", ""),
            template=config.get("template", "custom"),
            version="1.0.0",
            created_at=datetime.utcnow(),
            last_modified=datetime.utcnow(),
            generator_version=GenesisConfig.get_version(),
            stack=config.get("stack", {}),
            features=config.get("features", []),
            agents_used=[],
            generated_files=[],
            total_files=0,
            project_size=0
        )
        
        # Crear estructura básica
        await self._create_basic_structure()
        
        # Guardar metadata inicial
        await self._save_metadata()
        
        self.logger.info(f"📁 Proyecto inicializado: {self.metadata.name}")
    
    async def _create_basic_structure(self):
        """Crear estructura básica de directorios"""
        if not self.project_path:
            raise ValueError("Project path not set")
        
        # Directorios básicos
        basic_dirs = [
            ".genesis",  # Metadata interna
            "docs",      # Documentación
            "scripts",   # Scripts de utilidad
        ]
        
        for dir_name in basic_dirs:
            dir_path = self.project_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            self.generated_directories.add(str(dir_path))
        
        # Archivo gitignore básico
        gitignore_content = self._generate_basic_gitignore()
        gitignore_path = self.project_path / ".gitignore"
        gitignore_path.write_text(gitignore_content)
        
        await self.track_file(
            str(gitignore_path),
            "project_manager",
            template_used="basic_gitignore"
        )
    
    def _generate_basic_gitignore(self) -> str:
        """Generar .gitignore básico"""
        return """# Genesis Engine
.genesis/cache/
.genesis/temp/

# Environment variables
.env
.env.local
.env.*.local

# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
.venv/

# Build outputs
dist/
build/
.next/
target/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Temporary files
*.tmp
*.temp
"""
    
    async def track_file(
        self,
        file_path: str,
        generator_agent: str,
        template_used: Optional[str] = None
    ):
        """
        Rastrear un archivo generado
        
        Args:
            file_path: Ruta del archivo
            generator_agent: Agente que generó el archivo
            template_used: Template utilizado (opcional)
        """
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            self.logger.warning(f"⚠️ Archivo no existe para rastrear: {file_path}")
            return
        
        # Calcular tamaño y checksum
        file_size = path_obj.stat().st_size
        checksum = self._calculate_checksum(path_obj)
        
        # Crear tracker
        tracker = FileTracker(
            path=file_path,
            size=file_size,
            created_at=datetime.utcnow(),
            generator_agent=generator_agent,
            template_used=template_used,
            checksum=checksum
        )
        
        self.file_trackers[file_path] = tracker
        
        # Actualizar metadata
        if self.metadata:
            relative_path = str(path_obj.relative_to(self.project_path))
            if relative_path not in self.metadata.generated_files:
                self.metadata.generated_files.append(relative_path)
            
            self.metadata.total_files = len(self.metadata.generated_files)
            self.metadata.project_size += file_size
            self.metadata.last_modified = datetime.utcnow()
            
            # Agregar agente si no está en la lista
            if generator_agent not in self.metadata.agents_used:
                self.metadata.agents_used.append(generator_agent)
        
        self.logger.debug(f"📝 Archivo rastreado: {relative_path} ({file_size} bytes)")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum MD5 de un archivo"""
        import hashlib
        
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning(f"Error calculando checksum para {file_path}: {e}")
            return ""
    
    async def update_phase(self, phase: str):
        """Actualizar fase actual de generación"""
        self.current_phase = phase
        
        if self.metadata:
            self.metadata.last_modified = datetime.utcnow()
        
        await self._save_metadata()
        self.logger.info(f"📊 Fase actualizada: {phase}")
    
    async def complete_generation(self):
        """Marcar generación como completada"""
        self.generation_completed = True
        self.current_phase = "completed"
        
        if self.metadata:
            self.metadata.last_modified = datetime.utcnow()
        
        # Validación final
        await self._perform_final_validation()
        
        # Guardar metadata final
        await self._save_metadata()
        
        # Generar reporte final
        await self._generate_final_report()
        
        self.logger.info("✅ Generación completada")
    
    async def _save_metadata(self):
        """Guardar metadata del proyecto"""
        if not self.project_path or not self.metadata:
            return
        
        metadata_dir = self.project_path / ".genesis"
        metadata_dir.mkdir(exist_ok=True)
        
        metadata_file = metadata_dir / "project.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata.to_dict(), f, indent=2)
        
        # También guardar file trackers
        trackers_file = metadata_dir / "files.json"
        trackers_data = {
            path: {
                "size": tracker.size,
                "created_at": tracker.created_at.isoformat(),
                "generator_agent": tracker.generator_agent,
                "template_used": tracker.template_used,
                "checksum": tracker.checksum
            }
            for path, tracker in self.file_trackers.items()
        }
        
        with open(trackers_file, 'w') as f:
            json.dump(trackers_data, f, indent=2)
    
    async def load_project(self, project_path: Path):
        """
        Cargar proyecto existente
        
        Args:
            project_path: Ruta del proyecto
        """
        self.project_path = project_path
        
        metadata_file = project_path / ".genesis" / "project.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata del proyecto no encontrada: {metadata_file}")
        
        # Cargar metadata
        with open(metadata_file, 'r') as f:
            metadata_data = json.load(f)
        
        self.metadata = ProjectMetadata.from_dict(metadata_data)
        
        # Cargar file trackers
        trackers_file = project_path / ".genesis" / "files.json"
        if trackers_file.exists():
            with open(trackers_file, 'r') as f:
                trackers_data = json.load(f)
            
            for path, data in trackers_data.items():
                self.file_trackers[path] = FileTracker(
                    path=path,
                    size=data["size"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    generator_agent=data["generator_agent"],
                    template_used=data.get("template_used"),
                    checksum=data.get("checksum")
                )
        
        self.logger.info(f"📂 Proyecto cargado: {self.metadata.name}")
    
    async def validate_project(self) -> Dict[str, Any]:
        """
        Validar consistencia del proyecto
        
        Returns:
            Resultado de validación
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }
        
        if not self.project_path or not self.metadata:
            validation_result["valid"] = False
            validation_result["errors"].append("Proyecto no inicializado")
            return validation_result
        
        # Validar archivos existentes
        missing_files = []
        for file_path in self.metadata.generated_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            validation_result["warnings"].extend([
                f"Archivo faltante: {f}" for f in missing_files
            ])
        
        # Validar integridad de archivos (checksums)
        corrupted_files = []
        for file_path, tracker in self.file_trackers.items():
            if tracker.checksum and Path(file_path).exists():
                current_checksum = self._calculate_checksum(Path(file_path))
                if current_checksum != tracker.checksum:
                    corrupted_files.append(file_path)
        
        if corrupted_files:
            validation_result["warnings"].extend([
                f"Archivo modificado: {f}" for f in corrupted_files
            ])
        
        # Estadísticas
        validation_result["stats"] = {
            "total_files": len(self.metadata.generated_files),
            "tracked_files": len(self.file_trackers),
            "missing_files": len(missing_files),
            "modified_files": len(corrupted_files),
            "project_size": self._format_size(self.metadata.project_size),
            "agents_used": len(self.metadata.agents_used)
        }
        
        return validation_result
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatear tamaño en bytes"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    async def _perform_final_validation(self):
        """Realizar validación final del proyecto"""
        validation_result = await self.validate_project()
        
        self.validation_errors = validation_result["errors"]
        self.validation_warnings = validation_result["warnings"]
        
        if self.validation_errors:
            self.logger.error(f"❌ Errores de validación: {len(self.validation_errors)}")
            for error in self.validation_errors:
                self.logger.error(f"  - {error}")
        
        if self.validation_warnings:
            self.logger.warning(f"⚠️ Advertencias: {len(self.validation_warnings)}")
            for warning in self.validation_warnings:
                self.logger.warning(f"  - {warning}")
    
    async def _generate_final_report(self):
        """Generar reporte final del proyecto"""
        if not self.project_path or not self.metadata:
            return
        
        report_content = self._create_report_content()
        
        report_file = self.project_path / ".genesis" / "generation_report.md"
        report_file.write_text(report_content)
        
        self.logger.info(f"📄 Reporte generado: {report_file}")
    
    def _create_report_content(self) -> str:
        """Crear contenido del reporte"""
        if not self.metadata:
            return ""
        
        validation_result = {}  # Se obtendría de _perform_final_validation
        
        report = f"""# Genesis Engine - Reporte de Generación

## Información del Proyecto

- **Nombre**: {self.metadata.name}
- **Descripción**: {self.metadata.description}
- **Template**: {self.metadata.template}
- **Versión**: {self.metadata.version}
- **Creado**: {self.metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Última modificación**: {self.metadata.last_modified.strftime('%Y-%m-%d %H:%M:%S')}

## Stack Tecnológico

"""
        
        for key, value in self.metadata.stack.items():
            report += f"- **{key.title()}**: {value}\n"
        
        report += f"""

## Características Incluidas

"""
        
        for feature in self.metadata.features:
            report += f"- {feature}\n"
        
        report += f"""

## Estadísticas de Generación

- **Archivos generados**: {self.metadata.total_files}
- **Tamaño del proyecto**: {self._format_size(self.metadata.project_size)}
- **Agentes utilizados**: {len(self.metadata.agents_used)}

### Agentes Utilizados

"""
        
        for agent in self.metadata.agents_used:
            report += f"- {agent}\n"
        
        report += f"""

## Archivos Generados por Agente

"""
        
        # Agrupar archivos por agente
        files_by_agent = {}
        for file_path, tracker in self.file_trackers.items():
            agent = tracker.generator_agent
            if agent not in files_by_agent:
                files_by_agent[agent] = []
            
            relative_path = str(Path(file_path).relative_to(self.project_path))
            files_by_agent[agent].append(relative_path)
        
        for agent, files in files_by_agent.items():
            report += f"### {agent}\n\n"
            for file_path in sorted(files):
                report += f"- {file_path}\n"
            report += "\n"
        
        if self.validation_errors or self.validation_warnings:
            report += "## Validación\n\n"
            
            if self.validation_errors:
                report += "### Errores\n\n"
                for error in self.validation_errors:
                    report += f"- ❌ {error}\n"
                report += "\n"
            
            if self.validation_warnings:
                report += "### Advertencias\n\n"
                for warning in self.validation_warnings:
                    report += f"- ⚠️ {warning}\n"
                report += "\n"
        
        report += f"""
## Siguientes Pasos

1. Revisar la configuración en cada directorio
2. Instalar dependencias según las instrucciones
3. Configurar variables de entorno
4. Ejecutar pruebas iniciales
5. Desplegar en el entorno deseado

---

*Generado por Genesis Engine v{GenesisConfig.get_version()} el {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del proyecto"""
        if not self.metadata:
            return {}
        
        # Agrupar archivos por extensión
        extensions = {}
        for file_path in self.metadata.generated_files:
            ext = Path(file_path).suffix.lower()
            if not ext:
                ext = "sin_extension"
            extensions[ext] = extensions.get(ext, 0) + 1
        
        # Agrupar archivos por agente
        agents_stats = {}
        for tracker in self.file_trackers.values():
            agent = tracker.generator_agent
            if agent not in agents_stats:
                agents_stats[agent] = {"files": 0, "size": 0}
            agents_stats[agent]["files"] += 1
            agents_stats[agent]["size"] += tracker.size
        
        return {
            "project_name": self.metadata.name,
            "total_files": self.metadata.total_files,
            "total_size": self.metadata.project_size,
            "formatted_size": self._format_size(self.metadata.project_size),
            "agents_count": len(self.metadata.agents_used),
            "features_count": len(self.metadata.features),
            "generation_time": (self.metadata.last_modified - self.metadata.created_at).total_seconds(),
            "files_by_extension": extensions,
            "files_by_agent": agents_stats,
            "validation_errors": len(self.validation_errors),
            "validation_warnings": len(self.validation_warnings)
        }
    
    async def cleanup_temp_files(self):
        """Limpiar archivos temporales"""
        if not self.project_path:
            return
        
        temp_dirs = [
            self.project_path / ".genesis" / "temp",
            self.project_path / ".genesis" / "cache"
        ]
        
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.logger.debug(f"🧹 Limpiado: {temp_dir}")
    
    def __del__(self):
        """Cleanup al destruir el objeto"""
        if hasattr(self, 'project_path') and self.project_path:
            try:
                # Guardar metadata final si es necesario
                if hasattr(self, 'metadata') and self.metadata:
                    import asyncio
                    if not self.generation_completed:
                        # Usar run_until_complete de forma segura
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # Si hay un loop corriendo, crear tarea
                                asyncio.create_task(self._save_metadata())
                            else:
                                loop.run_until_complete(self._save_metadata())
                        except:
                            # Fallback: guardar sincrónicamente
                            pass
            except Exception:
                pass  # Ignorar errores en destructor