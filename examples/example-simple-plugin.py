#!/usr/bin/env python3
"""
Complete PromptSuite example with simple dictionary-based plugin
Shows all available functions through a plugin
"""
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler
from typing import Dict, Any, List, Optional

def create_simple_storage_backend():
    """
    Create a simple dictionary-based backend
    This function handles ALL storage independently
    PromptSuite only receives the functions, knows nothing about the dictionary
    """
    
    # ===== INDEPENDENT STORAGE =====
    # This dictionary is completely independent of PromptSuite
    # PromptSuite doesn't know it exists, only calls the functions
    storage = {
        "prompts": {},      # Stores prompts
        "history": [],      # Stores history
        "backups": {}       # Stores backups
    }
    
    # ===== FUNCTIONS FOR PROMPTSUITE =====
    # PromptSuite only knows these functions, not the dictionary
    
    def create_prompt_func(name: str, model_name: str, content: str, 
                          parameters: List[str], default_model: Optional[str] = None):
        """Function that PromptSuite calls to create a prompt"""
        if name in storage["prompts"]:
            raise Exception(f"Prompt '{name}' already exists")
        
        # Create prompt in dictionary
        storage["prompts"][name] = {
            "name": name,
            "default_model": default_model or model_name,
            "models": {
                model_name: {
                    "content": content,
                    "parameters": parameters
                }
            }
        }
        
        # Add to history
        storage["history"].append({
            "action": "create",
            "prompt_name": name,
            "timestamp": "2024-01-01 12:00:00"
        })
        
        return storage["prompts"][name]
    
    def get_prompt_func(name: str):
        """Function that PromptSuite calls to get a prompt"""
        if name not in storage["prompts"]:
            raise Exception(f"Prompt '{name}' not found")
        return storage["prompts"][name]
    
    def update_prompt_func(name: str, new_name: Optional[str] = None, 
                          default_model: Optional[str] = None):
        """Function that PromptSuite calls to update a prompt"""
        if name not in storage["prompts"]:
            raise Exception(f"Prompt '{name}' not found")
        
        if new_name:
            # Rename prompt
            storage["prompts"][new_name] = storage["prompts"].pop(name)
            storage["prompts"][new_name]["name"] = new_name
        
        if default_model:
            # Update default model
            target_name = new_name or name
            storage["prompts"][target_name]["default_model"] = default_model
        
        # Add to history
        storage["history"].append({
            "action": "update",
            "prompt_name": name,
            "new_name": new_name,
            "timestamp": "2024-01-01 12:00:00"
        })
    
    def delete_prompt_func(name: str):
        """Function that PromptSuite calls to delete a prompt"""
        if name in storage["prompts"]:
            del storage["prompts"][name]
            
            # Add to history
            storage["history"].append({
                "action": "delete",
                "prompt_name": name,
                "timestamp": "2024-01-01 12:00:00"
            })
    
    def list_prompts_func():
        """Function that PromptSuite calls to list prompts"""
        return list(storage["prompts"].keys())
    
    def save_prompt_func(prompt):
        """Function that PromptSuite calls to save a prompt"""
        storage["prompts"][prompt.name] = {
            "name": prompt.name,
            "default_model": prompt.default_model,
            "models": {
                name: {
                    "content": model.content,
                    "parameters": model.parameters
                }
                for name, model in prompt.models.items()
            }
        }
        
        # Add to history
        storage["history"].append({
            "action": "save",
            "prompt_name": prompt.name,
            "timestamp": "2024-01-01 12:00:00"
        })
    
    def get_history_func():
        """Function that PromptSuite calls to get history"""
        return storage["history"]
    
    def clear_history_func():
        """Function that PromptSuite calls to clear history"""
        storage["history"] = []
    
    def backup_func(backup_name: str):
        """Function that PromptSuite calls to create backup"""
        storage["backups"][backup_name] = storage["prompts"].copy()
        return f"backup_{backup_name}"
    
    # ===== CREATE PLUGIN FOR PROMPTSUITE =====
    # PromptSuite only receives these functions, knows nothing about the dictionary
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
    
    return handler, storage  # We also return storage to show the state

def main():
    print("🚀 PromptSuite - Complete Example with Simple Plugin")
    print("=" * 55)
    
    # Create simple backend
    handler, storage = create_simple_storage_backend()
    
    # Initialize PromptSuite with the plugin
    ps = PromptSuite(handler)
    
    print(f"✅ PromptSuite initialized with: {ps.source_info}")
    print(f"📊 Initial storage state: {len(storage['prompts'])} prompts")
    
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
    print(f"📊 Storage now has: {len(storage['prompts'])} prompts")
    
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
    backup_path = ps.backup("backup_prompts")
    print(f"✅ Backup created at: {backup_path}")
    
    # Get history
    history = ps.get_history()
    print(f"History: {len(history)} entries")
    for entry in history:
        print(f"  - {entry['action']}: {entry['prompt_name']}")
    
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
    ps.restore_prompt("translation", "backup_prompts")
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
    
    print(f"Plugin: {ps.source_info}")
    print(f"Final prompts: {ps.list_prompts()}")
    
    # Show storage state (to demonstrate it's independent)
    print(f"\n📊 Final storage state:")
    print(f"  - Prompts: {list(storage['prompts'].keys())}")
    print(f"  - History: {len(storage['history'])} entries")
    print(f"  - Backups: {list(storage['backups'].keys())}")
    
    # Show storage content
    print(f"\n📄 Storage content:")
    import json
    print(json.dumps(storage, indent=2, ensure_ascii=False))
    
    print("\n🎉 Simple Plugin example completed successfully!")
    print("💡 Note: PromptSuite knows nothing about the 'storage' dictionary")
    print("   It only calls the functions we provide")

if __name__ == "__main__":
    main()
