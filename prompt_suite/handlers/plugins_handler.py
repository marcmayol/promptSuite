"""
Handler de conexión para funciones Python externas
Permite conectar PromptSuite con cualquier backend Python
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
import asyncio
import inspect
from datetime import datetime

from ..core.models import Prompt, PromptModel
from ..core.exceptions import (
    PromptSuiteError,
    ValidationError,
    PromptNotFoundError,
    ModelNotFoundError
)


@dataclass
class PluginConnection:
    """Configuración de conexión a un backend"""
    name: str
    create_prompt_func: Callable
    get_prompt_func: Callable
    update_prompt_func: Callable
    delete_prompt_func: Callable
    list_prompts_func: Callable
    save_prompt_func: Callable
    get_history_func: Optional[Callable] = None
    clear_history_func: Optional[Callable] = None
    backup_func: Optional[Callable] = None
    async_support: bool = False


class PluginConnectionHandler:
    """
    Handler que conecta PromptSuite con funciones Python externas
    """
    
    @classmethod
    def create_connection(cls, name: str, **functions) -> 'PluginConnectionHandler':
        """
        Crear una conexión de plugin de forma simplificada
        
        Args:
            name: Nombre del plugin
            **functions: Funciones del backend (create_prompt_func, get_prompt_func, etc.)
        
        Returns:
            Instancia del handler configurado
        """
        # Crear la conexión
        connection = PluginConnection(name=name, **functions)
        # Retornar el handler
        return cls(connection)
    
    def __init__(self, connection: PluginConnection):
        self.connection = connection
        self._validate_connection()
    
    def _validate_connection(self):
        """Validar que la conexión tenga todas las funciones requeridas"""
        required_funcs = [
            'create_prompt_func', 'get_prompt_func', 'update_prompt_func',
            'delete_prompt_func', 'list_prompts_func', 'save_prompt_func'
        ]
        
        for func_name in required_funcs:
            func = getattr(self.connection, func_name)
            if not callable(func):
                raise ValidationError(f"La función {func_name} debe ser callable")
    
    def _call_function(self, func: Callable, *args, **kwargs) -> Any:
        """Llamar función con manejo de async/sync"""
        if self.connection.async_support and asyncio.iscoroutinefunction(func):
            # Si es async, necesitamos ejecutarlo en un event loop
            try:
                loop = asyncio.get_running_loop()
                # Si ya hay un loop corriendo, crear una tarea
                task = asyncio.create_task(func(*args, **kwargs))
                return task
            except RuntimeError:
                # No hay loop corriendo, crear uno nuevo
                return asyncio.run(func(*args, **kwargs))
        else:
            # Función síncrona
            return func(*args, **kwargs)
    
    def create_prompt(self, name: str, model_name: str, content: str, 
                     parameters: List[str], default_model: Optional[str] = None) -> Prompt:
        """Crear prompt usando función externa"""
        try:
            result = self._call_function(
                self.connection.create_prompt_func,
                name, model_name, content, parameters, default_model
            )
            
            # Si la función retorna un Prompt, usarlo directamente
            if isinstance(result, Prompt):
                return result
            
            # Si retorna un diccionario, convertirlo a Prompt
            if isinstance(result, dict):
                return self._dict_to_prompt(result)
            
            # Si retorna solo éxito, crear el Prompt localmente
            return Prompt(
                nombre=name,
                models={model_name: PromptModel(content=content, parameters=parameters)},
                default_model=default_model or model_name
            )
            
        except Exception as e:
            raise PromptSuiteError(f"Error creando prompt: {e}")
    
    def get_prompt(self, name: str) -> Prompt:
        """Obtener prompt usando función externa"""
        try:
            result = self._call_function(self.connection.get_prompt_func, name)
            
            if isinstance(result, Prompt):
                return result
            
            if isinstance(result, dict):
                return self._dict_to_prompt(result)
            
            raise PromptNotFoundError(f"Prompt '{name}' no encontrado")
            
        except Exception as e:
            raise PromptSuiteError(f"Error obteniendo prompt: {e}")
    
    def update_prompt(self, name: str, new_name: Optional[str] = None, 
                     default_model: Optional[str] = None) -> Prompt:
        """Actualizar prompt usando función externa"""
        try:
            result = self._call_function(
                self.connection.update_prompt_func,
                name, new_name, default_model
            )
            
            if isinstance(result, Prompt):
                return result
            
            if isinstance(result, dict):
                return self._dict_to_prompt(result)
            
            # Si no retorna nada, obtener el prompt actualizado
            return self.get_prompt(new_name or name)
            
        except Exception as e:
            raise PromptSuiteError(f"Error actualizando prompt: {e}")
    
    def delete_prompt(self, name: str):
        """Eliminar prompt usando función externa"""
        try:
            self._call_function(self.connection.delete_prompt_func, name)
        except Exception as e:
            raise PromptSuiteError(f"Error eliminando prompt: {e}")
    
    def list_prompts(self) -> List[str]:
        """Listar prompts usando función externa"""
        try:
            result = self._call_function(self.connection.list_prompts_func)
            
            if isinstance(result, list):
                return result
            
            # Si retorna un diccionario con prompts
            if isinstance(result, dict):
                return list(result.keys())
            
            return []
            
        except Exception as e:
            raise PromptSuiteError(f"Error listando prompts: {e}")
    
    def save_prompt(self, prompt: Prompt):
        """Guardar prompt usando función externa"""
        try:
            self._call_function(self.connection.save_prompt_func, prompt)
        except Exception as e:
            raise PromptSuiteError(f"Error guardando prompt: {e}")
    
    def get_history(self, name: Optional[str] = None, 
                   model_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtener historial usando función externa"""
        if not self.connection.get_history_func:
            return {}
        
        try:
            result = self._call_function(
                self.connection.get_history_func, name, model_name
            )
            
            if isinstance(result, dict):
                return result
            
            return {}
            
        except Exception as e:
            raise PromptSuiteError(f"Error obteniendo historial: {e}")
    
    def clear_history(self, name: Optional[str] = None):
        """Limpiar historial usando función externa"""
        if not self.connection.clear_history_func:
            return
        
        try:
            self._call_function(self.connection.clear_history_func, name)
        except Exception as e:
            raise PromptSuiteError(f"Error limpiando historial: {e}")
    
    def backup(self) -> str:
        """Crear backup usando función externa"""
        if not self.connection.backup_func:
            return "backup_not_supported"
        
        try:
            result = self._call_function(self.connection.backup_func)
            return str(result) if result else "backup_created"
        except Exception as e:
            raise PromptSuiteError(f"Error creando backup: {e}")
    
    def _dict_to_prompt(self, data: Dict[str, Any]) -> Prompt:
        """Convertir diccionario a objeto Prompt"""
        try:
            models = {}
            for model_name, model_data in data.get("models", {}).items():
                if isinstance(model_data, dict):
                    models[model_name] = PromptModel(
                        content=model_data.get("content", ""),
                        parameters=model_data.get("parameters", [])
                    )
                elif isinstance(model_data, PromptModel):
                    models[model_name] = model_data
            
            return Prompt(
                nombre=data.get("nombre", data.get("name", "")),
                models=models,
                default_model=data.get("default_model")
            )
        except Exception as e:
            raise ValidationError(f"Error convirtiendo diccionario a Prompt: {e}")
    
    def build_prompt(self, name: str, params: Dict[str, Any], 
                    model_name: Optional[str] = None) -> str:
        """Construir prompt con parámetros"""
        prompt = self.get_prompt(name)
        return prompt.build_prompt(params, model_name)
    
    def update_model(self, name: str, model_name: str, content: str, 
                    parameters: List[str]) -> Prompt:
        """Actualizar modelo específico"""
        prompt = self.get_prompt(name)
        model = PromptModel(content=content, parameters=parameters)
        prompt.update_model(model_name, model)
        self.save_prompt(prompt)
        return prompt
    
    def add_model(self, name: str, model_name: str, content: str, 
                 parameters: List[str]) -> Prompt:
        """Agregar nuevo modelo"""
        prompt = self.get_prompt(name)
        model = PromptModel(content=content, parameters=parameters)
        prompt.add_model(model_name, model)
        self.save_prompt(prompt)
        return prompt
    
    def remove_model(self, name: str, model_name: str) -> Prompt:
        """Eliminar modelo"""
        prompt = self.get_prompt(name)
        prompt.remove_model(model_name)
        self.save_prompt(prompt)
        return prompt
    
    def restore_prompt(self, name: str, timestamp: Optional[str] = None) -> Prompt:
        """Restaurar prompt desde historial"""
        # Por defecto, intentar obtener el prompt actual
        # Los backends pueden implementar su propia lógica de restauración
        return self.get_prompt(name)
