"""
Advanced Analysis Script
Includes SHAP analysis, geographic visualizations, and causal inference
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import os
import config
from src import data_processing, ml_pipeline, interpretability, geographic_viz, causal_inference


def main():
    print("=" * 80)
    print("ADVANCED ANALYSIS - SHAP, Geographic Maps, Causal Inference")
    print("=" * 80)
    
    # Load data
    print("\n[LOAD] Loading processed data...")
    try:
        data = data_processing.load_processed_data(verbose=False)
        merged = data['merged']
        print(f"[OK] Loaded data: {merged.shape}")
    except:
        print("[ERROR] Could not load data. Please run main_complete.py first.")
        return
    
    # ========================================================================
    # 1. GEOGRAPHIC VISUALIZATIONS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("1. GEOGRAPHIC VISUALIZATIONS")
    print("=" * 80)
    
    geographic_viz.generate_all_geographic_visualizations(merged, verbose=True)
    
    # ========================================================================
    # 2. SHAP ANALYSIS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("2. SHAP INTERPRETABILITY ANALYSIS")
    print("=" * 80)
    
    # Prepare data
    pm_features = [c for c in config.PM25_FEATURES if c in merged.columns]
    
    print("[SPLIT] Creating train/test split for SHAP...")
    X_train, X_test, y_train, y_test, train_df, test_df = ml_pipeline.create_time_aware_split(
        merged, pm_features, config.TARGET, verbose=False
    )
    
    # Load champion model
    champion_path = os.path.join(config.MODELS_DIR, 'champion_model.pkl')
    if os.path.exists(champion_path):
        print(f"[LOAD] Loading champion model from {champion_path}")
        champion_model = ml_pipeline.load_model('champion')
        
        # Generate SHAP report
        shap_results = interpretability.generate_shap_report(
            champion_model, X_train, X_test, pm_features,
            'Champion_RandomForest', verbose=True
        )
    else:
        print("[INFO] Champion model not found. Training new model...")
        
        # Train a new Random Forest model
        from sklearn.ensemble import RandomForestRegressor
        rf_model = ml_pipeline.build_model_pipeline(
            RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            pm_features
        )
        rf_model.fit(X_train, y_train)
        
        # Generate SHAP report
        shap_results = interpretability.generate_shap_report(
            rf_model, X_train, X_test, pm_features,
            'RandomForest', verbose=True
        )
    
    # ========================================================================
    # 3. CAUSAL INFERENCE
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("3. CAUSAL INFERENCE ANALYSIS")
    print("=" * 80)
    
    # Load extended data if available
    extended_path = os.path.join(config.PROCESSED_DATA_DIR, 'merged_extended.csv')
    if os.path.exists(extended_path):
        print(f"[LOAD] Loading extended dataset with confounders...")
        merged_extended = pd.read_csv(extended_path)
        print(f"[OK] Loaded extended data: {merged_extended.shape}")
        
        # Run causal inference
        causal_results = causal_inference.analyze_causality(merged_extended, verbose=True)
        
        # Save causal inference summary
        if causal_results:
            summary = []
            
            if 'psm' in causal_results and causal_results['psm']:
                psm = causal_results['psm']
                summary.append({
                    'Method': 'Propensity Score Matching',
                    'Effect': psm.get('ate', np.nan),
                    'CI_Lower': psm.get('ci_95', (np.nan, np.nan))[0],
                    'CI_Upper': psm.get('ci_95', (np.nan, np.nan))[1],
                    'N_Matched': psm.get('n_matched', 0)
                })
            
            if 'did' in causal_results and causal_results['did']:
                did = causal_results['did']
                summary.append({
                    'Method': 'Difference-in-Differences',
                    'Effect': did.get('did_effect', np.nan),
                    'Treated_Change': did.get('treated_change', np.nan),
                    'Control_Change': did.get('control_change', np.nan),
                    'N_Matched': np.nan
                })
            
            if summary:
                summary_df = pd.DataFrame(summary)
                summary_path = os.path.join(config.TABLES_DIR, 'causal_inference_summary.csv')
                summary_df.to_csv(summary_path, index=False)
                print(f"\n[SAVED] Causal inference summary to {summary_path}")
                print("\nCausal Inference Results:")
                print(summary_df.to_string(index=False))
    else:
        print("[INFO] Extended dataset not found. Causal inference requires confounding variables.")
        print("      Run main_complete.py to download World Bank data.")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("ADVANCED ANALYSIS COMPLETE!")
    print("=" * 80)
    
    print("\n[GENERATED FILES]")
    print(f"\nGeographic Maps (HTML):")
    print(f"  - {config.FIGURES_DIR}/map_pm25.html")
    print(f"  - {config.FIGURES_DIR}/map_u5mr.html")
    print(f"  - {config.FIGURES_DIR}/map_pm25_animated.html")
    print(f"  - {config.FIGURES_DIR}/map_bubble_pm25_u5mr.html")
    print(f"  - {config.FIGURES_DIR}/map_regional_pm25.html")
    
    print(f"\nSHAP Analysis:")
    print(f"  - {config.FIGURES_DIR}/shap_summary_*.png")
    print(f"  - {config.FIGURES_DIR}/shap_waterfall_*.png")
    print(f"  - {config.FIGURES_DIR}/shap_dependence_*.png")
    print(f"  - {config.TABLES_DIR}/shap_importance_*.csv")
    
    print(f"\nCausal Inference:")
    print(f"  - {config.TABLES_DIR}/causal_inference_summary.csv")
    print(f"  - {config.TABLES_DIR}/psm_matched_pairs.csv")
    
    print("\n[NEXT STEP]")
    print("Run the Streamlit dashboard:")
    print("  streamlit run streamlit_dashboard.py")
    print("=" * 80)


if __name__ == "__main__":
    main()

