#!/usr/bin/env python3
"""
Complete PromptSuite example with JSON files
Shows all available functions
"""
from prompt_suite import PromptSuite
import os

def main():
    print("🚀 PromptSuite - Complete Example with JSON")
    print("=" * 50)
    
    # JSON file for this example
    json_file = "example_prompts.json"
    
    # Initialize PromptSuite with JSON file
    ps = PromptSuite(json_file)
    
    print(f"✅ PromptSuite initialized with: {ps.source_info}")
    
    # ===== 1. CREATE PROMPTS =====
    print("\n📝 1. CREATE PROMPTS")
    print("-" * 20)
    
    # Create basic prompt
    ps.create_prompt(
        name="greeting",
        model_name="gpt-4",
        content="Hello {name}, how are you?",
        parameters=["name"]
    )
    print("✅ Prompt 'greeting' created")
    
    # Create prompt with default model
    ps.create_prompt(
        name="analysis",
        model_name="claude",
        content="Analyze the following text: {text}",
        parameters=["text"],
        default_model="claude"
    )
    print("✅ Prompt 'analysis' created")
    
    # Create complex prompt
    ps.create_prompt(
        name="translation",
        model_name="gpt-4",
        content="Translate '{text}' from {source_language} to {target_language}",
        parameters=["text", "source_language", "target_language"]
    )
    print("✅ Prompt 'translation' created")
    
    # ===== 2. ADD MODELS =====
    print("\n➕ 2. ADD MODELS")
    print("-" * 20)
    
    # Add additional model to 'greeting' prompt
    ps.add_model(
        name="greeting",
        model_name="claude",
        content="Hi {name}! How are you doing?",
        parameters=["name"]
    )
    print("✅ Model 'claude' added to 'greeting'")
    
    # Add additional model to 'analysis' prompt
    ps.add_model(
        name="analysis",
        model_name="gpt-4",
        content="Perform a detailed analysis of: {text}",
        parameters=["text"]
    )
    print("✅ Model 'gpt-4' added to 'analysis'")
    
    # ===== 3. BUILD PROMPTS =====
    print("\n🔨 3. BUILD PROMPTS")
    print("-" * 20)
    
    # Build with default model
    greeting_gpt = ps.build_prompt("greeting", {"name": "John"})
    print(f"GPT-4 Greeting: {greeting_gpt}")
    
    # Build with specific model
    greeting_claude = ps.build_prompt("greeting", {"name": "Mary"}, model_name="claude")
    print(f"Claude Greeting: {greeting_claude}")
    
    # Build analysis prompt
    analysis = ps.build_prompt("analysis", {"text": "This is a test text to analyze"})
    print(f"Analysis: {analysis}")
    
    # Build translation prompt
    translation = ps.build_prompt("translation", {
        "text": "Hello world",
        "source_language": "English",
        "target_language": "Spanish"
    })
    print(f"Translation: {translation}")
    
    # ===== 4. GET INFORMATION =====
    print("\n📊 4. GET INFORMATION")
    print("-" * 20)
    
    # List all prompts
    prompts = ps.list_prompts()
    print(f"Available prompts: {prompts}")
    
    # Get information of a specific prompt
    greeting_info = ps.get_prompt_info("greeting")
    print(f"Info for prompt 'greeting':")
    print(f"  - Models: {list(greeting_info['models'].keys())}")
    print(f"  - Default model: {greeting_info['default_model']}")
    
    # Get complete prompt
    complete_prompt = ps.get_prompt("greeting")
    print(f"Complete prompt 'greeting': {complete_prompt}")
    
    # ===== 5. UPDATE PROMPTS =====
    print("\n✏️ 5. UPDATE PROMPTS")
    print("-" * 20)
    
    # Update default model
    ps.update_model(
        name="greeting",
        model_name="gpt-4",
        content="Hello {name}! How are you doing?",
        parameters=["name"]
    )
    print("✅ Model 'gpt-4' of 'greeting' updated")
    
    # Update prompt (change name)
    ps.update_prompt("greeting", new_name="updated_greeting")
    print("✅ Prompt 'greeting' renamed to 'updated_greeting'")
    
    # Test the updated prompt
    updated_greeting = ps.build_prompt("updated_greeting", {"name": "Carlos"})
    print(f"Updated greeting: {updated_greeting}")
    
    # ===== 6. HISTORY AND BACKUP =====
    print("\n📚 6. HISTORY AND BACKUP")
    print("-" * 20)
    
    # Create backup
    backup_path = ps.backup("backup_prompts.json")
    print(f"✅ Backup created at: {backup_path}")
    
    # Get history (if exists)
    try:
        history = ps.get_history()
        print(f"History: {len(history)} entries")
    except:
        print("No history available")
    
    # ===== 7. DELETE ELEMENTS =====
    print("\n🗑️ 7. DELETE ELEMENTS")
    print("-" * 20)
    
    # Delete specific model
    ps.remove_model("updated_greeting", "claude")
    print("✅ Model 'claude' deleted from 'updated_greeting'")
    
    # Delete complete prompt
    ps.delete_prompt("translation")
    print("✅ Prompt 'translation' deleted")
    
    # List prompts after deletions
    final_prompts = ps.list_prompts()
    print(f"Final prompts: {final_prompts}")
    
    # ===== 8. RESTORE FROM BACKUP =====
    print("\n🔄 8. RESTORE FROM BACKUP")
    print("-" * 20)
    
    # Restore prompt from backup
    ps.restore_prompt("translation", "backup_prompts.json")
    print("✅ Prompt 'translation' restored from backup")
    
    # Verify restoration
    restored_translation = ps.build_prompt("translation", {
        "text": "Good morning",
        "source_language": "English",
        "target_language": "Spanish"
    })
    print(f"Restored translation: {restored_translation}")
    
    # ===== 9. FINAL INFORMATION =====
    print("\n📋 9. FINAL INFORMATION")
    print("-" * 20)
    
    print(f"JSON file: {ps.file_info}")
    print(f"Final prompts: {ps.list_prompts()}")
    
    # Show JSON file content
    print(f"\n📄 JSON file content:")
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    print("\n🎉 JSON example completed successfully!")

if __name__ == "__main__":
    main()
