#!/usr/bin/env python3
"""
Retrain Model with SHAP Support
================================
Retrains the model and saves training data sample for SHAP explanations.
"""

from core.pipeline import TrainingPipeline

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              RETRAINING MODEL WITH SHAP SUPPORT                              ║
║                                                                              ║
║  This will train a new model and include training data for SHAP             ║
║  explanations in the API.                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Initialize training pipeline with correct data directory
pipeline = TrainingPipeline(data_dir="data/raw")

# Run full pipeline with smaller sample for quick training
results = pipeline.run_full_pipeline(
    n_samples=1000,        # Use 1000 samples for quick training
    test_size=0.2,          # 80/20 split
    initialize_shap=True,   # Initialize SHAP during training
    save_model=True         # Save model with training data
)

print("\n" + "="*80)
print("MODEL TRAINING COMPLETE!")
print("="*80)
print(f"Model version: {results['version']}")
print(f"Accuracy: {results['evaluation']['eval_results']['accuracy']:.3f}")
print(f"AUC-ROC: {results['evaluation']['eval_results']['auc_roc']:.3f}")
print(f"Cost savings: ${results['evaluation']['threshold_results']['savings']:.2f}")
print("\n✓ Training data sample saved with model")
print("✓ SHAP explanations will now work in the API!")
print("\nRestart the API to use the new model:")
print("  python app.py")
print("="*80 + "\n")
