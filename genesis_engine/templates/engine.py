"""
Template Engine - Motor de plantillas Jinja2 para Genesis Engine

Este módulo es responsable de:
- Cargar y renderizar plantillas Jinja2
- Gestionar templates modulares por tecnología
- Proporcionar funciones helper personalizadas
- Validar sintaxis y variables de templates
- Cache de templates para mejor performance
"""

import os
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import fnmatch
from datetime import datetime
import asyncio
from genesis_engine.core.logging import get_logger
from genesis_engine.core.config import get_config

from jinja2 import Environment, FileSystemLoader, Template, TemplateError
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError

class TemplateEngine:
    """
    Motor de plantillas para Genesis Engine

    Gestiona la carga, renderizado y validación de templates Jinja2
    para generar código en diferentes tecnologías y frameworks.
    """

    # Variables obligatorias por plantilla integrada
    REQUIRED_VARIABLES: Dict[str, List[str]] = {
        "backend/fastapi/*": [
            "project_name",
            "description",
            "version",
            "entities",
            "database_type",
        ],
        "backend/nestjs/*": [
            "project_name",
            "description",
            "port",
            "entities",
        ],
        "frontend/nextjs/*": [
            "project_name",
            "description",
            "typescript",
            "styling",
            "state_management",
        ],
        "frontend/react/*": [
            "project_name",
            "description",
            "typescript",
            "styling",
            "state_management",
        ],
        "saas-basic/*": [
            "project_name",
            "description",
        ],
    }
    
    def __init__(self, templates_dir: Optional[Path] = None, strict_validation: Optional[bool] = None):
        self.templates_dir = templates_dir or self._get_default_templates_dir()
        if strict_validation is None:
            strict_validation = get_config().__dict__.get("strict_template_validation", True)
        self.strict_validation = strict_validation
        self.env = self._setup_jinja_environment()
        self.logger = get_logger("genesis.template_engine")
        
        # Cache de templates renderizados
        self._template_cache: Dict[str, Template] = {}
        
        # Funciones helper registradas
        self._helpers: Dict[str, callable] = {}
        
        # Filtros personalizados
        self._custom_filters: Dict[str, callable] = {}
        
        # Configurar helpers y filtros por defecto
        self._setup_default_helpers()
        self._setup_default_filters()
    
    def _get_default_templates_dir(self) -> Path:
        """Obtener directorio por defecto de templates"""
        current_file = Path(__file__).parent
        return current_file.parent / "templates"
    
    def _setup_jinja_environment(self) -> Environment:
        """Configurar entorno Jinja2"""
        loader = FileSystemLoader(str(self.templates_dir))
        
        env = Environment(
            loader=loader,
            autoescape=False,  # Para código, no HTML
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        return env
    
    def _setup_default_helpers(self):
        """Configurar funciones helper por defecto"""
        self._helpers.update({
            'camel_case': self._camel_case,
            'snake_case': self._snake_case,
            'kebab_case': self._kebab_case,
            'pascal_case': self._pascal_case,
            'plural': self._pluralize,
            'singular': self._singularize,
            'timestamp': lambda: datetime.utcnow().isoformat(),
            'uuid': self._generate_uuid,
            'random_secret': self._generate_random_secret,
            'format_type': self._format_type_mapping,
            'sql_type': self._get_sql_type,
            'typescript_type': self._get_typescript_type,
            'python_type': self._get_python_type
        })
        
        # Registrar helpers en el entorno Jinja2
        self.env.globals.update(self._helpers)
    
    def _setup_default_filters(self):
        """Configurar filtros personalizados"""
        self._custom_filters.update({
            'camelcase': self._camel_case,
            'camel_case': self._camel_case,
            'snakecase': self._snake_case,
            'snake_case': self._snake_case,
            'kebabcase': self._kebab_case,
            'kebab_case': self._kebab_case,
            'pascalcase': self._pascal_case,
            'pascal_case': self._pascal_case,
            'plural': self._pluralize,
            'singular': self._singularize,
            'sqltype': self._get_sql_type,
            'tstype': self._get_typescript_type,
            'pytype': self._get_python_type,
            'indent_code': self._indent_code,
            'quote_string': self._quote_string
        })
        
        # Registrar filtros en el entorno
        self.env.filters.update(self._custom_filters)

    def get_template_variables(self, template_name: str) -> List[str]:
        """
        Obtener variables usadas en un template.
        
        Args:
            template_name: Nombre del template
            
        Returns:
            Lista de variables
        """
        try:
            template_source = self.env.get_template(template_name).source
            from jinja2 import meta
            ast = self.env.parse(template_source)
            variables = meta.find_undeclared_variables(ast)
            return list(variables)
        except Exception as e:
            self.logger.warning(f"Error analyzing template {template_name}: {e}")
            return []

    def validate_required_variables(self, template_name: str, variables: Dict[str, Any]):
        """Validar que se proporcionen las variables requeridas para una plantilla."""

        missing = set()

        # Reglas específicas por patrón de template
        for pattern, required in self.REQUIRED_VARIABLES.items():
            if fnmatch.fnmatch(template_name, pattern):
                for name in required:
                    if name not in variables:
                        missing.add(name)

        # Validación genérica basada en variables esperadas dentro del template
        expected = set(self.get_template_variables(template_name))
        generic_required = {"project_name", "description"}
        for name in generic_required:
            if name in expected and name not in variables:
                missing.add(name)

        if missing:
            message = f"Variables faltantes para {template_name}: {', '.join(sorted(missing))}"
            if self.strict_validation:
                raise ValueError(message)
            else:
                self.logger.warning(message)
                # Agregar variables por defecto para evitar errores
                for name in missing:
                    if name == "project_name":
                        variables[name] = "my_project"
                    elif name == "description":
                        variables[name] = "Generated project"
                    else:
                        variables[name] = ""

    # MÉTODO SÍNCRONO AGREGADO para compatibilidad con tests
    def render_template_sync(
        self,
        template_name: str,
        variables: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> str:
        """
        Renderizar plantilla de forma síncrona.
        COMPATIBILIDAD: Para mantener compatibilidad con código síncrono.
        
        Args:
            template_name: Nombre del template
            variables: Variables para el template
            use_cache: Usar cache de templates
            
        Returns:
            Contenido renderizado
        """
        vars_clean = variables or {}
        
        # Validar variables requeridas (flexible para compatibilidad)
        try:
            self.validate_required_variables(template_name, vars_clean)
        except ValueError as e:
            if self.strict_validation:
                raise ValueError(str(e))
            else:
                self.logger.warning(f"Missing variables for {template_name}, using defaults")
        
        try:
            # Obtener template (con cache si está habilitado)
            if use_cache and template_name in self._template_cache:
                template = self._template_cache[template_name]
            else:
                template_key = template_name.replace("\\", "/")
                template = self.env.get_template(template_key)
                if use_cache:
                    self._template_cache[template_name] = template

            # Agregar variables globales útiles
            vars_clean.update({
                'generated_at': datetime.utcnow().isoformat(),
                'generator': 'Genesis Engine',
                'template_name': template_name
            })
            
            return template.render(**vars_clean)
            
        except TemplateNotFound:
            raise FileNotFoundError(f"Template not found: {template_name}")
        except TemplateError as e:
            raise ValueError(f"Template error in {template_name}: {e}")

    def render_template(
        self,
        template_name: str,
        variables: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> str:
        """Versión síncrona del renderizado de plantillas."""
        return self.render_template_sync(template_name, variables, use_cache)

    async def render_template_async(
        self,
        template_name: str,
        variables: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> str:
        """Renderizar una plantilla de forma asíncrona."""
        vars_clean = variables or {}
        
        # Validar variables antes de ejecutar en hilo separado
        self.validate_required_variables(template_name, vars_clean)
        
        try:
            # Ejecutar renderizado síncrono en executor
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                self.render_template_sync,
                template_name,
                vars_clean,
                use_cache
            )
            
            self.logger.debug(f"✅ Template renderizado: {template_name}")
            return content
            
        except Exception as e:
            self.logger.error(f"❌ Error renderizando template {template_name}: {e}")
            raise
    
    def render_string_template(
        self,
        template_string: str,
        variables: Dict[str, Any] = None
    ) -> str:
        """Renderizar template desde string de forma síncrona."""
        render_vars = variables or {}
        template = self.env.from_string(template_string)
        render_vars.update({
            "generated_at": datetime.utcnow().isoformat(),
            "generator": "Genesis Engine",
        })
        return template.render(**render_vars)

    async def render_string_template_async(
        self,
        template_string: str,
        variables: Dict[str, Any] = None,
    ) -> str:
        """Renderizar una plantilla desde un string de forma asíncrona."""
        vars_clean = variables or {}
        try:
            return await asyncio.to_thread(
                self.render_string_template, template_string, vars_clean
            )
        except Exception as e:
            self.logger.error(f"❌ Error renderizando string template: {e}")
            raise RuntimeError(f"Error renderizando string template: {e}") from e

    # MÉTODO SÍNCRONO AGREGADO para compatibilidad con tests
    def generate_project_sync(
        self,
        template_name: str,
        output_dir: Union[str, Path],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """
        Generar proyecto completo desde template de forma síncrona.
        COMPATIBILIDAD: Para mantener compatibilidad con código síncrono.
        
        Args:
            template_name: Nombre del template/directorio
            output_dir: Directorio de salida
            context: Variables para los templates
            
        Returns:
            Lista de archivos generados
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists() or not template_path.is_dir():
            raise FileNotFoundError(f"Directorio de template no encontrado: {template_path}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files: List[Path] = []
        context = context or {}
        
        for root, _, files in os.walk(template_path):
            rel_root = Path(root).relative_to(template_path)
            
            for fname in files:
                src = Path(root) / fname
                relative_template = Path(template_name) / rel_root / fname
                dest_rel = rel_root / fname

                if fname.endswith(".j2"):
                    # Template file - renderizar
                    # Validar variables requeridas (flexible para compatibilidad)
                    try:
                        self.validate_required_variables(relative_template.as_posix(), context)
                    except ValueError as e:
                        self.logger.warning(f"Missing variables for {relative_template}, using defaults")
                        # Agregar variables por defecto para evitar errores
                        if 'project_name' not in context:
                            context['project_name'] = 'my_project'
                        if 'description' not in context:
                            context['description'] = 'Generated project'
                    
                    try:
                        content = self.render_template_sync(relative_template.as_posix(), context)
                        
                        dest = output_path / dest_rel.with_suffix("")  # Remover .j2
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_text(content, encoding="utf-8")
                        generated_files.append(dest)
                        
                        self.logger.debug(f"Generated: {dest}")
                        
                    except Exception as e:
                        self.logger.error(f"Error rendering {relative_template}: {e}")
                        raise
                else:
                    # Archivo estático - copiar
                    dest = output_path / dest_rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                    generated_files.append(dest)
                    self.logger.debug(f"Copied: {dest}")

        self.logger.info(f"Generated {len(generated_files)} files in {output_path}")
        return generated_files

    async def generate_project(
        self,
        template_name: str,
        output_dir: Union[str, Path],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generar proyecto de forma asíncrona."""
        return await asyncio.to_thread(
            self.generate_project_sync, template_name, output_dir, context
        )

    async def generate_project_async(
        self,
        template_name: str,
        output_dir: Union[str, Path],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Renderizar todas las plantillas dentro de un directorio de forma asíncrona"""
        return await self.generate_project(template_name, output_dir, context)
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validar sintaxis de un template
        
        Args:
            template_name: Nombre del template
            
        Returns:
            Resultado de validación
        """
        try:
            template = self.env.get_template(template_name)
            
            # Intentar compilar el template
            template.environment.compile_expression(template.source, undefined_to_none=False)
            
            return {
                "valid": True,
                "template_name": template_name,
                "message": "Template válido"
            }
            
        except TemplateNotFound:
            return {
                "valid": False,
                "template_name": template_name,
                "error": "Template no encontrado"
            }
            
        except TemplateSyntaxError as e:
            return {
                "valid": False,
                "template_name": template_name,
                "error": f"Error de sintaxis: {e}",
                "line": getattr(e, 'lineno', None)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "template_name": template_name,
                "error": str(e)
            }
    
    def list_templates(self, pattern: Optional[str] = None) -> List[str]:
        """
        Listar templates disponibles
        
        Args:
            pattern: Patrón de filtro (ej: "fastapi/*")
            
        Returns:
            Lista de nombres de templates
        """
        try:
            templates = self.env.list_templates()
            
            if pattern:
                import fnmatch
                templates = [t for t in templates if fnmatch.fnmatch(t, pattern)]
            
            return sorted(templates)
            
        except Exception as e:
            self.logger.error(f"❌ Error listando templates: {e}")
            return []
    
    def register_helper(self, name: str, func: callable):
        """
        Registrar una función helper personalizada
        
        Args:
            name: Nombre del helper
            func: Función helper
        """
        self._helpers[name] = func
        self.env.globals[name] = func
        self.logger.debug(f"Helper registrado: {name}")
    
    def register_filter(self, name: str, func: callable):
        """
        Registrar un filtro personalizado
        
        Args:
            name: Nombre del filtro
            func: Función filtro
        """
        self._custom_filters[name] = func
        self.env.filters[name] = func
        self.logger.debug(f"Filtro registrado: {name}")
    
    def clear_cache(self):
        """Limpiar cache de templates"""
        self._template_cache.clear()
        self.logger.debug("Cache de templates limpiado")
    
    # Helper functions
    def _camel_case(self, text: str) -> str:
        """Convertir a camelCase"""
        if not text:
            return text
        
        words = text.replace('-', '_').split('_')
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _snake_case(self, text: str) -> str:
        """Convertir a snake_case"""
        import re
        
        # Insertar _ antes de mayúsculas
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        # Insertar _ antes de mayúsculas seguidas de minúsculas
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        
        return s2.lower().replace('-', '_')
    
    def _kebab_case(self, text: str) -> str:
        """Convertir a kebab-case"""
        return self._snake_case(text).replace('_', '-')
    
    def _pascal_case(self, text: str) -> str:
        """Convertir a PascalCase"""
        if not text:
            return text
        
        words = text.replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in words)
    
    def _pluralize(self, word: str) -> str:
        """Pluralizar palabra (inglés básico)"""
        if not word:
            return word
        
        if word.endswith('y'):
            return word[:-1] + 'ies'
        elif word.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return word + 'es'
        else:
            return word + 's'
    
    def _singularize(self, word: str) -> str:
        """Singularizar palabra (inglés básico)"""
        if not word:
            return word
        
        if word.endswith('ies'):
            return word[:-3] + 'y'
        elif word.endswith('es') and len(word) > 3:
            return word[:-2]
        elif word.endswith('s') and len(word) > 2:
            return word[:-1]
        else:
            return word
    
    def _generate_uuid(self) -> str:
        """Generar UUID"""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_random_secret(self, length: int = 32) -> str:
        """Generar secreto aleatorio"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _format_type_mapping(self, attr_type: str, target: str) -> str:
        """Mapear tipos entre diferentes lenguajes"""
        mappings = {
            'sql': self._get_sql_type,
            'typescript': self._get_typescript_type,
            'python': self._get_python_type
        }
        
        mapper = mappings.get(target.lower())
        if mapper:
            return mapper(attr_type)
        
        return attr_type
    
    def _get_sql_type(self, attr_type: str) -> str:
        """Obtener tipo SQL para un tipo genérico"""
        type_mapping = {
            'string': 'VARCHAR(255)',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'decimal': 'DECIMAL(10,2)',
            'boolean': 'BOOLEAN',
            'datetime': 'TIMESTAMP',
            'date': 'DATE',
            'uuid': 'UUID',
            'email': 'VARCHAR(255)',
            'password_hash': 'VARCHAR(255)',
            'json': 'JSONB'
        }
        
        return type_mapping.get(attr_type.lower(), 'VARCHAR(255)')
    
    def _get_typescript_type(self, attr_type: str) -> str:
        """Obtener tipo TypeScript para un tipo genérico"""
        type_mapping = {
            'string': 'string',
            'text': 'string',
            'integer': 'number',
            'decimal': 'number',
            'boolean': 'boolean',
            'datetime': 'Date',
            'date': 'Date',
            'uuid': 'string',
            'email': 'string',
            'password_hash': 'string',
            'json': 'object'
        }
        
        return type_mapping.get(attr_type.lower(), 'string')
    
    def _get_python_type(self, attr_type: str) -> str:
        """Obtener tipo Python para un tipo genérico"""
        type_mapping = {
            'string': 'str',
            'text': 'str',
            'integer': 'int',
            'decimal': 'Decimal',
            'boolean': 'bool',
            'datetime': 'datetime',
            'date': 'date',
            'uuid': 'UUID',
            'email': 'str',
            'password_hash': 'str',
            'json': 'dict'
        }
        
        return type_mapping.get(attr_type.lower(), 'str')
    
    def _indent_code(self, text: str, spaces: int = 4) -> str:
        """Indentar código"""
        if not text:
            return text
        
        indent = ' ' * spaces
        lines = text.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        
        return '\n'.join(indented_lines)
    
    def _quote_string(self, text: str, quote_type: str = 'double') -> str:
        """Agregar comillas a un string"""
        if quote_type == 'single':
            return f"'{text}'"
        else:
            return f'"{text}"'

# Instancia global del motor de templates
template_engine = TemplateEngine()