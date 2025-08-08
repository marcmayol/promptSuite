# Prompt Suite

## ⚠️ ⚠️  Versión Alpha - En desarrollo activo

Sistema de gestión de prompts con control de versiones para JSON y YAML. Diseñado para alto rendimiento y mínimo peso.

## Características

- ✅ **Control de versiones completo** con historial de cambios
- ✅ **Soporte para múltiples modelos** por prompt
- ✅ **Validación estricta** de templates y parámetros
- ✅ **Alto rendimiento** con imports condicionales
- ✅ **Soporte JSON y YAML** con handlers optimizados
- ✅ **Sistema de plugins** para cualquier backend Python
- ✅ **Soft delete** con recuperación desde historial
- ✅ **Parámetros opcionales** con validación en runtime
- ✅ **Backup automático** de archivos

## Instalación

### Instalación básica
```bash
pip install prompt-suite
```

### Instalación con optimizaciones de rendimiento
```bash
# Para mejor rendimiento JSON
pip install prompt-suite[json]

# Para soporte completo (incluye plugins)
pip install prompt-suite[full]

# Para desarrollo
pip install prompt-suite[dev]
```

### Instalación para plugins
```bash
# Para usar plugins con bases de datos
pip install prompt-suite[plugins]

# Para plugins con APIs
pip install prompt-suite[plugins,requests]
```

## Uso Rápido

```python
from prompt_suite import PromptSuite

# Crear instancia (JSON o YAML)
ps = PromptSuite("prompts.json")

# Crear un prompt
ps.create_prompt(
    name="saludo",
    model_name="gpt-4",
    content="Hola {name}, ¿cómo estás?",
    parameters=["name"]
)

# Construir el prompt
resultado = ps.build_prompt("saludo", {"name": "Juan"})
print(resultado)  # "Hola Juan, ¿cómo estás?"
```

### Uso Rápido con Plugin

```python
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

# Crear plugin simple
def create_simple_backend():
    storage = {"prompts": {}}
    
    def create_prompt_func(name, model_name, content, parameters, default_model=None):
        storage["prompts"][name] = {
            "nombre": name,
            "default_model": default_model or model_name,
            "models": {model_name: {"content": content, "parameters": parameters}}
        }
        return storage["prompts"][name]
    
    def get_prompt_func(name):
        return storage["prompts"][name]
    
    def list_prompts_func():
        return list(storage["prompts"].keys())
    
    def save_prompt_func(prompt):
        storage["prompts"][prompt.nombre] = {
            "nombre": prompt.nombre,
            "default_model": prompt.default_model,
            "models": {
                name: {"content": model.content, "parameters": model.parameters}
                for name, model in prompt.models.items()
            }
        }
    
    PluginHandler = get_plugins_handler()
    return PluginHandler.create_connection(
        name="simple_backend",
        create_prompt_func=create_prompt_func,
        get_prompt_func=get_prompt_func,
        update_prompt_func=lambda name, new_name=None, default_model=None: None,
        delete_prompt_func=lambda name: storage["prompts"].pop(name, None),
        list_prompts_func=list_prompts_func,
        save_prompt_func=save_prompt_func
    )

# Usar con plugin
handler = create_simple_backend()
ps = PromptSuite(handler)

# Crear y usar prompts
ps.create_prompt("saludo", "gpt-4", "Hola {nombre}", ["nombre"])
resultado = ps.build_prompt("saludo", {"nombre": "Juan"})
print(resultado)  # "Hola Juan"
```

## Ejemplos Completos

### 1. Crear y usar prompts

```python
from prompt_suite import PromptSuite

# Inicializar con archivo JSON
ps = PromptSuite("my_prompts.json")

# Crear un prompt para análisis de texto
ps.create_prompt(
    name="analisis_texto",
    model_name="gpt-4",
    content="""
    Analiza el siguiente texto y proporciona:
    - Sentimiento: {sentiment}
    - Tema principal: {topic}
    - Resumen: {summary}
    
    Texto: {text}
    """,
    parameters=["sentiment", "topic", "summary", "text"]
)

# Usar el prompt
resultado = ps.build_prompt("analisis_texto", {
    "sentiment": "positivo",
    "topic": "tecnología",
    "summary": "avances en IA",
    "text": "La inteligencia artificial está revolucionando..."
})
```

### 2. Múltiples modelos por prompt

```python
# Agregar otro modelo al mismo prompt
ps.add_model(
    name="analisis_texto",
    model_name="claude-3",
    content="""
    Eres un analista experto. Analiza este texto:
    
    Texto: {text}
    Sentimiento: {sentiment}
    Tema: {topic}
    """,
    parameters=["text", "sentiment", "topic"]
)

# Usar modelo específico
resultado = ps.build_prompt(
    "analisis_texto", 
    {"text": "Hola mundo", "sentiment": "neutral", "topic": "saludo"},
    model_name="claude-3"
)
```

### 3. Control de versiones

```python
# Actualizar un modelo (se guarda en historial)
ps.update_model(
    name="analisis_texto",
    model_name="gpt-4",
    content="Nuevo contenido mejorado...",
    parameters=["nuevo_param"]
)

# Ver historial
historial = ps.get_history("analisis_texto")
print(historial)

# Restaurar versión anterior
ps.restore_prompt("analisis_texto", timestamp="2024-01-15T10:30:00Z")
```

### 4. Gestión de prompts

```python
# Listar todos los prompts
prompts = ps.list_prompts()
print(prompts)

# Obtener información detallada
info = ps.get_prompt_info("analisis_texto")
print(info)

# Cambiar nombre
ps.update_prompt("analisis_texto", new_name="analisis_mejorado")

# Establecer modelo por defecto
ps.set_default_model("analisis_mejorado", "claude-3")

# Eliminar prompt (se guarda en historial)
ps.delete_prompt("analisis_mejorado")

# Restaurar desde historial
ps.restore_prompt("analisis_mejorado")
```

## 🔌 Sistema de Plugins

PromptSuite incluye un sistema de plugins que permite conectar con cualquier backend Python. Los plugins son completamente independientes y pueden usar cualquier tecnología de almacenamiento.

### Características de Plugins

- ✅ **Backend independiente** - PromptSuite no conoce la implementación
- ✅ **Cualquier tecnología** - SQLite, PostgreSQL, Redis, APIs, etc.
- ✅ **Funciones personalizadas** - Define tu propia lógica de almacenamiento
- ✅ **Soporte async/sync** - Funciones síncronas y asíncronas
- ✅ **Validación automática** - Verificación de funciones requeridas
- ✅ **Manejo de errores** - Integración transparente con el sistema de errores

### 5. Plugin Simple (Diccionario)

```python
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

def create_simple_backend():
    """Backend simple basado en diccionario"""
    storage = {"prompts": {}, "history": []}
    
    def create_prompt_func(name, model_name, content, parameters, default_model=None):
        storage["prompts"][name] = {
            "nombre": name,
            "default_model": default_model or model_name,
            "models": {model_name: {"content": content, "parameters": parameters}}
        }
        return storage["prompts"][name]
    
    def get_prompt_func(name):
        if name not in storage["prompts"]:
            raise Exception(f"Prompt '{name}' no encontrado")
        return storage["prompts"][name]
    
    def list_prompts_func():
        return list(storage["prompts"].keys())
    
    def save_prompt_func(prompt):
        storage["prompts"][prompt.nombre] = {
            "nombre": prompt.nombre,
            "default_model": prompt.default_model,
            "models": {
                name: {"content": model.content, "parameters": model.parameters}
                for name, model in prompt.models.items()
            }
        }
    
    # Crear plugin
    PluginHandler = get_plugins_handler()
    handler = PluginHandler.create_connection(
        name="simple_backend",
        create_prompt_func=create_prompt_func,
        get_prompt_func=get_prompt_func,
        update_prompt_func=lambda name, new_name=None, default_model=None: None,
        delete_prompt_func=lambda name: storage["prompts"].pop(name, None),
        list_prompts_func=list_prompts_func,
        save_prompt_func=save_prompt_func
    )
    
    return handler, storage

# Usar el plugin
handler, storage = create_simple_backend()
ps = PromptSuite(handler)

# Crear y usar prompts normalmente
ps.create_prompt("saludo", "gpt-4", "Hola {nombre}", ["nombre"])
resultado = ps.build_prompt("saludo", {"nombre": "Juan"})
print(resultado)  # "Hola Juan"
```

### 6. Plugin SQLite

```python
import sqlite3
import json
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

def create_sqlite_backend():
    """Backend basado en SQLite"""
    db_path = "prompts.db"
    
    def init_database():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tablas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                name TEXT PRIMARY KEY,
                default_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                prompt_name TEXT,
                model_name TEXT,
                content TEXT,
                parameters TEXT,
                PRIMARY KEY (prompt_name, model_name),
                FOREIGN KEY (prompt_name) REFERENCES prompts (name)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    init_database()
    
    def create_prompt_func(name, model_name, content, parameters, default_model=None):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO prompts (name, default_model) VALUES (?, ?)',
            (name, default_model or model_name)
        )
        
        cursor.execute(
            'INSERT INTO models (prompt_name, model_name, content, parameters) VALUES (?, ?, ?, ?)',
            (name, model_name, content, json.dumps(parameters))
        )
        
        conn.commit()
        conn.close()
    
    def get_prompt_func(name):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prompts WHERE name = ?', (name,))
        prompt_data = cursor.fetchone()
        
        cursor.execute('SELECT * FROM models WHERE prompt_name = ?', (name,))
        models_data = cursor.fetchall()
        
        conn.close()
        
        if not prompt_data:
            raise Exception(f"Prompt '{name}' no encontrado")
        
        models = {}
        for model_row in models_data:
            models[model_row[1]] = {
                "content": model_row[2],
                "parameters": json.loads(model_row[3])
            }
        
        return {
            "nombre": prompt_data[0],
            "default_model": prompt_data[1],
            "models": models
        }
    
    def list_prompts_func():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM prompts')
        prompts = [row[0] for row in cursor.fetchall()]
        conn.close()
        return prompts
    
    def save_prompt_func(prompt):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Actualizar prompt
        cursor.execute(
            'UPDATE prompts SET default_model = ? WHERE name = ?',
            (prompt.default_model, prompt.nombre)
        )
        
        # Actualizar modelos
        for model_name, model in prompt.models.items():
            cursor.execute('''
                INSERT OR REPLACE INTO models 
                (prompt_name, model_name, content, parameters) 
                VALUES (?, ?, ?, ?)
            ''', (prompt.nombre, model_name, model.content, json.dumps(model.parameters)))
        
        conn.commit()
        conn.close()
    
    # Crear plugin
    PluginHandler = get_plugins_handler()
    handler = PluginHandler.create_connection(
        name="sqlite_backend",
        create_prompt_func=create_prompt_func,
        get_prompt_func=get_prompt_func,
        update_prompt_func=lambda name, new_name=None, default_model=None: None,
        delete_prompt_func=lambda name: sqlite3.connect(db_path).execute('DELETE FROM prompts WHERE name = ?', (name,)).commit(),
        list_prompts_func=list_prompts_func,
        save_prompt_func=save_prompt_func
    )
    
    return handler

# Usar el plugin
handler = create_sqlite_backend()
ps = PromptSuite(handler)

# Los prompts se guardan en SQLite
ps.create_prompt("analisis", "gpt-4", "Analiza: {texto}", ["texto"])
```

### 7. Plugin con API Externa

```python
import requests
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

def create_api_backend(api_url, api_key):
    """Backend que conecta con una API externa"""
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    def create_prompt_func(name, model_name, content, parameters, default_model=None):
        data = {
            "name": name,
            "model_name": model_name,
            "content": content,
            "parameters": parameters,
            "default_model": default_model or model_name
        }
        response = requests.post(f"{api_url}/prompts", json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_prompt_func(name):
        response = requests.get(f"{api_url}/prompts/{name}", headers=headers)
        response.raise_for_status()
        return response.json()
    
    def list_prompts_func():
        response = requests.get(f"{api_url}/prompts", headers=headers)
        response.raise_for_status()
        return [prompt["name"] for prompt in response.json()]
    
    def save_prompt_func(prompt):
        data = {
            "name": prompt.nombre,
            "default_model": prompt.default_model,
            "models": {
                name: {"content": model.content, "parameters": model.parameters}
                for name, model in prompt.models.items()
            }
        }
        response = requests.put(f"{api_url}/prompts/{prompt.nombre}", json=data, headers=headers)
        response.raise_for_status()
    
    # Crear plugin
    PluginHandler = get_plugins_handler()
    handler = PluginHandler.create_connection(
        name="api_backend",
        create_prompt_func=create_prompt_func,
        get_prompt_func=get_prompt_func,
        update_prompt_func=lambda name, new_name=None, default_model=None: None,
        delete_prompt_func=lambda name: requests.delete(f"{api_url}/prompts/{name}", headers=headers),
        list_prompts_func=list_prompts_func,
        save_prompt_func=save_prompt_func
    )
    
    return handler

# Usar el plugin
handler = create_api_backend("https://api.ejemplo.com", "tu-api-key")
ps = PromptSuite(handler)
```

### Funciones Requeridas para Plugins

Para crear un plugin, debes proporcionar estas funciones obligatorias:

- `create_prompt_func(name, model_name, content, parameters, default_model=None)`
- `get_prompt_func(name)`
- `update_prompt_func(name, new_name=None, default_model=None)`
- `delete_prompt_func(name)`
- `list_prompts_func()`
- `save_prompt_func(prompt)`

**Funciones opcionales:**
- `get_history_func(name=None, model_name=None)`
- `clear_history_func(name=None)`
- `backup_func(backup_name)`

### Ventajas de los Plugins

1. **Flexibilidad total** - Usa cualquier tecnología de almacenamiento
2. **Independencia** - PromptSuite no conoce tu implementación
3. **Escalabilidad** - Conecta con bases de datos distribuidas
4. **Integración** - Conecta con sistemas existentes
5. **Rendimiento** - Optimiza según tus necesidades específicas

## Estructura de Datos

### Prompt JSON
```json
{
  "nombre": "saludo",
  "default_model": "gpt-4",
  "models": {
    "gpt-4": {
      "content": "Hola {name}, ¿cómo estás?",
      "parameters": ["name"],
      "last_updated": "2024-01-15T10:30:00Z"
    },
    "claude-3": {
      "content": "Saludos {name}",
      "parameters": ["name"],
      "last_updated": "2024-01-15T11:00:00Z"
    }
  },
  "last_updated": "2024-01-15T11:00:00Z"
}
```

### Prompt YAML
```yaml
nombre: saludo
default_model: gpt-4
models:
  gpt-4:
    content: "Hola {name}, ¿cómo estás?"
    parameters: [name]
    last_updated: "2024-01-15T10:30:00Z"
  claude-3:
    content: "Saludos {name}"
    parameters: [name]
    last_updated: "2024-01-15T11:00:00Z"
last_updated: "2024-01-15T11:00:00Z"
```

## API Completa

### PromptSuite

#### Constructor
```python
PromptSuite(file_path: str)
```

#### Métodos principales

- `create_prompt(name, model_name, content, parameters, default_model=None)`
- `get_prompt(name)`
- `build_prompt(name, params, model_name=None)`
- `update_prompt(name, new_name=None, default_model=None)`
- `update_model(name, model_name, content, parameters)`
- `add_model(name, model_name, content, parameters)`
- `remove_model(name, model_name)`
- `delete_prompt(name)`
- `restore_prompt(name, timestamp=None)`
- `get_history(name=None, model_name=None)`
- `clear_history(name=None)`
- `list_prompts()`
- `backup()`
- `set_default_model(name, model_name)`
- `get_prompt_info(name)`

#### Propiedades
- `file_info` - Información del archivo actual

## Validaciones

### Templates
- Los parámetros declarados deben coincidir con las variables del template
- Parámetros faltantes o extra generan errores
- Validación en tiempo de escritura y ejecución

### Nombres
- Nombres únicos para prompts
- Caracteres válidos (sin `/`, `\`, `:`, etc.)
- Validación de modelos por defecto

### Historial
- Soft delete automático
- Recuperación por timestamp
- Filtrado por modelo

## Optimizaciones de Rendimiento

### Imports Condicionales
```python
# Solo carga lo necesario
from prompt_suite import PromptSuite  # Lazy loading de handlers
```

### Dependencias Opcionales
```bash
# Solo JSON optimizado
pip install prompt-suite[json]

# Solo YAML
pip install prompt-suite[yaml]

# Todo optimizado
pip install prompt-suite[full]
```

### Handlers Específicos
- `JsonHandler` con soporte para `ujson`
- `YamlHandler` con soporte para `CLoader`
- Sin overhead de abstracción común

## Manejo de Errores

```python
from prompt_suite import (
    PromptSuiteError,
    ValidationError,
    PromptNotFoundError,
    MissingParameterError,
    ExtraParameterError
)

try:
    ps.build_prompt("inexistente", {"param": "valor"})
except PromptNotFoundError:
    print("Prompt no encontrado")

try:
    ps.build_prompt("saludo", {})  # Falta parámetro
except MissingParameterError:
    print("Falta parámetro requerido")
```

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## Changelog

### v0.2.0 (Pre-Alpha)
- ✅ **Sistema de plugins** para cualquier backend Python
- ✅ **Plugins para SQLite** con base de datos completa
- ✅ **Plugins para APIs externas** con soporte HTTP
- ✅ **Plugins simples** basados en diccionario
- ✅ **Soporte async/sync** en plugins
- ✅ **Validación automática** de funciones de plugin

### v0.1.0
- Implementación inicial
- Soporte JSON y YAML
- Control de versiones completo
- Validaciones estrictas
- Alto rendimiento con imports condicionales

