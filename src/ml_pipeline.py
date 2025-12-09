"""
Machine Learning Pipeline Module
Advanced ML models for predicting U5MR from PM2.5 and confounders
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, List, Optional
import os
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, KFold, GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import (r2_score, mean_absolute_error, mean_squared_error, 
                            median_absolute_error, mean_absolute_percentage_error)

import config


def create_time_aware_split(df: pd.DataFrame,
                            features: List[str],
                            target: str,
                            test_size: float = 0.2,
                            verbose: bool = True) -> Tuple:
    """
    Create time-aware train/test split (oldest 80% train, newest 20% test).
    
    Args:
        df: DataFrame with Year column
        features: List of feature column names
        target: Target column name
        test_size: Proportion of data for testing
        verbose: Print information
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, train_df, test_df)
    """
    if verbose:
        print(f"[SPLIT] Creating time-aware train/test split")
    
    # Remove missing values
    df_clean = df.dropna(subset=features + [target]).copy()
    
    if len(df_clean) == 0:
        raise ValueError(f"No data remaining after removing missing values. Check features: {features}")
    
    # Clip outliers (1st and 99th percentiles)
    for col in features + [target]:
        if col in df_clean.columns and df_clean[col].notna().sum() > 0:
            q1, q99 = df_clean[col].quantile([0.01, 0.99])
            df_clean[col] = df_clean[col].clip(q1, q99)
    
    # Split by year
    year_cutoff = df_clean['Year'].quantile(1 - test_size)
    train_df = df_clean[df_clean['Year'] <= year_cutoff].copy()
    test_df = df_clean[df_clean['Year'] > year_cutoff].copy()
    
    X_train = train_df[features]
    X_test = test_df[features]
    y_train = train_df[target]
    y_test = test_df[target]
    
    if verbose:
        print(f"  Train: {len(train_df)} samples, years {train_df['Year'].min()}-{train_df['Year'].max()}")
        print(f"  Test:  {len(test_df)} samples, years {test_df['Year'].min()}-{test_df['Year'].max()}")
        print(f"  Features: {features}")
    
    return X_train, X_test, y_train, y_test, train_df, test_df


def build_model_pipeline(model, features: List[str]) -> Pipeline:
    """
    Build sklearn pipeline with preprocessing and model.
    
    Args:
        model: Sklearn estimator
        features: List of feature names
        
    Returns:
        Pipeline object
    """
    preprocessor = ColumnTransformer(
        [('scaler', StandardScaler(), features)],
        remainder='drop'
    )
    
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    return pipeline


def train_and_evaluate_models(X_train: pd.DataFrame,
                              X_test: pd.DataFrame,
                              y_train: pd.Series,
                              y_test: pd.Series,
                              features: List[str],
                              cv_folds: int = 5,
                              verbose: bool = True) -> Tuple[Dict, pd.DataFrame]:
    """
    Train multiple models with grid search and evaluate on test set.
    
    Args:
        X_train, X_test: Feature matrices
        y_train, y_test: Target vectors
        features: List of feature names
        cv_folds: Number of CV folds
        verbose: Print progress
        
    Returns:
        Tuple of (trained_models_dict, results_dataframe)
    """
    if verbose:
        print(f"\n[TRAIN] Training multiple ML models with {cv_folds}-fold CV")
    
    # Define models and hyperparameter grids
    models = {
        'Ridge': {
            'model': Ridge(random_state=config.RANDOM_SEED),
            'params': {'model__alpha': config.RIDGE_ALPHAS}
        },
        'Lasso': {
            'model': Lasso(random_state=config.RANDOM_SEED, max_iter=10000),
            'params': {'model__alpha': config.LASSO_ALPHAS}
        },
        'ElasticNet': {
            'model': ElasticNet(random_state=config.RANDOM_SEED, max_iter=10000),
            'params': {
                'model__alpha': [0.01, 0.1, 1.0],
                'model__l1_ratio': [0.3, 0.5, 0.7]
            }
        },
        'RandomForest': {
            'model': RandomForestRegressor(
                n_estimators=config.RF_N_ESTIMATORS,
                random_state=config.RANDOM_SEED,
                n_jobs=-1
            ),
            'params': {
                'model__max_depth': config.RF_MAX_DEPTHS,
                'model__min_samples_leaf': config.RF_MIN_SAMPLES_LEAF
            }
        },
        'GradientBoosting': {
            'model': GradientBoostingRegressor(random_state=config.RANDOM_SEED),
            'params': {
                'model__n_estimators': config.GBR_N_ESTIMATORS,
                'model__learning_rate': config.GBR_LEARNING_RATES,
                'model__max_depth': config.GBR_MAX_DEPTHS
            }
        }
    }
    
    # Try to import XGBoost
    try:
        import xgboost as xgb
        models['XGBoost'] = {
            'model': xgb.XGBRegressor(
                random_state=config.RANDOM_SEED,
                n_jobs=-1,
                verbosity=0
            ),
            'params': {
                'model__n_estimators': [300, 600],
                'model__learning_rate': [0.05, 0.1],
                'model__max_depth': [3, 5],
                'model__subsample': [0.8, 1.0]
            }
        }
    except ImportError:
        if verbose:
            print("  [INFO] XGBoost not available, skipping")
    
    # Train models
    trained_models = {}
    results = []
    
    cv = KFold(n_splits=cv_folds, shuffle=True, random_state=config.RANDOM_SEED)
    
    for name, model_dict in models.items():
        if verbose:
            print(f"\n  Training {name}...")
        
        # Build pipeline
        pipeline = build_model_pipeline(model_dict['model'], features)
        
        # Grid search
        grid_search = GridSearchCV(
            pipeline,
            model_dict['params'],
            cv=cv,
            scoring='neg_mean_absolute_error',
            n_jobs=-1,
            verbose=0
        )
        
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        trained_models[name] = best_model
        
        # Evaluate on test set
        y_pred = best_model.predict(X_test)
        
        metrics = {
            'Model': name,
            'R2': r2_score(y_test, y_pred),
            'MAE': mean_absolute_error(y_test, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
            'MedAE': median_absolute_error(y_test, y_pred),
            'MAPE': mean_absolute_percentage_error(y_test, y_pred) * 100,
            'CV_Score': -grid_search.best_score_,
            'Best_Params': str(grid_search.best_params_)
        }
        
        results.append(metrics)
        
        if verbose:
            print(f"    R²={metrics['R2']:.4f}, MAE={metrics['MAE']:.2f}, "
                  f"RMSE={metrics['RMSE']:.2f}")
    
    results_df = pd.DataFrame(results).sort_values('MAE')
    
    if verbose:
        print(f"\n[DONE] Model training complete")
        print(f"\nModel Comparison (sorted by MAE):")
        print(results_df[['Model', 'R2', 'MAE', 'RMSE', 'MedAE']].to_string(index=False))
    
    return trained_models, results_df


def compute_feature_importance(model, 
                               features: List[str],
                               model_name: str) -> pd.DataFrame:
    """
    Extract feature importance from trained model.
    
    Args:
        model: Trained sklearn pipeline
        features: List of feature names
        model_name: Name of the model
        
    Returns:
        DataFrame with feature importances
    """
    if hasattr(model.named_steps['model'], 'feature_importances_'):
        # Tree-based models
        importances = model.named_steps['model'].feature_importances_
        imp_df = pd.DataFrame({
            'Feature': features,
            'Importance': importances,
            'Type': 'Gini'
        }).sort_values('Importance', ascending=False)
        
    elif hasattr(model.named_steps['model'], 'coef_'):
        # Linear models - scale by feature std
        scaler = model.named_steps['preprocessor'].named_transformers_['scaler']
        coefs = model.named_steps['model'].coef_
        scaled_coefs = np.abs(coefs * scaler.scale_)
        
        imp_df = pd.DataFrame({
            'Feature': features,
            'Importance': scaled_coefs,
            'Type': 'Coefficient'
        }).sort_values('Importance', ascending=False)
    else:
        imp_df = pd.DataFrame({'Feature': features, 'Importance': 0, 'Type': 'Unknown'})
    
    return imp_df


def plot_model_comparison(results_df: pd.DataFrame,
                         save_path: Optional[str] = None,
                         show: bool = False) -> None:
    """
    Plot model performance comparison.
    
    Args:
        results_df: DataFrame with model results
        save_path: Path to save figure
        show: Whether to display plot
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # R² comparison
    axes[0].barh(results_df['Model'], results_df['R2'], color='steelblue')
    axes[0].set_xlabel('R² Score')
    axes[0].set_title('Model Comparison: R²')
    axes[0].set_xlim(0, 1)
    
    # MAE comparison
    axes[1].barh(results_df['Model'], results_df['MAE'], color='coral')
    axes[1].set_xlabel('Mean Absolute Error')
    axes[1].set_title('Model Comparison: MAE')
    
    # RMSE comparison
    axes[2].barh(results_df['Model'], results_df['RMSE'], color='mediumseagreen')
    axes[2].set_xlabel('Root Mean Squared Error')
    axes[2].set_title('Model Comparison: RMSE')
    
    plt.tight_layout()
    
    if save_path is None:
        save_path = os.path.join(config.FIGURES_DIR, 'model_comparison.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_predictions_vs_actual(y_test: pd.Series,
                               y_pred: np.ndarray,
                               model_name: str,
                               save_path: Optional[str] = None,
                               show: bool = False) -> None:
    """
    Plot predicted vs actual values.
    
    Args:
        y_test: Actual values
        y_pred: Predicted values
        model_name: Name of model
        save_path: Path to save figure
        show: Whether to display plot
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Scatter plot
    axes[0].scatter(y_test, y_pred, alpha=0.5, s=30)
    max_val = max(y_test.max(), y_pred.max()) * 1.05
    axes[0].plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    axes[0].set_xlabel('Actual U5MR (per 1,000)')
    axes[0].set_ylabel('Predicted U5MR (per 1,000)')
    axes[0].set_title(f'{model_name}: Predicted vs Actual')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Residuals plot
    residuals = y_test - y_pred
    axes[1].scatter(y_pred, residuals, alpha=0.5, s=30)
    axes[1].axhline(0, color='r', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Predicted U5MR (per 1,000)')
    axes[1].set_ylabel('Residuals')
    axes[1].set_title(f'{model_name}: Residual Plot')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path is None:
        save_path = os.path.join(config.FIGURES_DIR, f'predictions_{model_name}.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_feature_importance(importance_df: pd.DataFrame,
                           model_name: str,
                           save_path: Optional[str] = None,
                           show: bool = False) -> None:
    """
    Plot feature importance.
    
    Args:
        importance_df: DataFrame with feature importances
        model_name: Name of model
        save_path: Path to save figure
        show: Whether to display plot
    """
    plt.figure(figsize=(10, 6))
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(importance_df)))
    plt.barh(importance_df['Feature'], importance_df['Importance'], color=colors)
    plt.xlabel(f'Importance ({importance_df["Type"].iloc[0]})')
    plt.title(f'{model_name}: Feature Importance')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    if save_path is None:
        save_path = os.path.join(config.FIGURES_DIR, f'feature_importance_{model_name}.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def save_models(models_dict: Dict, 
               save_dir: str = None) -> None:
    """
    Save trained models to disk.
    
    Args:
        models_dict: Dictionary of trained models
        save_dir: Directory to save models
    """
    if save_dir is None:
        save_dir = config.MODELS_DIR
    
    os.makedirs(save_dir, exist_ok=True)
    
    for name, model in models_dict.items():
        filepath = os.path.join(save_dir, f'{name.lower()}_model.pkl')
        joblib.dump(model, filepath)
        print(f"[SAVED] Model: {filepath}")


def load_model(model_name: str, 
              load_dir: str = None):
    """
    Load a trained model from disk.
    
    Args:
        model_name: Name of model to load
        load_dir: Directory containing models
        
    Returns:
        Loaded model
    """
    if load_dir is None:
        load_dir = config.MODELS_DIR
    
    filepath = os.path.join(load_dir, f'{model_name.lower()}_model.pkl')
    model = joblib.load(filepath)
    print(f"[LOADED] Model: {filepath}")
    return model

