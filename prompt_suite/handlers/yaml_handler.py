"""
Handler optimizado para archivos YAML
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml

# Intentar usar CLoader para mejor rendimiento
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ..core.utils import (
    load_yaml_file,
    save_yaml_file,
    create_backup,
    validate_prompt_name,
    validate_model_name
)
from ..core.models import Prompt, PromptModel
from ..core.exceptions import (
    PromptNotFoundError,
    ModelNotFoundError,
    ValidationError,
    HistoryError
)


class YamlHandler:
    """Handler optimizado para archivos YAML"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Cargar datos del archivo YAML"""
        data = load_yaml_file(self.file_path)
        
        # Asegurar estructura básica
        if "prompts" not in data:
            data["prompts"] = {}
        if "history" not in data:
            data["history"] = {}
        
        return data
    
    def _save_data(self):
        """Guardar datos al archivo YAML"""
        save_yaml_file(self.file_path, self.data)
    
    def _add_to_history(self, prompt: Prompt, action: str, model_name: Optional[str] = None):
        """Agregar entrada al historial"""
        timestamp = datetime.now().isoformat()
        
        if prompt.nombre not in self.data["history"]:
            self.data["history"][prompt.nombre] = []
        
        history_entry = {
            "timestamp": timestamp,
            "action": action,
            "prompt_data": prompt.to_dict()
        }
        
        if model_name:
            history_entry["model_name"] = model_name
        
        self.data["history"][prompt.nombre].append(history_entry)
    
    def create_prompt(self, name: str, model_name: str, content: str, parameters: List[str], 
                     default_model: Optional[str] = None) -> Prompt:
        """Crear un nuevo prompt"""
        name = validate_prompt_name(name)
        model_name = validate_model_name(model_name)
        
        if name in self.data["prompts"]:
            raise ValidationError(f"El prompt '{name}' ya existe")
        
        # Crear el modelo
        prompt_model = PromptModel(
            content=content,
            parameters=parameters
        )
        
        # Crear el prompt
        prompt = Prompt(
            nombre=name,
            models={model_name: prompt_model},
            default_model=default_model or model_name
        )
        
        # Guardar
        self.data["prompts"][name] = prompt.to_dict()
        self._add_to_history(prompt, "create")
        self._save_data()
        
        return prompt
    
    def get_prompt(self, name: str) -> Prompt:
        """Obtener un prompt por nombre"""
        name = validate_prompt_name(name)
        
        if name not in self.data["prompts"]:
            raise PromptNotFoundError(f"Prompt '{name}' no encontrado")
        
        return Prompt.from_dict(self.data["prompts"][name])
    
    def build_prompt(self, name: str, params: Dict[str, Any], model_name: Optional[str] = None) -> str:
        """Construir un prompt con parámetros"""
        prompt = self.get_prompt(name)
        return prompt.build_prompt(params, model_name)
    
    def update_prompt(self, name: str, new_name: Optional[str] = None, 
                     default_model: Optional[str] = None) -> Prompt:
        """Actualizar metadatos del prompt"""
        prompt = self.get_prompt(name)
        
        # Guardar versión anterior en historial
        self._add_to_history(prompt, "update_metadata")
        
        # Actualizar
        if new_name is not None:
            new_name = validate_prompt_name(new_name)
            if new_name != name and new_name in self.data["prompts"]:
                raise ValidationError(f"El prompt '{new_name}' ya existe")
            
            # Actualizar en datos
            self.data["prompts"][new_name] = self.data["prompts"].pop(name)
            prompt.nombre = new_name
        
        if default_model is not None:
            prompt.set_default_model(default_model)
        
        # Guardar cambios
        self.data["prompts"][prompt.nombre] = prompt.to_dict()
        self._save_data()
        
        return prompt
    
    def update_model(self, name: str, model_name: str, content: str, parameters: List[str]) -> Prompt:
        """Actualizar un modelo específico"""
        prompt = self.get_prompt(name)
        
        # Guardar versión anterior en historial
        self._add_to_history(prompt, "update_model", model_name)
        
        # Crear nuevo modelo
        new_model = PromptModel(
            content=content,
            parameters=parameters
        )
        
        # Actualizar
        prompt.update_model(model_name, new_model)
        
        # Guardar
        self.data["prompts"][name] = prompt.to_dict()
        self._save_data()
        
        return prompt
    
    def add_model(self, name: str, model_name: str, content: str, parameters: List[str]) -> Prompt:
        """Agregar un nuevo modelo a un prompt"""
        prompt = self.get_prompt(name)
        
        # Crear nuevo modelo
        new_model = PromptModel(
            content=content,
            parameters=parameters
        )
        
        # Agregar
        prompt.add_model(model_name, new_model)
        
        # Guardar
        self.data["prompts"][name] = prompt.to_dict()
        self._add_to_history(prompt, "add_model", model_name)
        self._save_data()
        
        return prompt
    
    def remove_model(self, name: str, model_name: str) -> Prompt:
        """Eliminar un modelo de un prompt"""
        prompt = self.get_prompt(name)
        
        # Guardar versión anterior en historial
        self._add_to_history(prompt, "remove_model", model_name)
        
        # Eliminar
        prompt.remove_model(model_name)
        
        # Guardar
        self.data["prompts"][name] = prompt.to_dict()
        self._save_data()
        
        return prompt
    
    def delete_prompt(self, name: str):
        """Eliminar un prompt (soft delete)"""
        prompt = self.get_prompt(name)
        
        # Agregar al historial antes de eliminar
        self._add_to_history(prompt, "delete")
        
        # Eliminar del prompt activo
        del self.data["prompts"][name]
        self._save_data()
    
    def restore_prompt(self, name: str, timestamp: Optional[str] = None) -> Prompt:
        """Restaurar un prompt desde el historial"""
        if name not in self.data["history"]:
            raise HistoryError(f"No hay historial para el prompt '{name}'")
        
        history = self.data["history"][name]
        
        if not history:
            raise HistoryError(f"El historial del prompt '{name}' está vacío")
        
        # Si no se especifica timestamp, usar la última entrada
        if timestamp is None:
            entry = history[-1]
        else:
            # Buscar por timestamp
            entry = None
            for h_entry in history:
                if h_entry["timestamp"] == timestamp:
                    entry = h_entry
                    break
            
            if entry is None:
                raise HistoryError(f"No se encontró entrada con timestamp '{timestamp}'")
        
        # Restaurar
        prompt = Prompt.from_dict(entry["prompt_data"])
        self.data["prompts"][name] = prompt.to_dict()
        self._add_to_history(prompt, "restore")
        self._save_data()
        
        return prompt
    
    def get_history(self, name: Optional[str] = None, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtener historial de prompts"""
        if name is None:
            # Todo el historial
            return self.data["history"]
        
        if name not in self.data["history"]:
            return {}
        
        history = self.data["history"][name]
        
        if model_name is None:
            return {name: history}
        
        # Filtrar por modelo
        filtered_history = [
            entry for entry in history
            if entry.get("model_name") == model_name
        ]
        
        return {name: filtered_history}
    
    def clear_history(self, name: Optional[str] = None):
        """Limpiar historial"""
        if name is None:
            # Limpiar todo el historial
            self.data["history"] = {}
        else:
            # Limpiar historial de un prompt específico
            if name in self.data["history"]:
                del self.data["history"][name]
        
        self._save_data()
    
    def list_prompts(self) -> List[str]:
        """Listar todos los prompts"""
        return list(self.data["prompts"].keys())
    
    def backup(self) -> str:
        """Crear backup del archivo"""
        return create_backup(self.file_path)
