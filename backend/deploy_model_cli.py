"""CLI tool for model deployment operations"""

import asyncio
import sys
from datetime import datetime
from sqlalchemy import select
from models import async_session
from ml_models_table import MLModel
from ml_runtime import model_registry
from model_deployment import deployment_pipeline

class DeployModelCLI:
    """Command-line interface for model deployment"""
    
    async def deploy(self, model_id: int, actor: str = "admin"):
        """Deploy a model with governance check"""
        
        print(f"\n🚀 Deploying model {model_id}...")
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            if not model:
                print(f"❌ Model {model_id} not found")
                return False
            
            print(f"   Model: {model.model_name} v{model.version}")
            print(f"   Type: {model.model_type}")
            print(f"   Accuracy: {model.accuracy or 'N/A'}")
            print(f"   Status: {model.deployment_status}")
        
        success, msg = await deployment_pipeline.deploy_with_pipeline(model_id, actor)
        
        if success:
            print(f"\n✅ {msg}")
            return True
        else:
            print(f"\n❌ {msg}")
            return False
    
    async def rollback(self, model_type: str, actor: str = "admin"):
        """Rollback to previous model version"""
        
        print(f"\n↩️  Rolling back model type: {model_type}...")
        
        success = await model_registry.rollback_model(model_type, actor)
        
        if success:
            print(f"\n✅ Rollback successful")
            return True
        else:
            print(f"\n❌ Rollback failed")
            return False
    
    async def list_models(self, model_type: str = None):
        """List all models showing deployed vs available"""
        
        print("\n📋 Model Registry:")
        print("=" * 100)
        
        async with async_session() as session:
            query = select(MLModel).order_by(MLModel.created_at.desc())
            
            if model_type:
                query = query.where(MLModel.model_type == model_type)
            
            result = await session.execute(query)
            models = result.scalars().all()
            
            if not models:
                print("No models found")
                return
            
            print(f"{'ID':<6} {'Name':<30} {'Type':<20} {'Version':<10} {'Accuracy':<10} {'Status':<15} {'Created':<20}")
            print("-" * 100)
            
            for model in models:
                status_icon = "🟢" if model.deployment_status == "deployed" else "⚪"
                accuracy_str = f"{model.accuracy:.2f}" if model.accuracy else "N/A"
                created_str = model.created_at.strftime("%Y-%m-%d %H:%M") if model.created_at else "N/A"
                
                print(f"{status_icon} {model.id:<4} {model.model_name:<30} {model.model_type:<20} "
                      f"{model.version:<10} {accuracy_str:<10} {model.deployment_status:<15} {created_str:<20}")
        
        print("\nLegend: 🟢 Deployed  ⚪ Available")
    
    async def show_details(self, model_id: int):
        """Show detailed information about a model"""
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            
            if not model:
                print(f"❌ Model {model_id} not found")
                return
            
            print(f"\n📊 Model Details (ID: {model_id})")
            print("=" * 60)
            print(f"Name:            {model.model_name}")
            print(f"Version:         {model.version}")
            print(f"Type:            {model.model_type}")
            print(f"Model Hash:      {model.model_hash}")
            print(f"Dataset Hash:    {model.dataset_hash}")
            print(f"Status:          {model.deployment_status}")
            print(f"Verification:    {model.verification_status}")
            print(f"\nMetrics:")
            print(f"  Accuracy:      {model.accuracy or 'N/A'}")
            print(f"  Precision:     {model.precision or 'N/A'}")
            print(f"  Recall:        {model.recall or 'N/A'}")
            print(f"  F1 Score:      {model.f1_score or 'N/A'}")
            print(f"\nTraining:")
            print(f"  Samples:       {model.training_data_count}")
            print(f"  Trust Min:     {model.trust_score_min or 'N/A'}")
            print(f"\nTimestamps:")
            print(f"  Created:       {model.created_at}")
            print(f"  Deployed:      {model.deployed_at or 'Not deployed'}")
            print(f"  Deprecated:    {model.deprecated_at or 'N/A'}")
            print(f"\nApproval:")
            print(f"  Approved by:   {model.approved_by or 'Not approved'}")
            
            artifact_path = model_registry._get_model_path(model_id)
            print(f"\nArtifact:")
            print(f"  Path:          {artifact_path}")
            print(f"  Exists:        {'✓' if artifact_path.exists() else '✗'}")

async def main():
    """CLI entry point"""
    
    cli = DeployModelCLI()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m grace_rebuild.backend.deploy_model_cli deploy <model_id> [actor]")
        print("  python -m grace_rebuild.backend.deploy_model_cli rollback <model_type> [actor]")
        print("  python -m grace_rebuild.backend.deploy_model_cli list-models [model_type]")
        print("  python -m grace_rebuild.backend.deploy_model_cli details <model_id>")
        return
    
    command = sys.argv[1]
    
    if command == "deploy":
        if len(sys.argv) < 3:
            print("❌ Usage: deploy <model_id> [actor]")
            return
        
        model_id = int(sys.argv[2])
        actor = sys.argv[3] if len(sys.argv) > 3 else "admin"
        await cli.deploy(model_id, actor)
    
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("❌ Usage: rollback <model_type> [actor]")
            return
        
        model_type = sys.argv[2]
        actor = sys.argv[3] if len(sys.argv) > 3 else "admin"
        await cli.rollback(model_type, actor)
    
    elif command == "list-models":
        model_type = sys.argv[2] if len(sys.argv) > 2 else None
        await cli.list_models(model_type)
    
    elif command == "details":
        if len(sys.argv) < 3:
            print("❌ Usage: details <model_id>")
            return
        
        model_id = int(sys.argv[2])
        await cli.show_details(model_id)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())
