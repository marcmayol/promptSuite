# Prompt Suite

## ⚠️ ⚠️  Versión Alpha - En desarrollo activo

Sistema de gestión de prompts con control de versiones para JSON y YAML. Diseñado para alto rendimiento y mínimo peso.

## Características

- ✅ **Control de versiones completo** con historial de cambios
- ✅ **Soporte para múltiples modelos** por prompt
- ✅ **Validación estricta** de templates y parámetros
- ✅ **Alto rendimiento** con imports condicionales
- ✅ **Soporte JSON y YAML** con handlers optimizados
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

# Para soporte completo
pip install prompt-suite[full]

# Para desarrollo
pip install prompt-suite[dev]
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

### v0.1.0
- Implementación inicial
- Soporte JSON y YAML
- Control de versiones completo
- Validaciones estrictas
- Alto rendimiento con imports condicionales

