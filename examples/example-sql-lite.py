#!/usr/bin/env python3
"""
Ejemplo completo de PromptSuite con plugin basado en SQLite
Muestra todas las funciones disponibles a través de un plugin
"""
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

def create_sqlite_backend():
    """
    Crear un backend basado en SQLite
    Esta función maneja TODO el almacenamiento de forma independiente
    PromptSuite solo recibe las funciones, no sabe nada de SQLite
    """
    
    # ===== CONFIGURACIÓN DE BASE DE DATOS =====
    # Esta base de datos es completamente independiente de PromptSuite
    # PromptSuite no sabe que existe, solo llama a las funciones
    db_path = "prompts.db"
    
    def init_database():
        """Inicializar la base de datos SQLite"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tabla de prompts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                name TEXT PRIMARY KEY,
                default_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de modelos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                prompt_name TEXT,
                model_name TEXT,
                content TEXT,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (prompt_name, model_name),
                FOREIGN KEY (prompt_name) REFERENCES prompts (name) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de historial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                prompt_name TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de backups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                backup_name TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Inicializar la base de datos
    init_database()
    
    # ===== FUNCIONES PARA PROMPTSUITE =====
    # PromptSuite solo conoce estas funciones, no la base de datos
    
    def create_prompt_func(name: str, model_name: str, content: str, 
                          parameters: List[str], default_model: Optional[str] = None):
        """Función que PromptSuite llama para crear un prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Insertar prompt
            cursor.execute(
                'INSERT INTO prompts (name, default_model) VALUES (?, ?)',
                (name, default_model or model_name)
            )
            
            # Insertar modelo
            cursor.execute(
                'INSERT INTO models (prompt_name, model_name, content, parameters) VALUES (?, ?, ?, ?)',
                (name, model_name, content, json.dumps(parameters))
            )
            
            # Registrar en historial
            cursor.execute(
                'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
                ('create', name, json.dumps({'model_name': model_name, 'content': content}))
            )
            
            conn.commit()
            
            # Retornar el prompt creado
            return get_prompt_func(name)
            
        except sqlite3.IntegrityError:
            raise Exception(f"Prompt '{name}' ya existe")
        finally:
            conn.close()
    
    def get_prompt_func(name: str):
        """Función que PromptSuite llama para obtener un prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener prompt
        cursor.execute('SELECT default_model FROM prompts WHERE name = ?', (name,))
        prompt_data = cursor.fetchone()
        
        if not prompt_data:
            raise Exception(f"Prompt '{name}' no encontrado")
        
        default_model = prompt_data[0]
        
        # Obtener modelos
        cursor.execute(
            'SELECT model_name, content, parameters FROM models WHERE prompt_name = ?',
            (name,)
        )
        models_data = cursor.fetchall()
        
        models = {}
        for model_name, content, parameters_json in models_data:
            parameters = json.loads(parameters_json)
            models[model_name] = {
                "content": content,
                "parameters": parameters
            }
        
        conn.close()
        
        return {
            "nombre": name,
            "default_model": default_model,
            "models": models
        }
    
    def update_prompt_func(name: str, new_name: Optional[str] = None, 
                          default_model: Optional[str] = None):
        """Función que PromptSuite llama para actualizar un prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if new_name:
            # Renombrar prompt
            cursor.execute(
                'UPDATE prompts SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?',
                (new_name, name)
            )
            cursor.execute(
                'UPDATE models SET prompt_name = ?, updated_at = CURRENT_TIMESTAMP WHERE prompt_name = ?',
                (new_name, name)
            )
        
        if default_model:
            # Actualizar modelo por defecto
            target_name = new_name or name
            cursor.execute(
                'UPDATE prompts SET default_model = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?',
                (default_model, target_name)
            )
        
        # Registrar en historial
        cursor.execute(
            'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
            ('update', name, json.dumps({'new_name': new_name, 'default_model': default_model}))
        )
        
        conn.commit()
        conn.close()
    
    def delete_prompt_func(name: str):
        """Función que PromptSuite llama para eliminar un prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Eliminar prompt (los modelos se eliminan automáticamente por CASCADE)
        cursor.execute('DELETE FROM prompts WHERE name = ?', (name,))
        
        # Registrar en historial
        cursor.execute(
            'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
            ('delete', name, '{}')
        )
        
        conn.commit()
        conn.close()
    
    def list_prompts_func():
        """Función que PromptSuite llama para listar prompts"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM prompts ORDER BY name')
        prompts = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return prompts
    
    def save_prompt_func(prompt):
        """Función que PromptSuite llama para guardar un prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Actualizar prompt
        cursor.execute(
            'UPDATE prompts SET default_model = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?',
            (prompt.default_model, prompt.nombre)
        )
        
        # Actualizar modelos
        for model_name, model in prompt.models.items():
            cursor.execute('''
                INSERT OR REPLACE INTO models (prompt_name, model_name, content, parameters, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (prompt.nombre, model_name, model.content, json.dumps(model.parameters)))
        
        # Registrar en historial
        cursor.execute(
            'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
            ('save', prompt.nombre, json.dumps({'models_count': len(prompt.models)}))
        )
        
        conn.commit()
        conn.close()
    
    def get_history_func():
        """Función que PromptSuite llama para obtener historial"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT action, prompt_name, details, timestamp 
            FROM history 
            ORDER BY timestamp DESC
        ''')
        
        history = []
        for action, prompt_name, details, timestamp in cursor.fetchall():
            history.append({
                "action": action,
                "prompt_name": prompt_name,
                "details": json.loads(details) if details else {},
                "timestamp": timestamp
            })
        
        conn.close()
        return history
    
    def clear_history_func():
        """Función que PromptSuite llama para limpiar historial"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM history')
        
        conn.commit()
        conn.close()
    
    def backup_func(backup_name: str):
        """Función que PromptSuite llama para crear backup"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todos los prompts
        cursor.execute('SELECT name, default_model FROM prompts')
        prompts_data = cursor.fetchall()
        
        backup_data = {}
        for name, default_model in prompts_data:
            # Obtener modelos del prompt
            cursor.execute(
                'SELECT model_name, content, parameters FROM models WHERE prompt_name = ?',
                (name,)
            )
            models_data = cursor.fetchall()
            
            models = {}
            for model_name, content, parameters_json in models_data:
                parameters = json.loads(parameters_json)
                models[model_name] = {
                    "content": content,
                    "parameters": parameters
                }
            
            backup_data[name] = {
                "nombre": name,
                "default_model": default_model,
                "models": models
            }
        
        # Guardar backup en la base de datos
        cursor.execute(
            'INSERT OR REPLACE INTO backups (backup_name, data) VALUES (?, ?)',
            (backup_name, json.dumps(backup_data))
        )
        
        conn.commit()
        conn.close()
        
        return f"backup_{backup_name}"
    
    # ===== CREAR PLUGIN PARA PROMPTSUITE =====
    # PromptSuite solo recibe estas funciones, no sabe nada de SQLite
    PluginHandler = get_plugins_handler()
    handler = PluginHandler.create_connection(
        name="sqlite_backend",
        create_prompt_func=create_prompt_func,
        get_prompt_func=get_prompt_func,
        update_prompt_func=update_prompt_func,
        delete_prompt_func=delete_prompt_func,
        list_prompts_func=list_prompts_func,
        save_prompt_func=save_prompt_func,
        get_history_func=get_history_func,
        clear_history_func=clear_history_func,
        backup_func=backup_func
    )
    
    return handler, db_path

def main():
    print("🚀 PromptSuite - Ejemplo Completo con Plugin SQLite")
    print("=" * 55)
    
    # Crear backend SQLite
    handler, db_path = create_sqlite_backend()
    
    # Inicializar PromptSuite con el plugin
    ps = PromptSuite(handler)
    
    print(f"✅ PromptSuite inicializado con: {ps.source_info}")
    print(f"🗄️ Base de datos SQLite: {db_path}")
    
    # ===== 1. CREAR PROMPTS =====
    print("\n📝 1. CREAR PROMPTS")
    print("-" * 20)
    
    # Crear prompt básico
    ps.create_prompt(
        name="saludo",
        model_name="gpt-4",
        content="Hola {nombre}, ¿cómo estás?",
        parameters=["nombre"]
    )
    print("✅ Prompt 'saludo' creado en SQLite")
    
    # Crear prompt con modelo por defecto
    ps.create_prompt(
        name="analisis",
        model_name="claude",
        content="Analiza el siguiente texto: {texto}",
        parameters=["texto"],
        default_model="claude"
    )
    print("✅ Prompt 'analisis' creado en SQLite")
    
    # Crear prompt complejo
    ps.create_prompt(
        name="traduccion",
        model_name="gpt-4",
        content="Traduce '{texto}' del {idioma_origen} al {idioma_destino}",
        parameters=["texto", "idioma_origen", "idioma_destino"]
    )
    print("✅ Prompt 'traduccion' creado en SQLite")
    
    # ===== 2. AGREGAR MODELOS =====
    print("\n➕ 2. AGREGAR MODELOS")
    print("-" * 20)
    
    # Agregar modelo adicional al prompt 'saludo'
    ps.add_model(
        name="saludo",
        model_name="claude",
        content="¡Hola {nombre}! ¿Todo bien?",
        parameters=["nombre"]
    )
    print("✅ Modelo 'claude' agregado a 'saludo' en SQLite")
    
    # Agregar modelo adicional al prompt 'analisis'
    ps.add_model(
        name="analisis",
        model_name="gpt-4",
        content="Realiza un análisis detallado de: {texto}",
        parameters=["texto"]
    )
    print("✅ Modelo 'gpt-4' agregado a 'analisis' en SQLite")
    
    # ===== 3. CONSTRUIR PROMPTS =====
    print("\n🔨 3. CONSTRUIR PROMPTS")
    print("-" * 20)
    
    # Construir con modelo por defecto
    saludo_gpt = ps.build_prompt("saludo", {"nombre": "Juan"})
    print(f"Saludo GPT-4: {saludo_gpt}")
    
    # Construir con modelo específico
    saludo_claude = ps.build_prompt("saludo", {"nombre": "María"}, model_name="claude")
    print(f"Saludo Claude: {saludo_claude}")
    
    # Construir prompt de análisis
    analisis = ps.build_prompt("analisis", {"texto": "Este es un texto de prueba para analizar"})
    print(f"Análisis: {analisis}")
    
    # Construir prompt de traducción
    traduccion = ps.build_prompt("traduccion", {
        "texto": "Hello world",
        "idioma_origen": "inglés",
        "idioma_destino": "español"
    })
    print(f"Traducción: {traduccion}")
    
    # ===== 4. OBTENER INFORMACIÓN =====
    print("\n📊 4. OBTENER INFORMACIÓN")
    print("-" * 20)
    
    # Listar todos los prompts
    prompts = ps.list_prompts()
    print(f"Prompts disponibles en SQLite: {prompts}")
    
    # Obtener información de un prompt específico
    info_saludo = ps.get_prompt_info("saludo")
    print(f"Info del prompt 'saludo':")
    print(f"  - Modelos: {list(info_saludo['models'].keys())}")
    print(f"  - Modelo por defecto: {info_saludo['default_model']}")
    
    # Obtener prompt completo
    prompt_completo = ps.get_prompt("saludo")
    print(f"Prompt completo 'saludo': {prompt_completo}")
    
    # ===== 5. ACTUALIZAR PROMPTS =====
    print("\n✏️ 5. ACTUALIZAR PROMPTS")
    print("-" * 20)
    
    # Actualizar modelo por defecto
    ps.update_model(
        name="saludo",
        model_name="gpt-4",
        content="¡Hola {nombre}! ¿Cómo te va?",
        parameters=["nombre"]
    )
    print("✅ Modelo 'gpt-4' de 'saludo' actualizado en SQLite")
    
    # Actualizar prompt (cambiar nombre)
    ps.update_prompt("saludo", new_name="saludo_actualizado")
    print("✅ Prompt 'saludo' renombrado a 'saludo_actualizado' en SQLite")
    
    # Probar el prompt actualizado
    saludo_actualizado = ps.build_prompt("saludo_actualizado", {"nombre": "Carlos"})
    print(f"Saludo actualizado: {saludo_actualizado}")
    
    # ===== 6. HISTORIAL Y BACKUP =====
    print("\n📚 6. HISTORIAL Y BACKUP")
    print("-" * 20)
    
    # Crear backup
    backup_path = ps.backup("backup_prompts")
    print(f"✅ Backup creado en SQLite: {backup_path}")
    
    # Obtener historial
    history = ps.get_history()
    print(f"Historial en SQLite: {len(history)} entradas")
    for entry in history[:5]:  # Mostrar solo las primeras 5
        print(f"  - {entry['action']}: {entry['prompt_name']} ({entry['timestamp']})")
    
    # ===== 7. ELIMINAR ELEMENTOS =====
    print("\n🗑️ 7. ELIMINAR ELEMENTOS")
    print("-" * 20)
    
    # Eliminar modelo específico
    ps.remove_model("saludo_actualizado", "claude")
    print("✅ Modelo 'claude' eliminado de 'saludo_actualizado' en SQLite")
    
    # Eliminar prompt completo
    ps.delete_prompt("traduccion")
    print("✅ Prompt 'traduccion' eliminado de SQLite")
    
    # Listar prompts después de eliminaciones
    prompts_finales = ps.list_prompts()
    print(f"Prompts finales en SQLite: {prompts_finales}")
    
    # ===== 8. RESTAURAR DESDE BACKUP =====
    print("\n🔄 8. RESTAURAR DESDE BACKUP")
    print("-" * 20)
    
    # Restaurar prompt desde backup
    ps.restore_prompt("traduccion", "backup_prompts")
    print("✅ Prompt 'traduccion' restaurado desde backup en SQLite")
    
    # Verificar restauración
    traduccion_restaurada = ps.build_prompt("traduccion", {
        "texto": "Good morning",
        "idioma_origen": "inglés",
        "idioma_destino": "español"
    })
    print(f"Traducción restaurada: {traduccion_restaurada}")
    
    # ===== 9. INFORMACIÓN FINAL =====
    print("\n📋 9. INFORMACIÓN FINAL")
    print("-" * 20)
    
    print(f"Plugin: {ps.source_info}")
    print(f"Prompts finales: {ps.list_prompts()}")
    
    # Mostrar información de la base de datos
    print(f"\n🗄️ Información de la base de datos SQLite:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Contar registros en cada tabla
    cursor.execute('SELECT COUNT(*) FROM prompts')
    prompts_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM models')
    models_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM history')
    history_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM backups')
    backups_count = cursor.fetchone()[0]
    
    print(f"  - Prompts: {prompts_count}")
    print(f"  - Modelos: {models_count}")
    print(f"  - Historial: {history_count} entradas")
    print(f"  - Backups: {backups_count}")
    
    # Mostrar estructura de la base de datos
    print(f"\n📊 Estructura de la base de datos:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  - Tablas: {tables}")
    
    conn.close()
    
    print("\n🎉 ¡Ejemplo de Plugin SQLite completado exitosamente!")
    print("💡 Nota: PromptSuite no sabe nada de la base de datos SQLite")
    print("   Solo llama a las funciones que le proporcionamos")

if __name__ == "__main__":
    main()
