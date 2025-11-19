"""
Model Init Bundle Loader

Pulls model weights, configs, and embeddings from local memory
so Grace can run offline without re-downloading.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.memory.memory_catalog import AssetType, memory_catalog
from backend.memory.memory_mount import memory_mount


@dataclass
class ModelBundle:
    """Model bundle with weights and config"""
    model_name: str
    weights_path: Path
    config: Dict[str, Any]
    trust_score: float


class ModelInitBundleLoader:
    """
    Loads model bundles from local memory storage
    
    Enables offline operation by pulling:
    - Model weights (embeddings, fine-tuned models)
    - Model configs
    - Pre-computed embeddings
    
    No need to re-download from HuggingFace, OpenAI, etc.
    """

    def __init__(self):
        self.cache: Dict[str, ModelBundle] = {}

    def load_model(self, model_name: str) -> Optional[ModelBundle]:
        """
        Load model bundle from local storage
        
        Args:
            model_name: Model identifier (e.g., "sentence-transformers/all-MiniLM-L6-v2")
        
        Returns:
            ModelBundle or None if not found
        """
        if model_name in self.cache:
            return self.cache[model_name]
        
        weights_path = memory_mount.load_model_bundle(model_name)
        if not weights_path:
            return None
        
        assets = memory_catalog.list_assets(
            asset_type=AssetType.MODEL_WEIGHTS,
        )
        
        for asset in assets:
            if asset.metadata.get("model_name") == model_name:
                bundle = ModelBundle(
                    model_name=model_name,
                    weights_path=weights_path,
                    config=asset.metadata.get("config", {}),
                    trust_score=asset.trust_score,
                )
                self.cache[model_name] = bundle
                return bundle
        
        return None

    def register_model(
        self,
        model_name: str,
        weights_path: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> ModelBundle:
        """
        Register new model bundle in memory storage
        
        Args:
            model_name: Model identifier
            weights_path: Path to model weights
            config: Model configuration
        
        Returns:
            ModelBundle
        """
        import asyncio
        
        loop = asyncio.get_event_loop()
        asset = loop.run_until_complete(
            memory_mount.store_model_bundle(model_name, weights_path, config)
        )
        
        bundle = ModelBundle(
            model_name=model_name,
            weights_path=Path(asset.path),
            config=config or {},
            trust_score=asset.trust_score,
        )
        
        self.cache[model_name] = bundle
        return bundle

    def list_available_models(self) -> List[str]:
        """List all available model bundles"""
        assets = memory_catalog.list_assets(
            asset_type=AssetType.MODEL_WEIGHTS,
        )
        return [asset.metadata.get("model_name", "unknown") for asset in assets]

    def load_embeddings(self, dataset_name: str) -> Optional[Path]:
        """
        Load pre-computed embeddings
        
        Args:
            dataset_name: Name of embedded dataset
        
        Returns:
            Path to embeddings file or None
        """
        assets = memory_catalog.list_assets(
            asset_type=AssetType.EMBEDDINGS,
        )
        
        for asset in assets:
            if asset.metadata.get("dataset_name") == dataset_name:
                return Path(asset.path)
        
        return None

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model configuration without loading weights"""
        bundle = self.load_model(model_name)
        return bundle.config if bundle else None


model_init_loader = ModelInitBundleLoader()
