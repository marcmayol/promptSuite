# Prompt Suite

## ⚠️ ⚠️  Alpha Version - Active Development

Prompt management system with version control for JSON and YAML. Designed for high performance and minimal footprint.

## Features

- ✅ **Complete version control** with change history
- ✅ **Multiple model support** per prompt
- ✅ **Strict validation** of templates and parameters
- ✅ **High performance** with conditional imports
- ✅ **JSON and YAML support** with optimized handlers
- ✅ **Plugin system** for any Python backend
- ✅ **Soft delete** with recovery from history
- ✅ **Optional parameters** with runtime validation
- ✅ **Automatic backup** of files

## Installation

### Basic Installation
```bash
pip install prompt-suite
```

### Installation with Performance Optimizations
```bash
# For better JSON performance
pip install prompt-suite[json]

# For complete support (includes plugins)
pip install prompt-suite[full]

# For development
pip install prompt-suite[dev]
```

### Installation for Plugins
```bash
# For using plugins with databases
pip install prompt-suite[plugins]

# For plugins with APIs
pip install prompt-suite[plugins,requests]
```

## Quick Start

```python
from prompt_suite import PromptSuite

# Create instance (JSON or YAML)
ps = PromptSuite("prompts.json")

# Create a prompt
ps.create_prompt(
    name="greeting",
    model_name="gpt-4",
    content="Hello {name}, how are you?",
    parameters=["name"]
)

# Build the prompt
result = ps.build_prompt("greeting", {"name": "John"})
print(result)  # "Hello John, how are you?"
```

### Quick Start with Plugin

```python
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

# Create simple plugin
def create_simple_backend():
    storage = {"prompts": {}}
    
    def create_prompt_func(name, model_name, content, parameters, default_model=None):
        storage["prompts"][name] = {
            "name": name,
            "default_model": default_model or model_name,
            "models": {model_name: {"content": content, "parameters": parameters}}
        }
        return storage["prompts"][name]
    
    def get_prompt_func(name):
        return storage["prompts"][name]
    
    def list_prompts_func():
        return list(storage["prompts"].keys())
    
    def save_prompt_func(prompt):
        storage["prompts"][prompt.name] = {
            "name": prompt.name,
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

# Use with plugin
handler = create_simple_backend()
ps = PromptSuite(handler)

# Create and use prompts
ps.create_prompt("greeting", "gpt-4", "Hello {name}", ["name"])
result = ps.build_prompt("greeting", {"name": "John"})
print(result)  # "Hello John"
```

## Complete Examples

### 1. Create and use prompts

```python
from prompt_suite import PromptSuite

# Initialize with JSON file
ps = PromptSuite("my_prompts.json")

# Create a prompt for text analysis
ps.create_prompt(
    name="text_analysis",
    model_name="gpt-4",
    content="""
    Analyze the following text and provide:
    - Sentiment: {sentiment}
    - Main topic: {topic}
    - Summary: {summary}
    
    Text: {text}
    """,
    parameters=["sentiment", "topic", "summary", "text"]
)

# Use the prompt
result = ps.build_prompt("text_analysis", {
    "sentiment": "positive",
    "topic": "technology",
    "summary": "AI advances",
    "text": "Artificial intelligence is revolutionizing..."
})
```

### 2. Multiple models per prompt

```python
# Add another model to the same prompt
ps.add_model(
    name="text_analysis",
    model_name="claude-3",
    content="""
    You are an expert analyst. Analyze this text:
    
    Text: {text}
    Sentiment: {sentiment}
    Topic: {topic}
    """,
    parameters=["text", "sentiment", "topic"]
)

# Use specific model
result = ps.build_prompt(
    "text_analysis", 
    {"text": "Hello world", "sentiment": "neutral", "topic": "greeting"},
    model_name="claude-3"
)
```

### 3. Version control

```python
# Update a model (saved in history)
ps.update_model(
    name="text_analysis",
    model_name="gpt-4",
    content="New improved content...",
    parameters=["new_param"]
)

# View history
history = ps.get_history("text_analysis")
print(history)

# Restore previous version
ps.restore_prompt("text_analysis", timestamp="2024-01-15T10:30:00Z")
```

### 4. Prompt management

```python
# List all prompts
prompts = ps.list_prompts()
print(prompts)

# Get detailed information
info = ps.get_prompt_info("text_analysis")
print(info)

# Change name
ps.update_prompt("text_analysis", new_name="improved_analysis")

# Set default model
ps.set_default_model("improved_analysis", "claude-3")

# Delete prompt (saved in history)
ps.delete_prompt("improved_analysis")

# Restore from history
ps.restore_prompt("improved_analysis")
```

## 🔌 Plugin System

PromptSuite includes a plugin system that allows connecting to any Python backend. Plugins are completely independent and can use any storage technology.

### Plugin Features

- ✅ **Independent backend** - PromptSuite doesn't know the implementation
- ✅ **Any technology** - SQLite, PostgreSQL, Redis, APIs, etc.
- ✅ **Custom functions** - Define your own storage logic
- ✅ **Async/sync support** - Synchronous and asynchronous functions
- ✅ **Automatic validation** - Verification of required functions
- ✅ **Error handling** - Transparent integration with error system

### 5. Simple Plugin (Dictionary)

```python
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

def create_simple_backend():
    """Simple dictionary-based backend"""
    storage = {"prompts": {}, "history": []}
    
    def create_prompt_func(name, model_name, content, parameters, default_model=None):
        storage["prompts"][name] = {
            "name": name,
            "default_model": default_model or model_name,
            "models": {model_name: {"content": content, "parameters": parameters}}
        }
        return storage["prompts"][name]
    
    def get_prompt_func(name):
        if name not in storage["prompts"]:
            raise Exception(f"Prompt '{name}' not found")
        return storage["prompts"][name]
    
    def list_prompts_func():
        return list(storage["prompts"].keys())
    
    def save_prompt_func(prompt):
        storage["prompts"][prompt.name] = {
            "name": prompt.name,
            "default_model": prompt.default_model,
            "models": {
                name: {"content": model.content, "parameters": model.parameters}
                for name, model in prompt.models.items()
            }
        }
    
    # Create plugin
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

# Use the plugin
handler, storage = create_simple_backend()
ps = PromptSuite(handler)

# Create and use prompts normally
ps.create_prompt("greeting", "gpt-4", "Hello {name}", ["name"])
result = ps.build_prompt("greeting", {"name": "John"})
print(result)  # "Hello John"
```

### 6. SQLite Plugin

```python
import sqlite3
import json
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

def create_sqlite_backend():
    """SQLite-based backend"""
    db_path = "prompts.db"
    
    def init_database():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
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
            raise Exception(f"Prompt '{name}' not found")
        
        models = {}
        for model_row in models_data:
            models[model_row[1]] = {
                "content": model_row[2],
                "parameters": json.loads(model_row[3])
            }
        
        return {
            "name": prompt_data[0],
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
        
        # Update prompt
        cursor.execute(
            'UPDATE prompts SET default_model = ? WHERE name = ?',
            (prompt.default_model, prompt.name)
        )
        
        # Update models
        for model_name, model in prompt.models.items():
            cursor.execute('''
                INSERT OR REPLACE INTO models 
                (prompt_name, model_name, content, parameters) 
                VALUES (?, ?, ?, ?)
            ''', (prompt.name, model_name, model.content, json.dumps(model.parameters)))
        
        conn.commit()
        conn.close()
    
    # Create plugin
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

# Use the plugin
handler = create_sqlite_backend()
ps = PromptSuite(handler)

# Prompts are saved in SQLite
ps.create_prompt("analysis", "gpt-4", "Analyze: {text}", ["text"])
```

### 7. External API Plugin

```python
import requests
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler

def create_api_backend(api_url, api_key):
    """Backend that connects to an external API"""
    
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
            "name": prompt.name,
            "default_model": prompt.default_model,
            "models": {
                name: {"content": model.content, "parameters": model.parameters}
                for name, model in prompt.models.items()
            }
        }
        response = requests.put(f"{api_url}/prompts/{prompt.name}", json=data, headers=headers)
        response.raise_for_status()
    
    # Create plugin
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

# Use the plugin
handler = create_api_backend("https://api.example.com", "your-api-key")
ps = PromptSuite(handler)
```

### Required Functions for Plugins

To create a plugin, you must provide these mandatory functions:

- `create_prompt_func(name, model_name, content, parameters, default_model=None)`
- `get_prompt_func(name)`
- `update_prompt_func(name, new_name=None, default_model=None)`
- `delete_prompt_func(name)`
- `list_prompts_func()`
- `save_prompt_func(prompt)`

**Optional functions:**
- `get_history_func(name=None, model_name=None)`
- `clear_history_func(name=None)`
- `backup_func(backup_name)`

### Plugin Advantages

1. **Total flexibility** - Use any storage technology
2. **Independence** - PromptSuite doesn't know your implementation
3. **Scalability** - Connect to distributed databases
4. **Integration** - Connect to existing systems
5. **Performance** - Optimize according to your specific needs

## Data Structure

### Prompt JSON
```json
{
  "name": "greeting",
  "default_model": "gpt-4",
  "models": {
    "gpt-4": {
      "content": "Hello {name}, how are you?",
      "parameters": ["name"],
      "last_updated": "2024-01-15T10:30:00Z"
    },
    "claude-3": {
      "content": "Greetings {name}",
      "parameters": ["name"],
      "last_updated": "2024-01-15T11:00:00Z"
    }
  },
  "last_updated": "2024-01-15T11:00:00Z"
}
```

### Prompt YAML
```yaml
name: greeting
default_model: gpt-4
models:
  gpt-4:
    content: "Hello {name}, how are you?"
    parameters: [name]
    last_updated: "2024-01-15T10:30:00Z"
  claude-3:
    content: "Greetings {name}"
    parameters: [name]
    last_updated: "2024-01-15T11:00:00Z"
last_updated: "2024-01-15T11:00:00Z"
```

## Complete API

### PromptSuite

#### Constructor
```python
PromptSuite(file_path: str)
```

#### Main Methods

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

#### Properties
- `file_info` - Current file information

## Validations

### Templates
- Declared parameters must match template variables
- Missing or extra parameters generate errors
- Validation at write time and execution time

### Names
- Unique names for prompts
- Valid characters (no `/`, `\`, `:`, etc.)
- Default model validation

### History
- Automatic soft delete
- Recovery by timestamp
- Filtering by model

## Performance Optimizations

### Conditional Imports
```python
# Only loads what's necessary
from prompt_suite import PromptSuite  # Lazy loading of handlers
```

### Optional Dependencies
```bash
# JSON only optimized
pip install prompt-suite[json]

# YAML only
pip install prompt-suite[yaml]

# Everything optimized
pip install prompt-suite[full]
```

### Specific Handlers
- `JsonHandler` with `ujson` support
- `YamlHandler` with `CLoader` support
- No common abstraction overhead

## Error Handling

```python
from prompt_suite import (
    PromptSuiteError,
    ValidationError,
    PromptNotFoundError,
    MissingParameterError,
    ExtraParameterError
)

try:
    ps.build_prompt("nonexistent", {"param": "value"})
except PromptNotFoundError:
    print("Prompt not found")

try:
    ps.build_prompt("greeting", {})  # Missing parameter
except MissingParameterError:
    print("Missing required parameter")
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Changelog

### v0.2.0 (Pre-Alpha)
- ✅ **Plugin system** for any Python backend
- ✅ **SQLite plugins** with complete database
- ✅ **External API plugins** with HTTP support
- ✅ **Simple plugins** based on dictionary
- ✅ **Async/sync support** in plugins
- ✅ **Automatic validation** of plugin functions

### v0.1.0
- Initial implementation
- JSON and YAML support
- Complete version control
- Strict validations
- High performance with conditional imports

