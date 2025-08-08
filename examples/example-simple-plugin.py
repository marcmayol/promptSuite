#!/usr/bin/env python3
"""
Ejemplo completo de PromptSuite con plugin simple basado en diccionario
Muestra todas las funciones disponibles a través de un plugin
"""
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler
from typing import Dict, Any, List, Optional

def create_simple_storage_backend():
    """
    Crear un backend simple basado en diccionario
    Esta función maneja TODO el almacenamiento de forma independiente
    PromptSuite solo recibe las funciones, no sabe nada del diccionario
    """
    
    # ===== ALMACENAMIENTO INDEPENDIENTE =====
    # Este diccionario es completamente independiente de PromptSuite
    # PromptSuite no sabe que existe, solo llama a las funciones
    storage = {
        "prompts": {},      # Almacena los prompts
        "history": [],      # Almacena el historial
        "backups": {}       # Almacena backups
    }
    
    # ===== FUNCIONES PARA PROMPTSUITE =====
    # PromptSuite solo conoce estas funciones, no el diccionario
    
    def create_prompt_func(name: str, model_name: str, content: str, 
                          parameters: List[str], default_model: Optional[str] = None):
        """Función que PromptSuite llama para crear un prompt"""
        if name in storage["prompts"]:
            raise Exception(f"Prompt '{name}' ya existe")
        
        # Crear el prompt en el diccionario
        storage["prompts"][name] = {
            "nombre": name,
            "default_model": default_model or model_name,
            "models": {
                model_name: {
                    "content": content,
                    "parameters": parameters
                }
            }
        }
        
        # Agregar al historial
        storage["history"].append({
            "action": "create",
            "prompt_name": name,
            "timestamp": "2024-01-01 12:00:00"
        })
        
        return storage["prompts"][name]
    
    def get_prompt_func(name: str):
        """Función que PromptSuite llama para obtener un prompt"""
        if name not in storage["prompts"]:
            raise Exception(f"Prompt '{name}' no encontrado")
        return storage["prompts"][name]
    
    def update_prompt_func(name: str, new_name: Optional[str] = None, 
                          default_model: Optional[str] = None):
        """Función que PromptSuite llama para actualizar un prompt"""
        if name not in storage["prompts"]:
            raise Exception(f"Prompt '{name}' no encontrado")
        
        if new_name:
            # Renombrar prompt
            storage["prompts"][new_name] = storage["prompts"].pop(name)
            storage["prompts"][new_name]["nombre"] = new_name
        
        if default_model:
            # Actualizar modelo por defecto
            target_name = new_name or name
            storage["prompts"][target_name]["default_model"] = default_model
        
        # Agregar al historial
        storage["history"].append({
            "action": "update",
            "prompt_name": name,
            "new_name": new_name,
            "timestamp": "2024-01-01 12:00:00"
        })
    
    def delete_prompt_func(name: str):
        """Función que PromptSuite llama para eliminar un prompt"""
        if name in storage["prompts"]:
            del storage["prompts"][name]
            
            # Agregar al historial
            storage["history"].append({
                "action": "delete",
                "prompt_name": name,
                "timestamp": "2024-01-01 12:00:00"
            })
    
    def list_prompts_func():
        """Función que PromptSuite llama para listar prompts"""
        return list(storage["prompts"].keys())
    
    def save_prompt_func(prompt):
        """Función que PromptSuite llama para guardar un prompt"""
        storage["prompts"][prompt.nombre] = {
            "nombre": prompt.nombre,
            "default_model": prompt.default_model,
            "models": {
                name: {
                    "content": model.content,
                    "parameters": model.parameters
                }
                for name, model in prompt.models.items()
            }
        }
        
        # Agregar al historial
        storage["history"].append({
            "action": "save",
            "prompt_name": prompt.nombre,
            "timestamp": "2024-01-01 12:00:00"
        })
    
    def get_history_func():
        """Función que PromptSuite llama para obtener historial"""
        return storage["history"]
    
    def clear_history_func():
        """Función que PromptSuite llama para limpiar historial"""
        storage["history"] = []
    
    def backup_func(backup_name: str):
        """Función que PromptSuite llama para crear backup"""
        storage["backups"][backup_name] = storage["prompts"].copy()
        return f"backup_{backup_name}"
    
    # ===== CREAR PLUGIN PARA PROMPTSUITE =====
    # PromptSuite solo recibe estas funciones, no sabe nada del diccionario
    PluginHandler = get_plugins_handler()
    handler = PluginHandler.create_connection(
        name="simple_storage_backend",
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
    
    return handler, storage  # Retornamos también storage para mostrar el estado

def main():
    print("🚀 PromptSuite - Ejemplo Completo con Plugin Simple")
    print("=" * 55)
    
    # Crear backend simple
    handler, storage = create_simple_storage_backend()
    
    # Inicializar PromptSuite con el plugin
    ps = PromptSuite(handler)
    
    print(f"✅ PromptSuite inicializado con: {ps.source_info}")
    print(f"📊 Estado inicial del storage: {len(storage['prompts'])} prompts")
    
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
    print("✅ Prompt 'saludo' creado")
    print(f"📊 Storage ahora tiene: {len(storage['prompts'])} prompts")
    
    # Crear prompt con modelo por defecto
    ps.create_prompt(
        name="analisis",
        model_name="claude",
        content="Analiza el siguiente texto: {texto}",
        parameters=["texto"],
        default_model="claude"
    )
    print("✅ Prompt 'analisis' creado")
    
    # Crear prompt complejo
    ps.create_prompt(
        name="traduccion",
        model_name="gpt-4",
        content="Traduce '{texto}' del {idioma_origen} al {idioma_destino}",
        parameters=["texto", "idioma_origen", "idioma_destino"]
    )
    print("✅ Prompt 'traduccion' creado")
    
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
    print("✅ Modelo 'claude' agregado a 'saludo'")
    
    # Agregar modelo adicional al prompt 'analisis'
    ps.add_model(
        name="analisis",
        model_name="gpt-4",
        content="Realiza un análisis detallado de: {texto}",
        parameters=["texto"]
    )
    print("✅ Modelo 'gpt-4' agregado a 'analisis'")
    
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
    print(f"Prompts disponibles: {prompts}")
    
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
    print("✅ Modelo 'gpt-4' de 'saludo' actualizado")
    
    # Actualizar prompt (cambiar nombre)
    ps.update_prompt("saludo", new_name="saludo_actualizado")
    print("✅ Prompt 'saludo' renombrado a 'saludo_actualizado'")
    
    # Probar el prompt actualizado
    saludo_actualizado = ps.build_prompt("saludo_actualizado", {"nombre": "Carlos"})
    print(f"Saludo actualizado: {saludo_actualizado}")
    
    # ===== 6. HISTORIAL Y BACKUP =====
    print("\n📚 6. HISTORIAL Y BACKUP")
    print("-" * 20)
    
    # Crear backup
    backup_path = ps.backup("backup_prompts")
    print(f"✅ Backup creado en: {backup_path}")
    
    # Obtener historial
    history = ps.get_history()
    print(f"Historial: {len(history)} entradas")
    for entry in history:
        print(f"  - {entry['action']}: {entry['prompt_name']}")
    
    # ===== 7. ELIMINAR ELEMENTOS =====
    print("\n🗑️ 7. ELIMINAR ELEMENTOS")
    print("-" * 20)
    
    # Eliminar modelo específico
    ps.remove_model("saludo_actualizado", "claude")
    print("✅ Modelo 'claude' eliminado de 'saludo_actualizado'")
    
    # Eliminar prompt completo
    ps.delete_prompt("traduccion")
    print("✅ Prompt 'traduccion' eliminado")
    
    # Listar prompts después de eliminaciones
    prompts_finales = ps.list_prompts()
    print(f"Prompts finales: {prompts_finales}")
    
    # ===== 8. RESTAURAR DESDE BACKUP =====
    print("\n🔄 8. RESTAURAR DESDE BACKUP")
    print("-" * 20)
    
    # Restaurar prompt desde backup
    ps.restore_prompt("traduccion", "backup_prompts")
    print("✅ Prompt 'traduccion' restaurado desde backup")
    
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
    
    # Mostrar estado del storage (para demostrar que es independiente)
    print(f"\n📊 Estado final del storage:")
    print(f"  - Prompts: {list(storage['prompts'].keys())}")
    print(f"  - Historial: {len(storage['history'])} entradas")
    print(f"  - Backups: {list(storage['backups'].keys())}")
    
    # Mostrar contenido del storage
    print(f"\n📄 Contenido del storage:")
    import json
    print(json.dumps(storage, indent=2, ensure_ascii=False))
    
    print("\n🎉 ¡Ejemplo de Plugin Simple completado exitosamente!")
    print("💡 Nota: PromptSuite no sabe nada del diccionario 'storage'")
    print("   Solo llama a las funciones que le proporcionamos")

if __name__ == "__main__":
    main()
