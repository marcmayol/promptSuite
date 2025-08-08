"""
Utilidades para Prompt Suite
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml

from .exceptions import FileFormatError


def detect_file_format(file_path: str) -> str:
    """Detectar el formato del archivo basado en la extensión"""
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == '.json':
        return 'json'
    elif extension in ['.yaml', '.yml']:
        return 'yaml'
    else:
        raise FileFormatError(f"Formato de archivo no soportado: {extension}")


def validate_file_path(file_path: str) -> str:
    """Validar y normalizar la ruta del archivo"""
    if not file_path or not isinstance(file_path, str):
        raise ValueError("La ruta del archivo debe ser una cadena no vacía")
    
    # Normalizar la ruta
    path = Path(file_path).resolve()
    
    # Crear el directorio si no existe
    path.parent.mkdir(parents=True, exist_ok=True)
    
    return str(path)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Cargar archivo JSON con manejo de errores"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise FileFormatError(f"Error al decodificar JSON: {e}")
    except FileNotFoundError:
        # Si el archivo no existe, crear uno vacío
        return {"prompts": {}, "history": {}}
    except Exception as e:
        raise FileFormatError(f"Error al leer archivo JSON: {e}")


def save_json_file(file_path: str, data: Dict[str, Any]):
    """Guardar archivo JSON con manejo de errores"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise FileFormatError(f"Error al guardar archivo JSON: {e}")


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """Cargar archivo YAML con manejo de errores"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise FileFormatError(f"Error al decodificar YAML: {e}")
    except FileNotFoundError:
        # Si el archivo no existe, crear uno vacío
        return {"prompts": {}, "history": {}}
    except Exception as e:
        raise FileFormatError(f"Error al leer archivo YAML: {e}")


def save_yaml_file(file_path: str, data: Dict[str, Any]):
    """Guardar archivo YAML con manejo de errores"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, default_style=None)
    except Exception as e:
        raise FileFormatError(f"Error al guardar archivo YAML: {e}")


def create_backup(file_path: str) -> str:
    """Crear una copia de seguridad del archivo"""
    path = Path(file_path)
    if not path.exists():
        return None
    
    backup_path = path.with_suffix(f"{path.suffix}.backup")
    try:
        import shutil
        shutil.copy2(path, backup_path)
        return str(backup_path)
    except Exception as e:
        raise FileFormatError(f"Error al crear backup: {e}")


def validate_prompt_name(name: str) -> str:
    """Validar el nombre del prompt"""
    if not name or not isinstance(name, str):
        raise ValueError("El nombre del prompt debe ser una cadena no vacía")
    
    name = name.strip()
    if not name:
        raise ValueError("El nombre del prompt no puede estar vacío")
    
    # Verificar caracteres válidos (opcional)
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in name:
            raise ValueError(f"El nombre del prompt no puede contener el carácter: {char}")
    
    return name


def validate_model_name(name: str) -> str:
    """Validar el nombre del modelo"""
    if not name or not isinstance(name, str):
        raise ValueError("El nombre del modelo debe ser una cadena no vacía")
    
    name = name.strip()
    if not name:
        raise ValueError("El nombre del modelo no puede estar vacío")
    
    return name


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Fusionar dos diccionarios de forma recursiva"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result
