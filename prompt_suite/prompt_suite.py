"""
Clase principal PromptSuite - Sistema de gestión de prompts con control de versiones
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .core.utils import detect_file_format, validate_file_path
from .core.models import Prompt, PromptModel
from .core.exceptions import (
    PromptSuiteError,
    ValidationError,
    PromptNotFoundError,
    ModelNotFoundError,
    HistoryError
)
from .handlers import get_json_handler, get_yaml_handler, get_plugins_handler


class PromptSuite:
    """
    Sistema de gestión de prompts con control de versiones.
    
    Soporta archivos JSON, YAML y plugins para funciones Python externas.
    """
    
    def __init__(self, source: Union[str, 'PluginConnectionHandler']):
        """
        Inicializar PromptSuite con un archivo o plugin.
        
        Args:
            source: Ruta al archivo JSON/YAML o handler de plugin
        """
        if isinstance(source, str):
            # Modo archivo (comportamiento actual)
            self.file_path = validate_file_path(source)
            self.file_format = detect_file_format(self.file_path)
            
            # Inicializar handler específico
            if self.file_format == 'json':
                JsonHandler = get_json_handler()
                self._handler = JsonHandler(self.file_path)
            elif self.file_format == 'yaml':
                YamlHandler = get_yaml_handler()
                self._handler = YamlHandler(self.file_path)
            else:
                raise ValidationError(f"Formato de archivo no soportado: {self.file_format}")
            
            self._connection_mode = False
            
        else:
            # Modo plugin - source ya es un PluginConnectionHandler
            self._handler = source
            self._connection_mode = True
    
    def create_prompt(self, name: str, model_name: str, content: str, parameters: List[str], 
                     default_model: Optional[str] = None) -> Prompt:
        """
        Crear un nuevo prompt.
        
        Args:
            name: Nombre único del prompt
            model_name: Nombre del modelo de IA
            content: Contenido del prompt con placeholders {variable}
            parameters: Lista de parámetros requeridos
            default_model: Modelo por defecto (opcional, usa model_name si no se especifica)
        
        Returns:
            Prompt creado
        
        Raises:
            ValidationError: Si el prompt ya existe o hay errores de validación
        """
        return self._handler.create_prompt(name, model_name, content, parameters, default_model)
    
    def get_prompt(self, name: str) -> Prompt:
        """
        Obtener un prompt por nombre.
        
        Args:
            name: Nombre del prompt
        
        Returns:
            Prompt encontrado
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
        """
        return self._handler.get_prompt(name)
    
    def build_prompt(self, name: str, params: Dict[str, Any], model_name: Optional[str] = None) -> str:
        """
        Construir un prompt con parámetros.
        
        Args:
            name: Nombre del prompt
            params: Diccionario con los parámetros
            model_name: Modelo específico a usar (opcional, usa el por defecto)
        
        Returns:
            Prompt construido como string
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
            MissingParameterError: Si faltan parámetros requeridos
            ExtraParameterError: Si se proporcionan parámetros extra
        """
        return self._handler.build_prompt(name, params, model_name)
    
    def update_prompt(self, name: str, new_name: Optional[str] = None, 
                     default_model: Optional[str] = None) -> Prompt:
        """
        Actualizar metadatos del prompt.
        
        Args:
            name: Nombre actual del prompt
            new_name: Nuevo nombre (opcional)
            default_model: Nuevo modelo por defecto (opcional)
        
        Returns:
            Prompt actualizado
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
            ValidationError: Si hay errores de validación
        """
        return self._handler.update_prompt(name, new_name, default_model)
    
    def update_model(self, name: str, model_name: str, content: str, parameters: List[str]) -> Prompt:
        """
        Actualizar un modelo específico dentro de un prompt.
        
        Args:
            name: Nombre del prompt
            model_name: Nombre del modelo a actualizar
            content: Nuevo contenido del prompt
            parameters: Nueva lista de parámetros
        
        Returns:
            Prompt actualizado
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
            ModelNotFoundError: Si el modelo no existe
            ValidationError: Si hay errores de validación
        """
        return self._handler.update_model(name, model_name, content, parameters)
    
    def add_model(self, name: str, model_name: str, content: str, parameters: List[str]) -> Prompt:
        """
        Agregar un nuevo modelo a un prompt existente.
        
        Args:
            name: Nombre del prompt
            model_name: Nombre del nuevo modelo
            content: Contenido del prompt para este modelo
            parameters: Lista de parámetros para este modelo
        
        Returns:
            Prompt actualizado
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
            ValidationError: Si el modelo ya existe o hay errores de validación
        """
        return self._handler.add_model(name, model_name, content, parameters)
    
    def remove_model(self, name: str, model_name: str) -> Prompt:
        """
        Eliminar un modelo de un prompt.
        
        Args:
            name: Nombre del prompt
            model_name: Nombre del modelo a eliminar
        
        Returns:
            Prompt actualizado
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
            ModelNotFoundError: Si el modelo no existe
            ValidationError: Si es el modelo por defecto
        """
        return self._handler.remove_model(name, model_name)
    
    def delete_prompt(self, name: str):
        """
        Eliminar un prompt (soft delete - se guarda en historial).
        
        Args:
            name: Nombre del prompt a eliminar
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
        """
        self._handler.delete_prompt(name)
    
    def restore_prompt(self, name: str, timestamp: Optional[str] = None) -> Prompt:
        """
        Restaurar un prompt desde el historial.
        
        Args:
            name: Nombre del prompt
            timestamp: Timestamp específico (opcional, usa la última versión si no se especifica)
        
        Returns:
            Prompt restaurado
        
        Raises:
            HistoryError: Si no hay historial o no se encuentra la versión
        """
        return self._handler.restore_prompt(name, timestamp)
    
    def get_history(self, name: Optional[str] = None, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener historial de prompts.
        
        Args:
            name: Nombre del prompt (opcional, obtiene todo el historial si no se especifica)
            model_name: Nombre del modelo (opcional, filtra por modelo si se especifica)
        
        Returns:
            Diccionario con el historial
        """
        return self._handler.get_history(name, model_name)
    
    def clear_history(self, name: Optional[str] = None):
        """
        Limpiar historial.
        
        Args:
            name: Nombre del prompt (opcional, limpia todo el historial si no se especifica)
        """
        self._handler.clear_history(name)
    
    def list_prompts(self) -> List[str]:
        """
        Listar todos los prompts disponibles.
        
        Returns:
            Lista de nombres de prompts
        """
        return self._handler.list_prompts()
    
    def backup(self) -> str:
        """
        Crear una copia de seguridad del archivo.
        
        Returns:
            Ruta del archivo de backup creado
        """
        return self._handler.backup()
    
    def set_default_model(self, name: str, model_name: str) -> Prompt:
        """
        Establecer el modelo por defecto de un prompt.
        
        Args:
            name: Nombre del prompt
            model_name: Nombre del modelo a establecer como por defecto
        
        Returns:
            Prompt actualizado
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
            ModelNotFoundError: Si el modelo no existe
        """
        return self.update_prompt(name, default_model=model_name)
    
    def get_prompt_info(self, name: str) -> Dict[str, Any]:
        """
        Obtener información detallada de un prompt.
        
        Args:
            name: Nombre del prompt
        
        Returns:
            Diccionario con información del prompt
        
        Raises:
            PromptNotFoundError: Si el prompt no existe
        """
        prompt = self.get_prompt(name)
        return {
            "nombre": prompt.nombre,
            "default_model": prompt.default_model,
            "models": list(prompt.models.keys()),
            "last_updated": prompt.last_updated.isoformat(),
            "model_details": {
                name: {
                    "parameters": model.parameters,
                    "last_updated": model.last_updated.isoformat()
                }
                for name, model in prompt.models.items()
            }
        }
    
    @property
    def source_info(self) -> Dict[str, Any]:
        """
        Obtener información de la fuente de datos.
        
        Returns:
            Diccionario con información de la fuente
        """
        if self._connection_mode:
            return {
                "mode": "connection",
                "connection_type": "external_functions"
            }
        else:
            return {
                "mode": "file",
                "file_path": self.file_path,
                "file_format": self.file_format,
                "total_prompts": len(self.list_prompts()),
                "has_history": bool(self.get_history())
            }
    
    @property
    def file_info(self) -> Dict[str, Any]:
        """
        Obtener información del archivo actual (compatibilidad).
        
        Returns:
            Diccionario con información del archivo
        """
        return self.source_info

