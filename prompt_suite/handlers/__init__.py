"""
Handlers para diferentes formatos de archivo y plugins
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

def get_plugins_handler():
    """Obtener el handler de plugins de forma lazy"""
    from .plugins_handler import PluginConnectionHandler
    return PluginConnectionHandler

__all__ = ['get_json_handler', 'get_yaml_handler', 'get_plugins_handler']
