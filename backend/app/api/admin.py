"""
Admin API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
import os
import sys
import numpy as np
import json
from pathlib import Path

from app.database import get_db
from app.models import Interaction
from app.config import settings
from app.ml.model_loader import model_loader

router = APIRouter(prefix="/api/admin", tags=["admin"])


def train_als_model_background():
    """Background task to train ALS model"""
    try:
        print("🔄 Starting ALS model retraining...")
        print("=" * 50)
        
        # Import training functions
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from scripts.ml.train_als import (
            load_interactions,
            build_user_item_matrix,
            train_als_model,
            save_model_artifacts
        )
        
        # Load interactions
        print("📊 Step 1: Loading interactions from database...")
        interactions = load_interactions()
        
        if not interactions:
            print("❌ No interactions found")
            return {"success": False, "message": "No interactions found"}
        
        print(f"✅ Loaded {len(interactions)} interactions")
        
        # Build user-item matrix
        print("🔢 Step 2: Building user-item matrix...")
        matrix, user_id_to_idx, item_id_to_idx, idx_to_user_id, idx_to_item_id = build_user_item_matrix(interactions)
        print(f"✅ Matrix built: {matrix.shape[0]} users, {matrix.shape[1]} items")
        
        # Train ALS model
        print("🤖 Step 3: Training ALS model...")
        model = train_als_model(matrix)
        print("✅ ALS model training completed")
        
        # Save artifacts
        print("💾 Step 4: Saving model artifacts...")
        save_model_artifacts(model, user_id_to_idx, item_id_to_idx, idx_to_user_id, idx_to_item_id)
        print("✅ Model artifacts saved")
        
        # Convert UUIDs to strings for JSON serialization in mappings
        print("📝 Step 5: Saving mappings as JSON...")
        mappings = {
            "user_id_to_idx": {str(k): int(v) for k, v in user_id_to_idx.items()},
            "item_id_to_idx": {str(k): int(v) for k, v in item_id_to_idx.items()},
            "idx_to_user_id": {int(k): str(v) for k, v in idx_to_user_id.items()},
            "idx_to_item_id": {int(k): str(v) for k, v in idx_to_item_id.items()}
        }
        
        # Save mappings as JSON
        mappings_path = "artifacts/als_mappings.json"
        os.makedirs("artifacts", exist_ok=True)
        with open(mappings_path, 'w') as f:
            json.dump(mappings, f, indent=2)
        print(f"✅ Saved mappings to {mappings_path}")
        
        print("=" * 50)
        print("🎉 ALS model retraining completed successfully!")
        print(f"📊 Final stats: {len(user_id_to_idx)} users, {len(item_id_to_idx)} items")
        return {"success": True, "message": "ALS model retrained successfully"}
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Error retraining ALS model: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return {"success": False, "message": f"Error: {str(e)}"}


@router.post("/retrain-als")
async def retrain_als_model(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Retrain ALS model with updated interactions data and reload it"""
    try:
        # Check if interactions exist
        interaction_count = db.query(Interaction).count()
        if interaction_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No interactions found. Please generate some interactions first."
            )
        
        # Add background task to train model
        background_tasks.add_task(train_als_model_background)
        
        return {
            "success": True,
            "message": "ALS model retraining started in background",
            "interaction_count": interaction_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start retraining: {str(e)}")


@router.post("/reload-als-model")
async def reload_als_model():
    """Reload the ALS model into memory"""
    try:
        print("🔄 Admin API: Reload ALS model request received")
        print("🔄 Reloading ALS model...")
        
        # Reload ALS factors
        model_loader._load_als_factors()
        
        users_count = model_loader.user_factors.shape[0] if model_loader.user_factors is not None else 0
        items_count = model_loader.item_factors.shape[0] if model_loader.item_factors is not None else 0
        
        print(f"✅ ALS model reloaded successfully: {users_count} users, {items_count} items")
        
        return {
            "success": True,
            "message": "ALS model reloaded successfully",
            "users_count": users_count,
            "items_count": items_count
        }
        
    except Exception as e:
        print(f"❌ Admin API: Error reloading model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")


@router.post("/retrain-and-reload-als")
async def retrain_and_reload_als(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Retrain ALS model and then reload it"""
    try:
        print("🚀 Admin API: Retrain and reload request received")
        
        # Check if interactions exist
        interaction_count = db.query(Interaction).count()
        print(f"📊 Found {interaction_count} interactions in database")
        
        if interaction_count == 0:
            print("❌ No interactions found")
            raise HTTPException(
                status_code=400,
                detail="No interactions found. Please generate some interactions first."
            )
        
        def retrain_and_reload():
            print("🔄 Background task: Starting retrain and reload process...")
            result = train_als_model_background()
            if result.get("success"):
                print("🔄 Background task: Reloading model into memory...")
                try:
                    model_loader._load_als_factors()
                    print("✅ Background task: Model retrained and reloaded successfully!")
                except Exception as e:
                    print(f"❌ Background task: Error reloading model: {e}")
                    result["reload_error"] = str(e)
            else:
                print(f"❌ Background task: Retraining failed: {result.get('message')}")
            return result
        
        # Add background task
        print("📋 Adding background task to queue...")
        background_tasks.add_task(retrain_and_reload)
        
        print("✅ Background task queued successfully")
        return {
            "success": True,
            "message": "ALS model retraining and reload started in background",
            "interaction_count": interaction_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Admin API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start retraining: {str(e)}")


@router.get("/model-status")
async def get_model_status():
    """Get current model status"""
    try:
        print("🔍 Admin API: Model status request received")
        
        status = {
            "faiss_loaded": model_loader.faiss_index is not None,
            "sentence_transformer_loaded": model_loader.sentence_transformer is not None,
            "als_loaded": model_loader.user_factors is not None and model_loader.item_factors is not None,
            "als_users_count": model_loader.user_factors.shape[0] if model_loader.user_factors is not None else 0,
            "als_items_count": model_loader.item_factors.shape[0] if model_loader.item_factors is not None else 0,
        }
        
        print(f"📊 Model status: FAISS={status['faiss_loaded']}, ST={status['sentence_transformer_loaded']}, ALS={status['als_loaded']}")
        if status['als_loaded']:
            print(f"👥 ALS details: {status['als_users_count']} users, {status['als_items_count']} items")
        
        return status
    except Exception as e:
        print(f"❌ Admin API: Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

