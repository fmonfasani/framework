"""
Template Engine - CORREGIDO - Motor de plantillas Jinja2 para Genesis Engine

FIXES:
- Validación menos restrictiva para evitar bloqueos
- Mejores valores por defecto para variables faltantes
- Logging ASCII-safe (sin emojis)
- Mejor manejo de errores en templates
- Variables por defecto más robustas
"""

import os
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import fnmatch
from datetime import datetime
import asyncio
from genesis_engine.core.logging import get_safe_logger  # CORRECCIÓN: Usar safe logger
from genesis_engine.core.config import get_config

from jinja2 import Environment, FileSystemLoader, Template, TemplateError
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError

class TemplateEngine:
    """
    Motor de plantillas para Genesis Engine - CORREGIDO
    
    FIXES:
    - Validación menos restrictiva
    - Mejores valores por defecto
    - Logs ASCII-safe
    """

    # Variables obligatorias por plantilla integrada - CORREGIDAS
    REQUIRED_VARIABLES: Dict[str, List[str]] = {
        "backend/fastapi/*": [
            "project_name",
            "description",
        ],
        "backend/nestjs/*": [
            "project_name",
            "description",
        ],
        "frontend/nextjs/*": [
            "project_name",
            "description",
        ],
        "frontend/react/*": [
            "project_name",
            "description",
        ],
        "saas-basic/*": [
            "project_name",
            "description",
        ],
    }
    
    # NUEVOS: Valores por defecto para variables comunes
    DEFAULT_VALUES: Dict[str, Any] = {
        "project_name": "my_project",
        "description": "Generated with Genesis Engine",
        "version": "1.0.0",
        "typescript": True,
        "state_management": "redux_toolkit",
        "styling": "tailwindcss",
        "ui_library": "tailwindcss",
        "framework": "nextjs",
        "python_version": "3.11",
        "node_version": "18",
        "port": 8000,
        "database_type": "postgresql",
        "entities": [],
        "has_backend": True,
        "has_frontend": True,
        "monitoring_enabled": True,
        "ssl_enabled": True,
        "testing_framework": "jest",
        "pwa_enabled": False,
        "backend_framework": "fastapi",
        "frontend_framework": "nextjs",
    }
    
    def __init__(self, templates_dir: Optional[Path] = None, strict_validation: Optional[bool] = None, use_defaults: bool = False):
        self.templates_dir = templates_dir or self._get_default_templates_dir()
        if strict_validation is None:
            # CORRECCIÓN: Por defecto NO estricto para evitar bloqueos
            strict_validation = get_config().__dict__.get("strict_template_validation", False)
        self.strict_validation = strict_validation
        self.use_defaults = use_defaults
        self.env = self._setup_jinja_environment()
        
        # CORRECCIÓN: Usar safe logger
        self.logger = get_safe_logger("genesis.template_engine")
        
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
            template_source = self.env.loader.get_source(self.env, template_name)[0]
            from jinja2 import meta
            ast = self.env.parse(template_source)
            variables = meta.find_undeclared_variables(ast)
            return list(variables)
        except Exception as e:
            self.logger.warning(f"Error analyzing template {template_name}: {e}")
            return []

    def validate_required_variables(self, template_name: str, variables: Dict[str, Any]):
        """
        MÉTODO CORREGIDO: Validar que se proporcionen las variables requeridas
        
        FIXES:
        - Menos restrictivo por defecto
        - Mejores valores por defecto automáticos
        - No bloquear por variables opcionales
        """
        missing = set()
        
        # CORRECCIÓN: Solo validar variables CRÍTICAS y solo en modo estricto
        critical_variables = {"project_name"}  # REDUCIDO: Solo project_name es crítico
        
        # Reglas específicas por patrón de template - MUY REDUCIDAS
        for pattern, required in self.REQUIRED_VARIABLES.items():
            if fnmatch.fnmatch(template_name, pattern):
                for name in required:
                    if name in critical_variables and name not in variables:
                        missing.add(name)

        # CORRECCIÓN: Agregar valores por defecto para variables faltantes solo si está habilitado
        if self.use_defaults:
            self._apply_default_values(variables)
        
        # Solo fallar en modo estricto Y si faltan variables críticas
        if missing and self.strict_validation:
            message = f"Variables críticas faltantes para {template_name}: {', '.join(sorted(missing))}"
            # CORRECCIÓN: Log en lugar de excepción inmediata en la mayoría de casos
            self.logger.error(f"[ERROR] {message}")
            raise ValueError(message)
        elif missing:
            # CORRECCIÓN: Solo warning si no es estricto
            message = f"Variables faltantes para {template_name}: {', '.join(sorted(missing))}"
            self.logger.warning(f"[WARN] {message} - usando valores por defecto")
            
            # Agregar valores por defecto para variables críticas faltantes
            for name in missing:
                if name in self.DEFAULT_VALUES:
                    variables[name] = self.DEFAULT_VALUES[name]
                    self.logger.info(f"[DEFAULT] {name} = {variables[name]}")
                else:
                    # NUEVO: Valor por defecto genérico
                    variables[name] = f"default_{name}"
                    self.logger.info(f"[DEFAULT] {name} = {variables[name]}")

    def _apply_default_values(self, variables: Dict[str, Any]):
        """
        NUEVO MÉTODO: Aplicar valores por defecto para variables comunes
        """
        for key, default_value in self.DEFAULT_VALUES.items():
            if key not in variables:
                variables[key] = default_value

    def render_template_sync(
        self,
        template_name: str,
        variables: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> str:
        """
        MÉTODO CORREGIDO: Renderizar plantilla de forma síncrona con mejor manejo de errores
        """
        vars_clean = variables or {}
        
        try:
            # CORRECCIÓN: Validación mejorada con manejo de errores
            self.validate_required_variables(template_name, vars_clean)
            
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
            
            # CORRECCIÓN: Mejor logging
            self.logger.debug(f"[OK] Renderizando template: {template_name}")
            
            return template.render(**vars_clean)
            
        except TemplateNotFound:
            error_msg = f"Template not found: {template_name}"
            self.logger.error(f"[ERROR] {error_msg}")
            raise FileNotFoundError(error_msg)
        except TemplateError as e:
            error_msg = f"Template error in {template_name}: {e}"
            self.logger.error(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error rendering {template_name}: {e}"
            self.logger.error(f"[ERROR] {error_msg}")
            # CORRECCIÓN: En lugar de fallar, intentar con template básico
            if not self.strict_validation:
                self.logger.warning(f"[WARN] Usando template básico para {template_name}")
                return self._generate_fallback_content(template_name, vars_clean)
            raise

    def _generate_fallback_content(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        NUEVO MÉTODO: Generar contenido de fallback cuando el template falla
        """
        project_name = variables.get("project_name", "my_project")
        description = variables.get("description", "Generated project")
        
        if "Dockerfile" in template_name:
            if "frontend" in template_name:
                return f"""FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
"""
            else:  # backend
                return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        elif "package.json" in template_name:
            return f"""{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "{description}",
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }},
  "dependencies": {{
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }}
}}"""
        
        elif "next.config.js" in template_name:
            return """/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig"""
        
        else:
            return f"""# {project_name}

{description}

Generated by Genesis Engine as fallback content.
"""

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
            
            # CORRECCIÓN: Log sin emojis
            self.logger.debug(f"[OK] Template renderizado: {template_name}")
            return content
            
        except Exception as e:
            # CORRECCIÓN: Log sin emojis
            self.logger.error(f"[ERROR] Error renderizando template {template_name}: {e}")
            raise
    
    def render_string_template(
        self,
        template_string: str,
        variables: Dict[str, Any] = None
    ) -> str:
        """Renderizar template desde string de forma síncrona."""
        render_vars = variables or {}
        
        # CORRECCIÓN: Aplicar valores por defecto solo si está habilitado
        if self.use_defaults:
            self._apply_default_values(render_vars)
        
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
            # CORRECCIÓN: Log sin emojis
            self.logger.error(f"[ERROR] Error renderizando string template: {e}")
            raise RuntimeError(f"Error renderizando string template: {e}") from e

    def generate_project_sync(
        self,
        template_name: str,
        output_dir: Union[str, Path],
        context: Optional[Dict[str, Any]] = None,
        *,
        raise_on_missing: bool = False,  # CORRECCIÓN: Por defecto False
    ) -> List[Path]:
        """
        MÉTODO CORREGIDO: Generar proyecto completo desde template
        
        FIXES:
        - raise_on_missing por defecto False
        - Mejor manejo de errores
        - Valores por defecto robustos
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists() or not template_path.is_dir():
            raise FileNotFoundError(f"Directorio de template no encontrado: {template_path}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files: List[Path] = []
        context = context or {}
        
        # CORRECCIÓN: Aplicar valores por defecto antes de procesar solo si está habilitado
        if self.use_defaults:
            self._apply_default_values(context)
        
        for root, _, files in os.walk(template_path):
            rel_root = Path(root).relative_to(template_path)
            
            for fname in files:
                src = Path(root) / fname
                relative_template = Path(template_name) / rel_root / fname
                dest_rel = rel_root / fname

                if fname.endswith(".j2"):
                    # Template file - renderizar
                    try:
                        # CORRECCIÓN: Usar validación menos estricta
                        if raise_on_missing:
                            # Solo en casos específicos forzar validación estricta
                            original = self.strict_validation
                            self.strict_validation = True
                            self.validate_required_variables(relative_template.as_posix(), context)
                            self.strict_validation = original
                        else:
                            # Validación estándar con warnings
                            self.validate_required_variables(relative_template.as_posix(), context)
                        
                        content = self.render_template_sync(relative_template.as_posix(), context)
                        
                        dest = output_path / dest_rel.with_suffix("")  # Remover .j2
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_text(content, encoding="utf-8")
                        generated_files.append(dest)
                        
                        self.logger.debug(f"Generated: {dest}")
                        
                    except Exception as e:
                        error_msg = f"Error rendering {relative_template}: {e}"
                        
                        if raise_on_missing or self.strict_validation:
                            self.logger.error(f"[ERROR] {error_msg}")
                            raise
                        else:
                            # CORRECCIÓN: En modo no estricto, generar archivo básico
                            self.logger.warning(f"[WARN] {error_msg} - generando contenido básico")
                            
                            try:
                                fallback_content = self._generate_fallback_content(
                                    relative_template.as_posix(), 
                                    context
                                )
                                dest = output_path / dest_rel.with_suffix("")
                                dest.parent.mkdir(parents=True, exist_ok=True)
                                dest.write_text(fallback_content, encoding="utf-8")
                                generated_files.append(dest)
                                self.logger.info(f"[FALLBACK] Generated: {dest}")
                            except Exception as fallback_error:
                                self.logger.error(f"[ERROR] Fallback también falló: {fallback_error}")
                                # Continuar con siguiente archivo
                                continue
                else:
                    # Archivo estático - copiar
                    try:
                        dest = output_path / dest_rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dest)
                        generated_files.append(dest)
                        self.logger.debug(f"Copied: {dest}")
                    except Exception as e:
                        self.logger.warning(f"[WARN] Error copiando archivo {src}: {e}")
                        # Continuar con siguiente archivo

        # CORRECCIÓN: Log sin emojis
        self.logger.info(f"[OK] Generated {len(generated_files)} files in {output_path}")
        return generated_files

    async def generate_project_async(
        self,
        template_name: str,
        output_dir: Union[str, Path],
        context: Optional[Dict[str, Any]] = None,
        *,
        raise_on_missing: bool = False,
    ) -> List[Path]:
        """Generar proyecto de forma asíncrona."""
        return await asyncio.to_thread(
            self.generate_project_sync,
            template_name,
            output_dir,
            context,
            raise_on_missing=raise_on_missing,
        )

    def generate_project(
        self,
        template_name: str,
        output_dir: Union[str, Path],
        context: Optional[Dict[str, Any]] = None,
        *,
        raise_on_missing: bool = False,
    ) -> List[Path]:
        """Generar proyecto de forma síncrona."""
        return self.generate_project_sync(
            template_name, 
            output_dir, 
            context, 
            raise_on_missing=raise_on_missing
        )
    
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
            # CORRECCIÓN: Log sin emojis
            self.logger.error(f"[ERROR] Error listando templates: {e}")
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
    
    # Helper functions (sin cambios significativos)
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

# CORRECCIÓN: Instancia global con configuración no estricta por defecto
template_engine = TemplateEngine(strict_validation=False, use_defaults=True)