#!/usr/bin/env python3
"""
Model Manager for Predictive Maintenance
=========================================
Handles model persistence, versioning, and metadata management.

Features:
- Save/load trained models
- Model versioning with metadata
- JSON-based metadata storage
- Automatic model registry

Author: Predictive Maintenance for Army XEM
"""

import os
import json
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any
import warnings

warnings.filterwarnings("ignore")


class ModelManager:
    """
    Manages model persistence and versioning for predictive maintenance.
    
    Directory structure:
        data/models/
            ├── registry.json          # Model registry with all versions
            ├── current/               # Symlink/copy to latest model
            │   ├── model.pkl
            │   ├── metadata.json
            │   └── scaler.pkl (if needed)
            ├── v1_20251115_132045/    # Versioned model directory
            │   ├── model.pkl
            │   ├── metadata.json
            │   └── scaler.pkl
            └── v2_20251115_154523/
                └── ...
    """
    
    def __init__(self, models_dir: str = "data/models"):
        """
        Initialize Model Manager.
        
        Args:
            models_dir: Root directory for model storage
        """
        self.models_dir = Path(models_dir)
        self.registry_path = self.models_dir / "registry.json"
        self.current_model_dir = self.models_dir / "current"
        
        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.current_model_dir.mkdir(exist_ok=True)
        
        # Initialize registry if not exists
        if not self.registry_path.exists():
            self._initialize_registry()
        
        print(f"✓ ModelManager initialized at: {self.models_dir}")
    
    def _initialize_registry(self):
        """Initialize empty model registry."""
        registry = {
            "models": [],
            "current_version": None,
            "created_at": datetime.now().isoformat()
        }
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def _load_registry(self) -> Dict:
        """Load model registry."""
        with open(self.registry_path, 'r') as f:
            return json.load(f)
    
    def _save_registry(self, registry: Dict):
        """Save model registry."""
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def _generate_version_name(self) -> str:
        """Generate version name with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        registry = self._load_registry()
        version_num = len(registry["models"]) + 1
        return f"v{version_num}_{timestamp}"
    
    def save_model(
        self,
        model: Any,
        metadata: Dict,
        scaler: Optional[Any] = None,
        version_name: Optional[str] = None
    ) -> str:
        """
        Save model with metadata and optional scaler.
        
        Args:
            model: Trained model object (e.g., RiskPredictor)
            metadata: Model metadata (metrics, config, etc.)
            scaler: Optional data scaler
            version_name: Optional custom version name
        
        Returns:
            Version name of saved model
        """
        # Generate version name
        if version_name is None:
            version_name = self._generate_version_name()
        
        # Create version directory
        version_dir = self.models_dir / version_name
        version_dir.mkdir(exist_ok=True)
        
        print(f"\n{'='*80}")
        print(f"SAVING MODEL: {version_name}")
        print(f"{'='*80}")
        
        # Save model
        model_path = version_dir / "model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Model saved: {model_path}")
        
        # Save scaler if provided
        if scaler is not None:
            scaler_path = version_dir / "scaler.pkl"
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            print(f"✓ Scaler saved: {scaler_path}")
        
        # Add timestamp to metadata
        metadata["version"] = version_name
        metadata["saved_at"] = datetime.now().isoformat()
        metadata["model_path"] = str(model_path)
        
        # Save metadata
        metadata_path = version_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved: {metadata_path}")
        
        # Update registry
        registry = self._load_registry()
        registry["models"].append({
            "version": version_name,
            "saved_at": metadata["saved_at"],
            "metrics": metadata.get("metrics", {}),
            "path": str(version_dir)
        })
        registry["current_version"] = version_name
        self._save_registry(registry)
        print(f"✓ Registry updated")
        
        # Copy to current directory
        self._set_current_model(version_name)
        
        print(f"{'='*80}")
        print(f"✓ Model {version_name} saved successfully!")
        print(f"{'='*80}\n")
        
        return version_name
    
    def _set_current_model(self, version_name: str):
        """Set a model version as current by copying files."""
        version_dir = self.models_dir / version_name
        
        if not version_dir.exists():
            raise ValueError(f"Model version {version_name} not found")
        
        # Clear current directory
        for file in self.current_model_dir.glob("*"):
            file.unlink()
        
        # Copy files to current
        for file in version_dir.glob("*"):
            shutil.copy2(file, self.current_model_dir / file.name)
        
        print(f"✓ Current model set to: {version_name}")
    
    def load_model(
        self,
        version: Optional[str] = None,
        include_metadata: bool = True,
        include_scaler: bool = True
    ) -> Dict[str, Any]:
        """
        Load model (and optionally metadata/scaler).
        
        Args:
            version: Model version to load (None = current/latest)
            include_metadata: Include metadata in return dict
            include_scaler: Include scaler in return dict
        
        Returns:
            Dictionary with 'model', 'metadata', 'scaler' keys
        """
        # Determine directory
        if version is None:
            model_dir = self.current_model_dir
            registry = self._load_registry()
            version = registry.get("current_version", "current")
        else:
            model_dir = self.models_dir / version
        
        if not model_dir.exists():
            raise ValueError(f"Model directory not found: {model_dir}")
        
        print(f"\n{'='*80}")
        print(f"LOADING MODEL: {version}")
        print(f"{'='*80}")
        
        result = {}
        
        # Load model
        model_path = model_dir / "model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            result["model"] = pickle.load(f)
        print(f"✓ Model loaded from: {model_path}")
        
        # Load metadata
        if include_metadata:
            metadata_path = model_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    result["metadata"] = json.load(f)
                print(f"✓ Metadata loaded")
        
        # Load scaler
        if include_scaler:
            scaler_path = model_dir / "scaler.pkl"
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    result["scaler"] = pickle.load(f)
                print(f"✓ Scaler loaded")
        
        print(f"{'='*80}\n")
        
        return result
    
    def load_latest_model(self, **kwargs) -> Dict[str, Any]:
        """
        Load the latest/current model.
        
        Args:
            **kwargs: Passed to load_model()
        
        Returns:
            Dictionary with model, metadata, scaler
        """
        return self.load_model(version=None, **kwargs)
    
    def list_models(self) -> List[Dict]:
        """
        List all available models.
        
        Returns:
            List of model information dictionaries
        """
        registry = self._load_registry()
        return registry["models"]
    
    def get_current_version(self) -> Optional[str]:
        """Get current model version."""
        registry = self._load_registry()
        return registry.get("current_version")
    
    def delete_model(self, version: str):
        """
        Delete a model version.
        
        Args:
            version: Version name to delete
        """
        version_dir = self.models_dir / version
        
        if not version_dir.exists():
            raise ValueError(f"Model version {version} not found")
        
        # Don't delete if it's the current version
        current = self.get_current_version()
        if version == current:
            raise ValueError(f"Cannot delete current version {version}. Set a different version as current first.")
        
        # Delete directory
        shutil.rmtree(version_dir)
        
        # Update registry
        registry = self._load_registry()
        registry["models"] = [m for m in registry["models"] if m["version"] != version]
        self._save_registry(registry)
        
        print(f"✓ Model {version} deleted")
    
    def get_model_info(self, version: Optional[str] = None) -> Dict:
        """
        Get detailed model information.
        
        Args:
            version: Model version (None = current)
        
        Returns:
            Model information dictionary
        """
        if version is None:
            version = self.get_current_version()
        
        registry = self._load_registry()
        for model in registry["models"]:
            if model["version"] == version:
                return model
        
        raise ValueError(f"Model version {version} not found in registry")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                    MODEL MANAGER - DEMO                                      ║
    ║                                                                              ║
    ║  Manages model persistence and versioning:                                  ║
    ║  • Save trained models with metadata                                        ║
    ║  • Load models by version or latest                                         ║
    ║  • JSON-based model registry                                                ║
    ║  • Automatic versioning with timestamps                                     ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    USAGE EXAMPLE:
    ==============
    
    from core.model_manager import ModelManager
    from core.risk_predictor import RiskPredictor
    
    # Initialize manager
    manager = ModelManager()
    
    # Train and save model
    predictor = RiskPredictor()
    predictor.train(X_train, y_train)
    
    metadata = {
        "model_type": "RiskPredictor",
        "metrics": {
            "accuracy": 0.95,
            "auc_roc": 0.97
        },
        "training_samples": len(X_train),
        "features": list(X_train.columns)
    }
    
    version = manager.save_model(predictor, metadata)
    
    # Load model later
    loaded = manager.load_latest_model()
    predictor = loaded["model"]
    metadata = loaded["metadata"]
    
    # List all models
    models = manager.list_models()
    
    ══════════════════════════════════════════════════════════════════════════════
    
    KEY FEATURES:
    • Automatic versioning (v1_20251115_132045)
    • JSON metadata storage (metrics, config, features)
    • Model registry for tracking all versions
    • Load latest or specific version
    • Filesystem-based (no database needed)
    
    Perfect for microservices: Each service loads models independently
    """)
