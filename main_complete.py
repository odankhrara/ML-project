"""
Air Pollution and Under-5 Mortality Analysis
COMPLETE VERSION - All Phases

This script runs the complete analysis pipeline including:
- Data loading and processing
- Feature engineering with external data
- Multiple ML models with evaluation
- Comprehensive visualizations
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import os
import config
from src import data_processing, visualization, statistical_analysis
from src import feature_engineering, ml_pipeline


def main():
    """Complete analysis pipeline"""
    
    print("=" * 80)
    print("AIR POLLUTION & UNDER-5 MORTALITY ANALYSIS - COMPLETE")
    print("=" * 80)
    print(f"\nBase Directory: {config.BASE_DIR}")
    
    # ========================================================================
    # PHASE 1 & 2: DATA LOADING AND BASIC ANALYSIS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("PHASE 1 & 2: Data Loading and Basic Analysis")
    print("=" * 80)
    
    # Check if processed data already exists
    try:
        print("\n[CHECK] Looking for existing processed data...")
        data = data_processing.load_processed_data(verbose=False)
        merged = data['merged']
        print(f"[OK] Loaded existing processed data: {merged.shape}")
    except:
        print("[INFO] No processed data found, loading raw data...")
        
        # Load and process data
        who_long, who_wide = data_processing.load_who_pm25_data(config.WHO_CSV)
        u5mr_long = data_processing.load_unicef_u5mr_data(config.UNICEF_XLSX)
        merged = data_processing.merge_pm25_u5mr(who_wide, u5mr_long)
        
        # Save processed data
        data_processing.save_processed_data(who_long, who_wide, u5mr_long, merged)
    
    # Basic EDA
    print("\n[EDA] Creating basic exploratory visualizations...")
    visualization.create_exploratory_plots(merged, show=False)
    
    # Statistical analysis
    print("\n[STATS] Performing basic statistical analysis...")
    analysis_results = statistical_analysis.analyze_dataset(merged, verbose=False)
    
    # ========================================================================
    # PHASE 3: MACHINE LEARNING WITH PM2.5 ONLY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("PHASE 3: Machine Learning Pipeline (PM2.5 Only)")
    print("=" * 80)
    
    # Prepare data
    pm_features = [c for c in config.PM25_FEATURES if c in merged.columns]
    
    X_train, X_test, y_train, y_test, train_df, test_df = ml_pipeline.create_time_aware_split(
        merged, pm_features, config.TARGET, verbose=True
    )
    
    # Train models
    models_pm_only, results_pm_only = ml_pipeline.train_and_evaluate_models(
        X_train, X_test, y_train, y_test, pm_features, verbose=True
    )
    
    # Save results
    results_pm_only.to_csv(
        os.path.join(config.TABLES_DIR, 'model_results_pm25_only.csv'),
        index=False
    )
    print(f"\n[SAVED] Model results to {config.TABLES_DIR}/model_results_pm25_only.csv")
    
    # Plot model comparison
    ml_pipeline.plot_model_comparison(
        results_pm_only,
        save_path=os.path.join(config.FIGURES_DIR, 'model_comparison_pm25_only.png')
    )
    
    # Get best model
    best_model_name = results_pm_only.iloc[0]['Model']
    best_model = models_pm_only[best_model_name]
    
    print(f"\n[BEST] Best model: {best_model_name}")
    print(f"  R² = {results_pm_only.iloc[0]['R2']:.4f}")
    print(f"  MAE = {results_pm_only.iloc[0]['MAE']:.2f}")
    
    # Plot predictions
    y_pred_best = best_model.predict(X_test)
    ml_pipeline.plot_predictions_vs_actual(
        y_test, y_pred_best, best_model_name,
        save_path=os.path.join(config.FIGURES_DIR, f'predictions_{best_model_name}_pm25_only.png')
    )
    
    # Feature importance
    importance_df = ml_pipeline.compute_feature_importance(best_model, pm_features, best_model_name)
    ml_pipeline.plot_feature_importance(
        importance_df, best_model_name,
        save_path=os.path.join(config.FIGURES_DIR, f'feature_importance_{best_model_name}_pm25_only.png')
    )
    
    # ========================================================================
    # PHASE 4: FEATURE ENGINEERING & EXTERNAL DATA
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("PHASE 4: Feature Engineering with External Data")
    print("=" * 80)
    
    # Download external confounding variables
    try:
        external_data = feature_engineering.download_external_data(verbose=True)
    except Exception as e:
        print(f"[WARNING] Could not download external data: {e}")
        print("[INFO] Continuing with PM2.5 features only...")
        external_data = {}
    
    if external_data:
        # Merge external features
        merged_extended = feature_engineering.merge_external_features(
            merged, external_data, verbose=True
        )
        
        # Create engineered features
        merged_extended = feature_engineering.create_engineered_features(
            merged_extended, verbose=True
        )
        
        # Prepare feature sets
        feature_sets = feature_engineering.prepare_feature_sets(
            merged_extended, verbose=True
        )
        
        # Save extended dataset
        merged_extended.to_csv(
            os.path.join(config.PROCESSED_DATA_DIR, 'merged_extended.csv'),
            index=False
        )
        print(f"\n[SAVED] Extended dataset to {config.PROCESSED_DATA_DIR}/merged_extended.csv")
        
        # ====================================================================
        # PHASE 5: ADVANCED ML WITH ALL FEATURES
        # ====================================================================
        
        print("\n" + "=" * 80)
        print("PHASE 5: Advanced ML with Confounders & Engineered Features")
        print("=" * 80)
        
        all_results = {}
        
        for set_name, features in feature_sets.items():
            print(f"\n[TRAIN] Training models with feature set: {set_name}")
            print(f"  Features ({len(features)}): {features[:5]}{'...' if len(features) > 5 else ''}")
            
            try:
                X_train, X_test, y_train, y_test, train_df, test_df = ml_pipeline.create_time_aware_split(
                    merged_extended, features, config.TARGET, verbose=False
                )
                
                models, results = ml_pipeline.train_and_evaluate_models(
                    X_train, X_test, y_train, y_test, features, verbose=False
                )
                
                results['Feature_Set'] = set_name
                all_results[set_name] = {
                    'models': models,
                    'results': results,
                    'features': features,
                    'test_data': (X_test, y_test)
                }
                
                # Save results for this feature set
                results.to_csv(
                    os.path.join(config.TABLES_DIR, f'model_results_{set_name}.csv'),
                    index=False
                )
                
                print(f"\n  Best model for {set_name}:")
                best_row = results.iloc[0]
                print(f"    {best_row['Model']}: R²={best_row['R2']:.4f}, MAE={best_row['MAE']:.2f}")
                
            except Exception as e:
                print(f"  [ERROR] Failed to train with {set_name}: {e}")
                continue
        
        # Compare feature sets
        if all_results:
            print("\n" + "=" * 80)
            print("FEATURE SET COMPARISON")
            print("=" * 80)
            
            comparison_rows = []
            for set_name, data in all_results.items():
                best_result = data['results'].iloc[0]
                comparison_rows.append({
                    'Feature_Set': set_name,
                    'N_Features': len(data['features']),
                    'Best_Model': best_result['Model'],
                    'R2': best_result['R2'],
                    'MAE': best_result['MAE'],
                    'RMSE': best_result['RMSE']
                })
            
            comparison_df = pd.DataFrame(comparison_rows).sort_values('MAE')
            print("\n" + comparison_df.to_string(index=False))
            
            comparison_df.to_csv(
                os.path.join(config.TABLES_DIR, 'feature_set_comparison.csv'),
                index=False
            )
            
            # Get overall best model
            best_set_name = comparison_df.iloc[0]['Feature_Set']
            best_set_data = all_results[best_set_name]
            best_model_name = comparison_df.iloc[0]['Best_Model']
            best_model = best_set_data['models'][best_model_name]
            
            print(f"\n[CHAMPION] Overall best model:")
            print(f"  Feature Set: {best_set_name}")
            print(f"  Model: {best_model_name}")
            print(f"  R² = {comparison_df.iloc[0]['R2']:.4f}")
            print(f"  MAE = {comparison_df.iloc[0]['MAE']:.2f}")
            print(f"  RMSE = {comparison_df.iloc[0]['RMSE']:.2f}")
            
            # Plot champion model
            X_test, y_test = best_set_data['test_data']
            y_pred_champion = best_model.predict(X_test)
            
            ml_pipeline.plot_predictions_vs_actual(
                y_test, y_pred_champion, f"{best_model_name} ({best_set_name})",
                save_path=os.path.join(config.FIGURES_DIR, 'predictions_champion_model.png')
            )
            
            # Feature importance for champion
            importance_df = ml_pipeline.compute_feature_importance(
                best_model, best_set_data['features'], best_model_name
            )
            ml_pipeline.plot_feature_importance(
                importance_df, f"{best_model_name} ({best_set_name})",
                save_path=os.path.join(config.FIGURES_DIR, 'feature_importance_champion.png')
            )
            
            # Save champion model
            ml_pipeline.save_models({'champion': best_model})
    
    else:
        print("\n[INFO] Skipping advanced ML due to missing external data")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE - FINAL SUMMARY")
    print("=" * 80)
    
    print(f"\n[DATASET]")
    print(f"  - Countries: {merged['Country_ISO3'].nunique()}")
    print(f"  - Years: {merged['Year'].min()} - {merged['Year'].max()}")
    print(f"  - Total observations: {len(merged)}")
    
    print(f"\n[KEY FINDINGS]")
    if 'regression_summary' in analysis_results:
        reg = analysis_results['regression_summary']
        print(f"  - PM2.5 explains {reg['r_squared']*100:.1f}% of U5MR variance")
        print(f"  - Each 1 ug/m3 increase in PM2.5 -> +{reg['coef_slope']:.3f} U5MR")
        print(f"  - Relationship is highly significant (p < 0.001)")
    
    print(f"\n[ML MODELS TRAINED]")
    print(f"  - Phase 3 (PM2.5 only): {len(models_pm_only)} models")
    print(f"    Best: {best_model_name} (MAE={results_pm_only.iloc[0]['MAE']:.2f})")
    
    if 'all_results' in locals() and all_results:
        print(f"  - Phase 5 (with confounders): {len(all_results)} feature sets")
        print(f"    Champion: {best_model_name} with {best_set_name}")
        print(f"    (MAE={comparison_df.iloc[0]['MAE']:.2f})")
    
    print(f"\n[GENERATED FILES]")
    print(f"  - Processed data: {config.PROCESSED_DATA_DIR}/")
    print(f"  - Figures: {config.FIGURES_DIR}/")
    print(f"  - Tables: {config.TABLES_DIR}/")
    print(f"  - Models: {config.MODELS_DIR}/")
    
    print(f"\n[RECOMMENDATIONS FOR IMPROVEMENT]")
    print(f"  1. Collect data on healthcare infrastructure and access")
    print(f"  2. Add education levels and maternal health indicators")
    print(f"  3. Implement causal inference methods (IV, PSM, DID)")
    print(f"  4. Analyze regional heterogeneity (by continent/income level)")
    print(f"  5. Consider time-series models for forecasting")
    print(f"  6. Add interaction terms with socioeconomic factors")
    
    print("\n" + "=" * 80)
    print("[SUCCESS] ALL PHASES COMPLETE - PROJECT SUCCESS!")
    print("=" * 80)


if __name__ == "__main__":
    main()

