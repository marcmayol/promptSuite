#!/usr/bin/env python3
"""
Ejemplo completo de uso de Prompt Suite
"""
from prompt_suite import PromptSuite

def main():
    print("🚀 Prompt Suite - Ejemplo Completo")
    print("=" * 50)
    
    # Crear instancia con archivo JSON
    ps = PromptSuite("example_prompts.json")
    
    print(f"📁 Archivo: {ps.file_info['file_path']}")
    print(f"📊 Formato: {ps.file_info['file_format']}")
    print()
    
    # 1. Crear prompts básicos
    print("1️⃣ Creando prompts básicos...")
    
    # Prompt de saludo
    ps.create_prompt(
        name="saludo",
        model_name="gpt-4",
        content="Hola {name}, ¿cómo estás? Espero que tengas un {day_type} día.",
        parameters=["name", "day_type"]
    )
    
    # Prompt de análisis
    ps.create_prompt(
        name="analisis_texto",
        model_name="gpt-4",
        content="""
        Analiza el siguiente texto y proporciona:
        
        - Sentimiento: {sentiment}
        - Tema principal: {topic}
        - Resumen: {summary}
        - Palabras clave: {keywords}
        
        Texto a analizar: {text}
        """,
        parameters=["sentiment", "topic", "summary", "keywords", "text"]
    )
    
    print("✅ Prompts creados exitosamente")
    print()
    
    # 2. Construir prompts
    print("2️⃣ Construyendo prompts...")
    
    # Usar prompt de saludo
    saludo = ps.build_prompt("saludo", {
        "name": "Juan",
        "day_type": "excelente"
    })
    print(f"Saludo: {saludo}")
    
    # Usar prompt de análisis
    analisis = ps.build_prompt("analisis_texto", {
        "sentiment": "positivo",
        "topic": "tecnología e IA",
        "summary": "avances en inteligencia artificial",
        "keywords": "IA, machine learning, innovación",
        "text": "La inteligencia artificial está revolucionando la forma en que trabajamos y vivimos."
    })
    print(f"Análisis: {analisis[:100]}...")
    print()
    
    # 3. Agregar múltiples modelos
    print("3️⃣ Agregando múltiples modelos...")
    
    # Agregar modelo Claude al prompt de análisis
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
    analisis_claude = ps.build_prompt(
        "analisis_texto",
        {
            "text": "La tecnología avanza rápidamente",
            "sentiment": "optimista",
            "topic": "progreso tecnológico"
        },
        model_name="claude-3"
    )
    print(f"Análisis Claude: {analisis_claude}")
    print()
    
    # 4. Información de prompts
    print("4️⃣ Información de prompts...")
    
    prompts = ps.list_prompts()
    print(f"Prompts disponibles: {prompts}")
    
    info = ps.get_prompt_info("analisis_texto")
    print(f"Info del prompt 'analisis_texto':")
    print(f"  - Modelos: {info['models']}")
    print(f"  - Modelo por defecto: {info['default_model']}")
    print(f"  - Última actualización: {info['last_updated']}")
    print()
    
    # 5. Control de versiones
    print("5️⃣ Control de versiones...")
    
    # Actualizar un modelo (se guarda en historial)
    ps.update_model(
        name="analisis_texto",
        model_name="gpt-4",
        content="""
        Analiza el siguiente texto y proporciona:
        
        - Sentimiento: {sentiment}
        - Tema principal: {topic}
        - Resumen: {summary}
        - Palabras clave: {keywords}
        - Puntuación: {score}
        
        Texto a analizar: {text}
        """,
        parameters=["sentiment", "topic", "summary", "keywords", "score", "text"]
    )
    
    # Ver historial
    historial = ps.get_history("analisis_texto")
    print(f"Entradas en historial: {len(historial['analisis_texto'])}")
    
    # Ver historial por modelo
    historial_gpt4 = ps.get_history("analisis_texto", "gpt-4")
    print(f"Entradas en historial GPT-4: {len(historial_gpt4['analisis_texto'])}")
    print()
    
    # 6. Gestión de modelos por defecto
    print("6️⃣ Gestión de modelos por defecto...")
    
    # Cambiar modelo por defecto
    ps.set_default_model("analisis_texto", "claude-3")
    
    # Verificar cambio
    info_actualizada = ps.get_prompt_info("analisis_texto")
    print(f"Nuevo modelo por defecto: {info_actualizada['default_model']}")
    print()
    
    # 7. Manejo de errores (Simplificado)
    print("7️⃣ Manejo de errores...")
    
    try:
        # Intentar usar prompt inexistente
        ps.build_prompt("inexistente", {"param": "valor"})
    except Exception as e:
        print(f"❌ Error esperado: {e}")
    
    try:
        # Intentar usar parámetros faltantes
        ps.build_prompt("saludo", {"name": "Juan"})  # Falta day_type
    except Exception as e:
        print(f"❌ Error esperado: {e}")
    
    try:
        # Intentar usar parámetros extra
        ps.build_prompt("saludo", {
            "name": "Juan",
            "day_type": "bueno",
            "extra_param": "valor"
        })
    except Exception as e:
        print(f"❌ Error esperado: {e}")
    
    print()
    
    # 8. Backup y limpieza
    print("8️⃣ Backup y limpieza...")
    
    # Crear backup
    backup_path = ps.backup()
    print(f"✅ Backup creado: {backup_path}")
    
    # Limpiar historial de un prompt específico
    ps.clear_history("saludo")
    print("✅ Historial de 'saludo' limpiado")
    
    # Ver historial general
    historial_general = ps.get_history()
    print(f"Prompts con historial: {list(historial_general.keys())}")
    
    print()
    print("🎉 ¡Ejemplo completado exitosamente!")
    print(f"📁 Archivo creado: {ps.file_info['file_path']}")
    print(f"📊 Total de prompts: {ps.file_info['total_prompts']}")


if __name__ == "__main__":
    main()
