#!/usr/bin/env python3
"""
Ejemplo completo de PromptSuite con archivos JSON
Muestra todas las funciones disponibles
"""
from prompt_suite import PromptSuite
import os

def main():
    print("🚀 PromptSuite - Ejemplo Completo con JSON")
    print("=" * 50)
    
    # Archivo JSON para este ejemplo
    json_file = "example_prompts.json"
    
    # Inicializar PromptSuite con archivo JSON
    ps = PromptSuite(json_file)
    
    print(f"✅ PromptSuite inicializado con: {ps.source_info}")
    
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
    backup_path = ps.backup("backup_prompts.json")
    print(f"✅ Backup creado en: {backup_path}")
    
    # Obtener historial (si existe)
    try:
        history = ps.get_history()
        print(f"Historial: {len(history)} entradas")
    except:
        print("No hay historial disponible")
    
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
    ps.restore_prompt("traduccion", "backup_prompts.json")
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
    
    print(f"Archivo JSON: {ps.file_info}")
    print(f"Prompts finales: {ps.list_prompts()}")
    
    # Mostrar contenido del archivo JSON
    print(f"\n📄 Contenido del archivo JSON:")
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    print("\n🎉 ¡Ejemplo JSON completado exitosamente!")

if __name__ == "__main__":
    main()
