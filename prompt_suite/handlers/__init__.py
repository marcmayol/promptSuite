"""
Handlers para diferentes formatos de archivo
"""

# Imports condicionales para alto rendimiento
def get_json_handler():
    """Obtener el handler de JSON de forma lazy"""
    from .json_handler import JsonHandler
    return JsonHandler

def get_yaml_handler():
    """Obtener el handler de YAML de forma lazy"""
    from .yaml_handler import YamlHandler
    return YamlHandler

__all__ = ['get_json_handler', 'get_yaml_handler']
