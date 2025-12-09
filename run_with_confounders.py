"""
Run ML Pipeline with Socio-Economic Confounders
Compares PM2.5-only vs PM2.5 + Confounders
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, median_absolute_error, mean_absolute_percentage_error
import config
import src.data_processing as dp
import src.feature_engineering as fe

# Set random seed
np.random.seed(42)

print("="*80)
print("ML PIPELINE WITH SOCIO-ECONOMIC CONFOUNDERS")
print("="*80)

# ============================================================================
# STEP 1: Load Base Data
# ============================================================================
print("\n[STEP 1] Loading base data...")
data_dict = dp.load_processed_data()
df_base = data_dict['merged']
print(f"  Base data: {df_base.shape}")

# ============================================================================
# STEP 2: Download and Load External Data
# ============================================================================
print("\n[STEP 2] Loading socio-economic confounders...")
external_data = fe.download_external_data(verbose=True)

# ============================================================================
# STEP 3: Merge External Features
# ============================================================================
print("\n[STEP 3] Merging features...")
df_merged = fe.merge_external_features(df_base, external_data, verbose=True)

# ============================================================================
# STEP 4: Create Engineered Features
# ============================================================================
print("\n[STEP 4] Engineering features...")
df_full = fe.create_engineered_features(df_merged, verbose=True)

print(f"\n[INFO] Full dataset: {df_full.shape}")
print(f"  Columns: {df_full.columns.tolist()}")

# ============================================================================
# STEP 5: Prepare Feature Sets
# ============================================================================
print("\n[STEP 5] Preparing feature sets...")

target = 'U5MR_per_1000'

# Feature Set 1: PM2.5 Only (3 features)
features_pm25_only = ['PM25_Total_ugm3', 'PM25_Urban_ugm3', 'PM25_Rural_ugm3']

# Feature Set 2: PM2.5 + Socio-Economic Confounders
features_with_confounders = [
    'PM25_Total_ugm3', 'PM25_Urban_ugm3', 'PM25_Rural_ugm3',
    'log_gdp_pc', 'log_health_exp', 'urban_pct', 'fertility'
]

# Feature Set 3: Full (PM2.5 + Confounders + Engineered)
features_full = features_with_confounders + [
    'log_pm25', 'pm25_squared', 'pm25_x_gdp', 'pm25_x_urban', 'pm25_urban_rural_gap'
]

feature_sets = {
    'PM2.5 Only': features_pm25_only,
    'PM2.5 + Confounders': features_with_confounders,
    'Full (with Interactions)': features_full
}

print(f"\n[FEATURE SETS]")
for name, features in feature_sets.items():
    available = [f for f in features if f in df_full.columns]
    print(f"  {name}: {len(available)} features")
    print(f"    {available}")

# ============================================================================
# STEP 6: Create Time-Aware Split (2015 split)
# ============================================================================
print("\n[STEP 6] Creating time-aware train/test split (Year <= 2015 for training)...")

train_mask = df_full['Year'] <= 2015
test_mask = df_full['Year'] > 2015

print(f"  Training: {train_mask.sum()} samples (Year <= 2015)")
print(f"  Testing: {test_mask.sum()} samples (Year > 2015)")

# ============================================================================
# STEP 7: Train Models for Each Feature Set
# ============================================================================
print("\n[STEP 7] Training models for each feature set...")

# Define models to test
models_to_test = {
    'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'XGBoost': XGBRegressor(random_state=42, n_jobs=-1, verbosity=0),
    'GradientBoosting': GradientBoostingRegressor(random_state=42),
}

# Hyperparameter grids (simplified for speed)
param_grids = {
    'RandomForest': {
        'model__max_depth': [None, 10, 20],
        'model__min_samples_leaf': [1, 2]
    },
    'XGBoost': {
        'model__max_depth': [3, 5, 7],
        'model__learning_rate': [0.01, 0.1],
        'model__n_estimators': [200, 400]
    },
    'GradientBoosting': {
        'model__max_depth': [3, 5],
        'model__learning_rate': [0.05, 0.1],
        'model__n_estimators': [200, 400]
    }
}

# Store all results
all_results = []

for fs_name, features in feature_sets.items():
    print(f"\n{'='*80}")
    print(f"FEATURE SET: {fs_name}")
    print(f"{'='*80}")
    
    # Check available features
    available_features = [f for f in features if f in df_full.columns]
    if len(available_features) == 0:
        print(f"  [SKIP] No features available")
        continue
    
    # Prepare data
    cols_needed = available_features + [target, 'Year']
    df_work = df_full[cols_needed].copy()
    df_work = df_work.dropna()
    
    if len(df_work) == 0:
        print(f"  [SKIP] No data after removing missing values")
        continue
    
    print(f"  Using {len(available_features)} features: {available_features}")
    print(f"  Working with {len(df_work)} observations")
    
    # Split
    train_data = df_work[df_work['Year'] <= 2015]
    test_data = df_work[df_work['Year'] > 2015]
    
    if len(train_data) == 0 or len(test_data) == 0:
        print(f"  [SKIP] Insufficient train or test data")
        continue
    
    X_train = train_data[available_features]
    y_train = train_data[target]
    X_test = test_data[available_features]
    y_test = test_data[target]
    
    print(f"  Train: {X_train.shape}, Test: {X_test.shape}")
    
    # Train each model
    for model_name, model in models_to_test.items():
        print(f"\n  [{model_name}]")
        
        # Create pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', model)
        ])
        
        # GridSearchCV
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        grid = GridSearchCV(
            pipeline,
            param_grids[model_name],
            cv=cv,
            scoring='r2',
            n_jobs=-1,
            verbose=0
        )
        
        # Train
        grid.fit(X_train, y_train)
        
        # Predict
        y_pred_train = grid.predict(X_train)
        y_pred_test = grid.predict(X_test)
        
        # Evaluate
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        medae_test = median_absolute_error(y_test, y_pred_test)
        
        print(f"    R² Train: {r2_train:.4f}")
        print(f"    R² Test:  {r2_test:.4f}")
        print(f"    MAE Test: {mae_test:.2f}")
        print(f"    RMSE Test: {rmse_test:.2f}")
        print(f"    Best params: {grid.best_params_}")
        
        # Store results
        all_results.append({
            'Feature_Set': fs_name,
            'N_Features': len(available_features),
            'Model': model_name,
            'R2_Train': r2_train,
            'R2_Test': r2_test,
            'MAE': mae_test,
            'RMSE': rmse_test,
            'MedAE': medae_test,
            'CV_Score': grid.best_score_,
            'Best_Params': str(grid.best_params_)
        })

# ============================================================================
# STEP 8: Save and Visualize Results
# ============================================================================
print("\n[STEP 8] Saving results...")

results_df = pd.DataFrame(all_results)
results_path = os.path.join(config.TABLES_DIR, 'model_comparison_with_confounders.csv')
results_df.to_csv(results_path, index=False)
print(f"  [SAVED] {results_path}")

# Display results
print("\n" + "="*80)
print("RESULTS SUMMARY")
print("="*80)
print(results_df.to_string(index=False))

# ============================================================================
# STEP 9: Create Comparison Visualizations
# ============================================================================
print("\n[STEP 9] Creating visualizations...")

# Figure 1: R² Comparison across feature sets
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: R² Test by Feature Set
pivot_r2 = results_df.pivot(index='Model', columns='Feature_Set', values='R2_Test')
pivot_r2.plot(kind='bar', ax=axes[0], width=0.8)
axes[0].set_title('Model Performance (R²) by Feature Set', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Model')
axes[0].set_ylabel('R² Score (Test Set)')
axes[0].legend(title='Feature Set', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[0].axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
axes[0].grid(axis='y', alpha=0.3)
axes[0].set_ylim(bottom=0)

# Plot 2: MAE by Feature Set
pivot_mae = results_df.pivot(index='Model', columns='Feature_Set', values='MAE')
pivot_mae.plot(kind='bar', ax=axes[1], width=0.8, color=['#e74c3c', '#3498db', '#2ecc71'])
axes[1].set_title('Model Error (MAE) by Feature Set', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Model')
axes[1].set_ylabel('Mean Absolute Error (MAE)')
axes[1].legend(title='Feature Set', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
fig_path = os.path.join(config.FIGURES_DIR, 'feature_set_comparison.png')
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"  [SAVED] {fig_path}")
plt.close()

# Figure 2: Improvement from adding confounders
if 'PM2.5 Only' in results_df['Feature_Set'].values and 'PM2.5 + Confounders' in results_df['Feature_Set'].values:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    pm_only = results_df[results_df['Feature_Set'] == 'PM2.5 Only'].sort_values('Model')
    pm_conf = results_df[results_df['Feature_Set'] == 'PM2.5 + Confounders'].sort_values('Model')
    
    x = np.arange(len(pm_only))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pm_only['R2_Test'], width, label='PM2.5 Only', color='#e74c3c', alpha=0.8)
    bars2 = ax.bar(x + width/2, pm_conf['R2_Test'], width, label='PM2.5 + Confounders', color='#2ecc71', alpha=0.8)
    
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_ylabel('R² Score', fontsize=12, fontweight='bold')
    ax.set_title('Impact of Adding Socio-Economic Confounders', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(pm_only['Model'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    fig_path = os.path.join(config.FIGURES_DIR, 'confounder_impact.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"  [SAVED] {fig_path}")
    plt.close()

# Figure 3: Feature importance for best model with confounders
best_conf_idx = results_df[results_df['Feature_Set'] == 'PM2.5 + Confounders']['R2_Test'].idxmax()
best_conf = results_df.loc[best_conf_idx]

print(f"\n[BEST MODEL WITH CONFOUNDERS]")
print(f"  Model: {best_conf['Model']}")
print(f"  R²: {best_conf['R2_Test']:.4f}")
print(f"  MAE: {best_conf['MAE']:.2f}")

# Train final model to get feature importance
df_work = df_full[features_with_confounders + [target, 'Year']].dropna()
train_data = df_work[df_work['Year'] <= 2015]
test_data = df_work[df_work['Year'] > 2015]

X_train = train_data[features_with_confounders]
y_train = train_data[target]
X_test = test_data[features_with_confounders]
y_test = test_data[target]

# Train best model
if best_conf['Model'] == 'RandomForest':
    final_model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
elif best_conf['Model'] == 'XGBoost':
    final_model = XGBRegressor(n_estimators=300, random_state=42, n_jobs=-1, verbosity=0)
else:
    final_model = GradientBoostingRegressor(n_estimators=300, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

final_model.fit(X_train_scaled, y_train)

# Get feature importance
if hasattr(final_model, 'feature_importances_'):
    importance = final_model.feature_importances_
    
    # Create DataFrame
    feat_imp_df = pd.DataFrame({
        'Feature': features_with_confounders,
        'Importance': importance
    }).sort_values('Importance', ascending=False)
    
    # Save
    imp_path = os.path.join(config.TABLES_DIR, 'feature_importance_with_confounders.csv')
    feat_imp_df.to_csv(imp_path, index=False)
    print(f"\n[SAVED] {imp_path}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#e74c3c' if 'PM25' in f else '#3498db' for f in feat_imp_df['Feature']]
    ax.barh(feat_imp_df['Feature'], feat_imp_df['Importance'], color=colors, alpha=0.7)
    ax.set_xlabel('Importance', fontsize=12, fontweight='bold')
    ax.set_title(f'Feature Importance: {best_conf["Model"]} with Confounders', 
                fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#e74c3c', alpha=0.7, label='PM2.5 Features'),
        Patch(facecolor='#3498db', alpha=0.7, label='Socio-Economic Features')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    fig_path = os.path.join(config.FIGURES_DIR, 'feature_importance_with_confounders.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"[SAVED] {fig_path}")
    plt.close()

# ============================================================================
# STEP 10: Key Insights
# ============================================================================
print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)

# Calculate improvement
pm_only_r2 = results_df[results_df['Feature_Set'] == 'PM2.5 Only']['R2_Test'].max()
pm_conf_r2 = results_df[results_df['Feature_Set'] == 'PM2.5 + Confounders']['R2_Test'].max()
improvement = ((pm_conf_r2 - pm_only_r2) / pm_only_r2) * 100

print(f"\n1. MODEL PERFORMANCE:")
print(f"   - PM2.5 Only: R² = {pm_only_r2:.4f} (explains {pm_only_r2*100:.1f}% of variance)")
print(f"   - PM2.5 + Confounders: R² = {pm_conf_r2:.4f} (explains {pm_conf_r2*100:.1f}% of variance)")
print(f"   - Improvement: {improvement:+.1f}%")

print(f"\n2. BEST MODEL:")
print(f"   - {best_conf['Model']} with Confounders")
print(f"   - R² = {best_conf['R2_Test']:.4f}")
print(f"   - MAE = {best_conf['MAE']:.2f} deaths per 1000 live births")

if hasattr(final_model, 'feature_importances_'):
    top3 = feat_imp_df.head(3)
    print(f"\n3. TOP 3 MOST IMPORTANT FEATURES:")
    for idx, row in top3.iterrows():
        print(f"   - {row['Feature']}: {row['Importance']:.4f}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nFiles saved:")
print(f"  - {results_path}")
print(f"  - {os.path.join(config.FIGURES_DIR, 'feature_set_comparison.png')}")
print(f"  - {os.path.join(config.FIGURES_DIR, 'confounder_impact.png')}")
print(f"  - {os.path.join(config.FIGURES_DIR, 'feature_importance_with_confounders.png')}")
print(f"  - {imp_path}")

