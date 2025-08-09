#!/usr/bin/env python3
"""
Complete PromptSuite example with SQLite-based plugin
Shows all available functions through a plugin
"""
from prompt_suite import PromptSuite
from prompt_suite.handlers import get_plugins_handler
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

def create_sqlite_backend():
    """
    Create a SQLite-based backend
    This function handles ALL storage independently
    PromptSuite only receives the functions, knows nothing about SQLite
    """
    
    # ===== DATABASE CONFIGURATION =====
    # This database is completely independent of PromptSuite
    # PromptSuite doesn't know it exists, only calls the functions
    db_path = "prompts.db"
    
    def init_database():
        """Initialize SQLite database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                name TEXT PRIMARY KEY,
                default_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Models table
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
        
        # History table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                prompt_name TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Backups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                backup_name TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Initialize database
    init_database()
    
    # ===== FUNCTIONS FOR PROMPTSUITE =====
    # PromptSuite only knows these functions, not the database
    
    def create_prompt_func(name: str, model_name: str, content: str, 
                          parameters: List[str], default_model: Optional[str] = None):
        """Function that PromptSuite calls to create a prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Insert prompt
            cursor.execute(
                'INSERT INTO prompts (name, default_model) VALUES (?, ?)',
                (name, default_model or model_name)
            )
            
            # Insert model
            cursor.execute(
                'INSERT INTO models (prompt_name, model_name, content, parameters) VALUES (?, ?, ?, ?)',
                (name, model_name, content, json.dumps(parameters))
            )
            
            # Add to history
            cursor.execute(
                'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
                ('create', name, json.dumps({'model_name': model_name, 'parameters': parameters}))
            )
            
            conn.commit()
            conn.close()
            
            return {"name": name, "default_model": default_model or model_name}
            
        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            raise Exception(f"Prompt '{name}' already exists")
    
    def get_prompt_func(name: str):
        """Function that PromptSuite calls to get a prompt"""
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
    
    def update_prompt_func(name: str, new_name: Optional[str] = None, 
                          default_model: Optional[str] = None):
        """Function that PromptSuite calls to update a prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if name not in [row[0] for row in cursor.execute('SELECT name FROM prompts')]:
            conn.close()
            raise Exception(f"Prompt '{name}' not found")
        
        if new_name:
            # Rename prompt
            cursor.execute('UPDATE prompts SET name = ? WHERE name = ?', (new_name, name))
            cursor.execute('UPDATE models SET prompt_name = ? WHERE prompt_name = ?', (new_name, name))
            
            # Add to history
            cursor.execute(
                'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
                ('rename', name, json.dumps({'new_name': new_name}))
            )
        
        if default_model:
            # Update default model
            target_name = new_name or name
            cursor.execute(
                'UPDATE prompts SET default_model = ? WHERE name = ?',
                (default_model, target_name)
            )
            
            # Add to history
            cursor.execute(
                'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
                ('update_default', target_name, json.dumps({'default_model': default_model}))
            )
        
        conn.commit()
        conn.close()
    
    def delete_prompt_func(name: str):
        """Function that PromptSuite calls to delete a prompt"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM prompts WHERE name = ?', (name,))
        
        # Add to history
        cursor.execute(
            'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
            ('delete', name, '{}')
        )
        
        conn.commit()
        conn.close()
    
    def list_prompts_func():
        """Function that PromptSuite calls to list prompts"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM prompts')
        prompts = [row[0] for row in cursor.fetchall()]
        conn.close()
        return prompts
    
    def save_prompt_func(prompt):
        """Function that PromptSuite calls to save a prompt"""
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
        
        # Add to history
        cursor.execute(
            'INSERT INTO history (action, prompt_name, details) VALUES (?, ?, ?)',
            ('save', prompt.name, json.dumps({'models': list(prompt.models.keys())}))
        )
        
        conn.commit()
        conn.close()
    
    def get_history_func():
        """Function that PromptSuite calls to get history"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM history ORDER BY timestamp DESC')
        history = []
        for row in cursor.fetchall():
            history.append({
                "id": row[0],
                "action": row[1],
                "prompt_name": row[2],
                "details": json.loads(row[3]) if row[3] else {},
                "timestamp": row[4]
            })
        conn.close()
        return history
    
    def clear_history_func():
        """Function that PromptSuite calls to clear history"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history')
        conn.commit()
        conn.close()
    
    def backup_func(backup_name: str):
        """Function that PromptSuite calls to create backup"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prompts')
        prompts_data = cursor.fetchall()
        
        backup_data = {}
        for prompt_row in prompts_data:
            name = prompt_row[0]
            default_model = prompt_row[1]
            
            cursor.execute('SELECT * FROM models WHERE prompt_name = ?', (name,))
            models_data = cursor.fetchall()
            
            models = {}
            for model_row in models_data:
                models[model_row[1]] = {
                    "content": model_row[2],
                    "parameters": json.loads(model_row[3])
                }
            
            backup_data[name] = {
                "name": name,
                "default_model": default_model,
                "models": models
            }
        
        # Save backup to database
        cursor.execute(
            'INSERT OR REPLACE INTO backups (backup_name, data) VALUES (?, ?)',
            (backup_name, json.dumps(backup_data))
        )
        
        conn.commit()
        conn.close()
        
        return f"backup_{backup_name}"
    
    # ===== CREATE PLUGIN FOR PROMPTSUITE =====
    # PromptSuite only receives these functions, knows nothing about SQLite
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
    print("🚀 PromptSuite - Complete Example with SQLite Plugin")
    print("=" * 55)
    
    # Create SQLite backend
    handler, db_path = create_sqlite_backend()
    
    # Initialize PromptSuite with the plugin
    ps = PromptSuite(handler)
    
    print(f"✅ PromptSuite initialized with: {ps.source_info}")
    print(f"🗄️ SQLite database: {db_path}")
    
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
    print("✅ Prompt 'greeting' created in SQLite")
    
    # Create prompt with default model
    ps.create_prompt(
        name="analysis",
        model_name="claude",
        content="Analyze the following text: {text}",
        parameters=["text"],
        default_model="claude"
    )
    print("✅ Prompt 'analysis' created in SQLite")
    
    # Create complex prompt
    ps.create_prompt(
        name="translation",
        model_name="gpt-4",
        content="Translate '{text}' from {source_language} to {target_language}",
        parameters=["text", "source_language", "target_language"]
    )
    print("✅ Prompt 'translation' created in SQLite")
    
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
    print("✅ Model 'claude' added to 'greeting' in SQLite")
    
    # Add additional model to 'analysis' prompt
    ps.add_model(
        name="analysis",
        model_name="gpt-4",
        content="Perform a detailed analysis of: {text}",
        parameters=["text"]
    )
    print("✅ Model 'gpt-4' added to 'analysis' in SQLite")
    
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
    print(f"Available prompts in SQLite: {prompts}")
    
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
    print("✅ Model 'gpt-4' of 'greeting' updated in SQLite")
    
    # Update prompt (change name)
    ps.update_prompt("greeting", new_name="updated_greeting")
    print("✅ Prompt 'greeting' renamed to 'updated_greeting' in SQLite")
    
    # Test the updated prompt
    updated_greeting = ps.build_prompt("updated_greeting", {"name": "Carlos"})
    print(f"Updated greeting: {updated_greeting}")
    
    # ===== 6. HISTORY AND BACKUP =====
    print("\n📚 6. HISTORY AND BACKUP")
    print("-" * 20)
    
    # Create backup
    backup_path = ps.backup("backup_prompts")
    print(f"✅ Backup created in SQLite: {backup_path}")
    
    # Get history
    history = ps.get_history()
    print(f"History in SQLite: {len(history)} entries")
    for entry in history[:5]:  # Show only first 5
        print(f"  - {entry['action']}: {entry['prompt_name']} ({entry['timestamp']})")
    
    # ===== 7. DELETE ELEMENTS =====
    print("\n🗑️ 7. DELETE ELEMENTS")
    print("-" * 20)
    
    # Delete specific model
    ps.remove_model("updated_greeting", "claude")
    print("✅ Model 'claude' deleted from 'updated_greeting' in SQLite")
    
    # Delete complete prompt
    ps.delete_prompt("translation")
    print("✅ Prompt 'translation' deleted from SQLite")
    
    # List prompts after deletions
    final_prompts = ps.list_prompts()
    print(f"Final prompts in SQLite: {final_prompts}")
    
    # ===== 8. RESTORE FROM BACKUP =====
    print("\n🔄 8. RESTORE FROM BACKUP")
    print("-" * 20)
    
    # Restore prompt from backup
    ps.restore_prompt("translation", "backup_prompts")
    print("✅ Prompt 'translation' restored from backup in SQLite")
    
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
    
    # Show database information
    print(f"\n🗄️ SQLite database information:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count records in each table
    cursor.execute('SELECT COUNT(*) FROM prompts')
    prompts_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM models')
    models_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM history')
    history_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM backups')
    backups_count = cursor.fetchone()[0]
    
    print(f"  - Prompts: {prompts_count}")
    print(f"  - Models: {models_count}")
    print(f"  - History: {history_count} entries")
    print(f"  - Backups: {backups_count}")
    
    # Show database structure
    print(f"\n📊 Database structure:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  - Tables: {tables}")
    
    conn.close()
    
    print("\n🎉 SQLite Plugin example completed successfully!")
    print("💡 Note: PromptSuite knows nothing about the SQLite database")
    print("   It only calls the functions we provide")

if __name__ == "__main__":
    main()
