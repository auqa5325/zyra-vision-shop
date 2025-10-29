#!/usr/bin/env python3
"""
List all available Gemini models via the API
"""

import os
import sys
import json

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from app.config import settings

def list_gemini_models():
    """Connect to Gemini API and list all available models"""
    
    # Get API key from settings
    api_key = settings.gemini_api_key
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set GEMINI_API_KEY in your .env file")
        return
    
    # Configure Gemini API
    print("🔌 Connecting to Gemini API...")
    genai.configure(api_key=api_key)
    print("✅ Connected successfully!\n")
    
    try:
        # List all models
        print("📋 Fetching available models...")
        models_iter = genai.list_models()
        
        # Convert to list to avoid iterator exhaustion
        models_list = list(models_iter)
        
        print(f"\n{'='*80}")
        print(f"Found {len(models_list)} available models:")
        print(f"{'='*80}\n")
        
        # Group models by type
        model_categories = {
            "generative": [],
            "embedding": [],
            "other": []
        }
        
        for model in models_list:
            model_name = model.name.replace('models/', '')
            model_info = {
                "name": model_name,
                "display_name": model.display_name,
                "description": model.description,
                "version": getattr(model, 'version', 'N/A'),
                "supported_generation_methods": getattr(model, 'supported_generation_methods', []),
                "input_token_limit": getattr(model, 'input_token_limit', None),
                "output_token_limit": getattr(model, 'output_token_limit', None),
            }
            
            # Categorize models
            if 'embedding' in model_name.lower():
                model_categories["embedding"].append(model_info)
            elif 'generate' in model_name.lower() or 'chat' in model_name.lower() or 'gemini' in model_name.lower():
                model_categories["generative"].append(model_info)
            else:
                model_categories["other"].append(model_info)
        
        # Display generative models
        if model_categories["generative"]:
            print("🤖 GENERATIVE MODELS:")
            print("-" * 80)
            for model in model_categories["generative"]:
                print(f"\n  Model: {model['name']}")
                if model['display_name']:
                    print(f"  Display Name: {model['display_name']}")
                if model['description']:
                    print(f"  Description: {model['description']}")
                if model['version']:
                    print(f"  Version: {model['version']}")
                if model['input_token_limit']:
                    print(f"  Input Token Limit: {model['input_token_limit']:,}")
                if model['output_token_limit']:
                    print(f"  Output Token Limit: {model['output_token_limit']:,}")
                if model['supported_generation_methods']:
                    print(f"  Supported Methods: {', '.join(model['supported_generation_methods'])}")
            print()
        
        # Display embedding models
        if model_categories["embedding"]:
            print("🔢 EMBEDDING MODELS:")
            print("-" * 80)
            for model in model_categories["embedding"]:
                print(f"\n  Model: {model['name']}")
                if model['display_name']:
                    print(f"  Display Name: {model['display_name']}")
                if model['description']:
                    print(f"  Description: {model['description']}")
                if model['input_token_limit']:
                    print(f"  Input Token Limit: {model['input_token_limit']:,}")
                if model['supported_generation_methods']:
                    print(f"  Supported Methods: {', '.join(model['supported_generation_methods'])}")
            print()
        
        # Display other models
        if model_categories["other"]:
            print("📦 OTHER MODELS:")
            print("-" * 80)
            for model in model_categories["other"]:
                print(f"\n  Model: {model['name']}")
                if model['display_name']:
                    print(f"  Display Name: {model['display_name']}")
                if model['description']:
                    print(f"  Description: {model['description']}")
            print()
        
        # Summary table
        print(f"\n{'='*80}")
        print("QUICK REFERENCE - MODEL NAMES:")
        print(f"{'='*80}")
        print(f"\n{'Model Name':<40} {'Type':<20}")
        print("-" * 80)
        
        for category, models_list in model_categories.items():
            if models_list:
                for model in models_list:
                    category_label = category.title()
                    print(f"{model['name']:<40} {category_label:<20}")
        
        print(f"\n{'='*80}")
        print(f"Total: {len([m for cat in model_categories.values() for m in cat])} models")
        print(f"{'='*80}\n")
        
        # JSON output option
        print("💡 Tip: To get detailed JSON output, run with --json flag")
        
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        import traceback
        traceback.print_exc()


def list_models_json():
    """List models in JSON format"""
    api_key = settings.gemini_api_key
    
    if not api_key:
        print(json.dumps({"error": "GEMINI_API_KEY not found"}))
        return
    
    genai.configure(api_key=api_key)
    
    try:
        models_iter = genai.list_models()
        models_list = []
        
        for model in models_iter:
            model_info = {
                "name": model.name.replace('models/', ''),
                "display_name": getattr(model, 'display_name', None),
                "description": getattr(model, 'description', None),
                "version": getattr(model, 'version', None),
                "supported_generation_methods": getattr(model, 'supported_generation_methods', []),
                "input_token_limit": getattr(model, 'input_token_limit', None),
                "output_token_limit": getattr(model, 'output_token_limit', None),
            }
            models_list.append(model_info)
        
        print(json.dumps(models_list, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='List all available Gemini models')
    parser.add_argument('--json', action='store_true', 
                       help='Output results in JSON format')
    args = parser.parse_args()
    
    if args.json:
        list_models_json()
    else:
        list_gemini_models()

