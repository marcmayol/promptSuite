"""
Modelos de datos para Prompt Suite
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re

from .exceptions import (
    ValidationError,
    TemplateValidationError,
    MissingParameterError,
    ExtraParameterError
)


@dataclass
class PromptModel:
    """Modelo individual dentro de un prompt"""
    content: str
    parameters: List[str]
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validar el modelo después de la inicialización"""
        self._validate_content()
        self._validate_parameters()
    
    def _validate_content(self):
        """Validar que el contenido sea una cadena no vacía"""
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValidationError("El contenido debe ser una cadena no vacía")
    
    def _validate_parameters(self):
        """Validar que los parámetros sean una lista de cadenas únicas"""
        if not isinstance(self.parameters, list):
            raise ValidationError("Los parámetros deben ser una lista")
        
        # Verificar que todos sean cadenas
        for param in self.parameters:
            if not isinstance(param, str) or not param.strip():
                raise ValidationError("Todos los parámetros deben ser cadenas no vacías")
        
        # Verificar que no haya duplicados
        if len(self.parameters) != len(set(self.parameters)):
            raise ValidationError("Los parámetros no pueden tener duplicados")
    
    def validate_template(self):
        """Validar que el contenido coincida con los parámetros declarados"""
        # Extraer variables del template
        template_vars = set(re.findall(r'\{(\w+)\}', self.content))
        declared_params = set(self.parameters)
        
        # Verificar parámetros faltantes
        missing_params = template_vars - declared_params
        if missing_params:
            raise MissingParameterError(
                f"Parámetros faltantes en la declaración: {missing_params}"
            )
        
        # Verificar parámetros extra
        extra_params = declared_params - template_vars
        if extra_params:
            raise ExtraParameterError(
                f"Parámetros extra en la declaración: {extra_params}"
            )
    
    def build(self, params: Dict[str, Any]) -> str:
        """Construir el prompt con los parámetros proporcionados"""
        # Validar que todos los parámetros requeridos estén presentes
        missing_params = set(self.parameters) - set(params.keys())
        if missing_params:
            raise MissingParameterError(
                f"Parámetros faltantes: {missing_params}"
            )
        
        # Verificar parámetros extra
        extra_params = set(params.keys()) - set(self.parameters)
        if extra_params:
            raise ExtraParameterError(
                f"Parámetros extra proporcionados: {extra_params}"
            )
        
        # Construir el prompt
        try:
            return self.content.format(**params)
        except KeyError as e:
            raise MissingParameterError(f"Parámetro faltante en template: {e}")
        except Exception as e:
            raise TemplateValidationError(f"Error al construir template: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            "content": self.content,
            "parameters": self.parameters,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptModel':
        """Crear desde diccionario"""
        return cls(
            content=data["content"],
            parameters=data["parameters"],
            last_updated=datetime.fromisoformat(data["last_updated"])
        )


@dataclass
class Prompt:
    """Prompt completo con múltiples modelos"""
    nombre: str
    models: Dict[str, PromptModel]
    default_model: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validar el prompt después de la inicialización"""
        self._validate_nombre()
        self._validate_models()
        self._validate_default_model()
    
    def _validate_nombre(self):
        """Validar que el nombre sea una cadena no vacía"""
        if not isinstance(self.nombre, str) or not self.nombre.strip():
            raise ValidationError("El nombre debe ser una cadena no vacía")
    
    def _validate_models(self):
        """Validar que haya al menos un modelo"""
        if not self.models:
            raise ValidationError("Debe haber al menos un modelo")
        
        # Validar que todos los modelos sean válidos
        for model_name, model in self.models.items():
            if not isinstance(model_name, str) or not model_name.strip():
                raise ValidationError("Los nombres de modelo deben ser cadenas no vacías")
            model.validate_template()
    
    def _validate_default_model(self):
        """Validar que el modelo por defecto exista si está especificado"""
        if self.default_model is not None:
            if self.default_model not in self.models:
                raise ValidationError(
                    f"El modelo por defecto '{self.default_model}' no existe en los modelos disponibles"
                )
    
    def get_model(self, model_name: Optional[str] = None) -> PromptModel:
        """Obtener un modelo específico o el por defecto"""
        if model_name is None:
            if self.default_model is None:
                raise ValidationError("No hay modelo por defecto especificado")
            model_name = self.default_model
        
        if model_name not in self.models:
            raise ValidationError(f"Modelo '{model_name}' no encontrado")
        
        return self.models[model_name]
    
    def build_prompt(self, params: Dict[str, Any], model_name: Optional[str] = None) -> str:
        """Construir el prompt con los parámetros proporcionados"""
        model = self.get_model(model_name)
        return model.build(params)
    
    def add_model(self, model_name: str, model: PromptModel):
        """Agregar un nuevo modelo"""
        if model_name in self.models:
            raise ValidationError(f"El modelo '{model_name}' ya existe")
        
        model.validate_template()
        self.models[model_name] = model
        self.last_updated = datetime.now()
    
    def update_model(self, model_name: str, model: PromptModel):
        """Actualizar un modelo existente"""
        if model_name not in self.models:
            raise ValidationError(f"El modelo '{model_name}' no existe")
        
        model.validate_template()
        self.models[model_name] = model
        self.last_updated = datetime.now()
    
    def remove_model(self, model_name: str):
        """Eliminar un modelo"""
        if model_name not in self.models:
            raise ValidationError(f"El modelo '{model_name}' no existe")
        
        if self.default_model == model_name:
            raise ValidationError(
                f"No se puede eliminar el modelo por defecto '{model_name}'. "
                "Cambia el modelo por defecto primero."
            )
        
        del self.models[model_name]
        self.last_updated = datetime.now()
    
    def set_default_model(self, model_name: str):
        """Establecer el modelo por defecto"""
        if model_name not in self.models:
            raise ValidationError(f"El modelo '{model_name}' no existe")
        
        self.default_model = model_name
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            "nombre": self.nombre,
            "default_model": self.default_model,
            "models": {
                name: model.to_dict() for name, model in self.models.items()
            },
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prompt':
        """Crear desde diccionario"""
        models = {
            name: PromptModel.from_dict(model_data)
            for name, model_data in data["models"].items()
        }
        
        return cls(
            nombre=data["nombre"],
            models=models,
            default_model=data.get("default_model"),
            last_updated=datetime.fromisoformat(data["last_updated"])
        )
