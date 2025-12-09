"""
Model Interpretability Module
SHAP analysis and advanced model interpretation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from typing import Optional, Tuple
import config


def compute_shap_values(model, X_train: pd.DataFrame, X_test: pd.DataFrame,
                       model_name: str, verbose: bool = True):
    """
    Compute SHAP values for model interpretation.
    
    Args:
        model: Trained sklearn pipeline
        X_train: Training features
        X_test: Test features
        model_name: Name of the model
        verbose: Print progress
        
    Returns:
        SHAP explainer and values
    """
    try:
        import shap
        
        if verbose:
            print(f"[SHAP] Computing SHAP values for {model_name}...")
        
        # Get the actual model from pipeline
        actual_model = model.named_steps['model']
        
        # Transform data using preprocessor
        X_train_transformed = model.named_steps['preprocessor'].transform(X_train)
        X_test_transformed = model.named_steps['preprocessor'].transform(X_test)
        
        # Create appropriate explainer based on model type
        if hasattr(actual_model, 'tree_'):
            # Tree-based models (RandomForest, GradientBoosting, XGBoost)
            explainer = shap.TreeExplainer(actual_model)
            shap_values = explainer.shap_values(X_test_transformed)
        else:
            # Linear models or others
            # Use a sample for KernelExplainer (computationally expensive)
            sample_size = min(100, len(X_train_transformed))
            background = shap.kmeans(X_train_transformed, sample_size)
            explainer = shap.KernelExplainer(actual_model.predict, background)
            shap_values = explainer.shap_values(X_test_transformed[:100])  # Limit for speed
        
        if verbose:
            print(f"  Computed SHAP values for {len(shap_values)} test samples")
        
        return explainer, shap_values, X_test_transformed
        
    except ImportError:
        print("[ERROR] SHAP not installed. Run: pip install shap")
        return None, None, None
    except Exception as e:
        print(f"[ERROR] SHAP computation failed: {e}")
        return None, None, None


def plot_shap_summary(shap_values, X_test_transformed: np.ndarray,
                     features: list, model_name: str,
                     save_path: Optional[str] = None,
                     show: bool = False) -> None:
    """
    Create SHAP summary plot (beeswarm).
    
    Args:
        shap_values: SHAP values array
        X_test_transformed: Transformed test features
        features: Feature names
        model_name: Name of model
        save_path: Path to save figure
        show: Whether to display plot
    """
    try:
        import shap
        
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_test_transformed, 
                         feature_names=features, show=False)
        plt.title(f"{model_name}: SHAP Feature Importance")
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(config.FIGURES_DIR, f'shap_summary_{model_name}.png')
        plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
            
    except Exception as e:
        print(f"[ERROR] SHAP plotting failed: {e}")


def plot_shap_waterfall(explainer, shap_values, X_test_transformed: np.ndarray,
                       features: list, model_name: str, sample_idx: int = 0,
                       save_path: Optional[str] = None,
                       show: bool = False) -> None:
    """
    Create SHAP waterfall plot for individual prediction.
    
    Args:
        explainer: SHAP explainer object
        shap_values: SHAP values array
        X_test_transformed: Transformed test features
        features: Feature names
        model_name: Name of model
        sample_idx: Index of sample to explain
        save_path: Path to save figure
        show: Whether to display plot
    """
    try:
        import shap
        
        # Create explanation object
        if len(shap_values.shape) == 1:
            shap_vals = shap_values
        else:
            shap_vals = shap_values[sample_idx]
        
        explanation = shap.Explanation(
            values=shap_vals,
            base_values=explainer.expected_value if hasattr(explainer, 'expected_value') else 0,
            data=X_test_transformed[sample_idx],
            feature_names=features
        )
        
        plt.figure(figsize=(10, 6))
        shap.waterfall_plot(explanation, show=False)
        plt.title(f"{model_name}: SHAP Explanation for Sample {sample_idx}")
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(config.FIGURES_DIR, 
                                    f'shap_waterfall_{model_name}_sample{sample_idx}.png')
        plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
            
    except Exception as e:
        print(f"[ERROR] SHAP waterfall plot failed: {e}")


def plot_shap_dependence(shap_values, X_test_transformed: np.ndarray,
                        features: list, feature_idx: int, model_name: str,
                        save_path: Optional[str] = None,
                        show: bool = False) -> None:
    """
    Create SHAP dependence plot for a specific feature.
    
    Args:
        shap_values: SHAP values array
        X_test_transformed: Transformed test features
        features: Feature names
        feature_idx: Index of feature to plot
        model_name: Name of model
        save_path: Path to save figure
        show: Whether to display plot
    """
    try:
        import shap
        
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(feature_idx, shap_values, X_test_transformed,
                            feature_names=features, show=False)
        plt.title(f"{model_name}: SHAP Dependence Plot for {features[feature_idx]}")
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(config.FIGURES_DIR,
                                    f'shap_dependence_{model_name}_{features[feature_idx]}.png')
        plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
            
    except Exception as e:
        print(f"[ERROR] SHAP dependence plot failed: {e}")


def generate_shap_report(model, X_train: pd.DataFrame, X_test: pd.DataFrame,
                        features: list, model_name: str,
                        verbose: bool = True) -> dict:
    """
    Generate comprehensive SHAP analysis report.
    
    Args:
        model: Trained sklearn pipeline
        X_train: Training features
        X_test: Test features
        features: Feature names
        model_name: Name of model
        verbose: Print progress
        
    Returns:
        Dictionary with SHAP results
    """
    if verbose:
        print(f"\n[SHAP] Generating interpretability report for {model_name}")
    
    # Compute SHAP values
    explainer, shap_values, X_test_transformed = compute_shap_values(
        model, X_train, X_test, model_name, verbose
    )
    
    if shap_values is None:
        return {}
    
    # Generate plots
    plot_shap_summary(shap_values, X_test_transformed, features, model_name)
    
    # Waterfall plot for first 3 samples
    for idx in range(min(3, len(shap_values))):
        plot_shap_waterfall(explainer, shap_values, X_test_transformed,
                           features, model_name, sample_idx=idx)
    
    # Dependence plots for top 3 features
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_features = np.argsort(mean_abs_shap)[-3:][::-1]
    
    for feat_idx in top_features:
        plot_shap_dependence(shap_values, X_test_transformed, features,
                            feat_idx, model_name)
    
    # Calculate feature importance from SHAP
    shap_importance = pd.DataFrame({
        'Feature': features,
        'SHAP_Importance': mean_abs_shap
    }).sort_values('SHAP_Importance', ascending=False)
    
    # Save importance table
    shap_importance.to_csv(
        os.path.join(config.TABLES_DIR, f'shap_importance_{model_name}.csv'),
        index=False
    )
    print(f"[SAVED] SHAP importance table")
    
    if verbose:
        print(f"\n[SHAP] Top Features by SHAP Importance:")
        print(shap_importance.head(10).to_string(index=False))
    
    return {
        'explainer': explainer,
        'shap_values': shap_values,
        'importance': shap_importance
    }

