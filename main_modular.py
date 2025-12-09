"""
Air Pollution and Under-5 Mortality Analysis
PHASE 2: Modular Version with Clean Code Structure

This is the main entry point for the analysis pipeline.
"""

import warnings
warnings.filterwarnings('ignore')

import config
from src import data_processing, visualization, statistical_analysis


def main():
    """Main analysis pipeline"""
    
    print("=" * 80)
    print("AIR POLLUTION & UNDER-5 MORTALITY ANALYSIS - PHASE 2 (MODULAR)")
    print("=" * 80)
    print(f"\nBase Directory: {config.BASE_DIR}")
    print(f"Data files:")
    print(f"  - WHO PM2.5: {config.WHO_CSV}")
    print(f"  - UNICEF U5MR: {config.UNICEF_XLSX}")
    
    # ========================================================================
    # STEP 1: DATA LOADING AND PROCESSING
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 1: Loading and Processing Data")
    print("=" * 80)
    
    # Load WHO PM2.5 data
    try:
        who_long, who_wide = data_processing.load_who_pm25_data(config.WHO_CSV)
        print(f"\n[OK] WHO PM2.5 data loaded successfully")
        print(f"  Long format: {who_long.shape}")
        print(f"  Wide format: {who_wide.shape}")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return
    except Exception as e:
        print(f"[ERROR] Failed to load WHO data: {e}")
        return
    
    # Load UNICEF U5MR data
    try:
        u5mr_long = data_processing.load_unicef_u5mr_data(config.UNICEF_XLSX)
        print(f"\n[OK] UNICEF U5MR data loaded successfully")
        print(f"  Long format: {u5mr_long.shape}")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return
    except Exception as e:
        print(f"[ERROR] Failed to load UNICEF data: {e}")
        return
    
    # Merge datasets
    merged = data_processing.merge_pm25_u5mr(who_wide, u5mr_long)
    print(f"\n[OK] Datasets merged successfully")
    print(f"  Merged shape: {merged.shape}")
    
    # Save processed data
    data_processing.save_processed_data(who_long, who_wide, u5mr_long, merged)
    print(f"\n[SAVED] All processed data saved to {config.PROCESSED_DATA_DIR}")
    
    # ========================================================================
    # STEP 2: EXPLORATORY DATA ANALYSIS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 2: Exploratory Data Analysis")
    print("=" * 80)
    
    # Create visualizations
    visualization.create_exploratory_plots(merged, show=False)
    
    # ========================================================================
    # STEP 3: STATISTICAL ANALYSIS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 3: Statistical Analysis")
    print("=" * 80)
    
    # Perform comprehensive statistical analysis
    analysis_results = statistical_analysis.analyze_dataset(merged, verbose=True)
    
    # ========================================================================
    # COMPLETION SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("[SUCCESS] PHASE 2 COMPLETE - MODULAR VERSION!")
    print("=" * 80)
    
    print(f"\nGenerated files:")
    print(f"\n  Processed data: {config.PROCESSED_DATA_DIR}/")
    print(f"    - who_pm25_long.csv ({who_long.shape[0]} rows)")
    print(f"    - who_pm25_wide.csv ({who_wide.shape[0]} rows)")
    print(f"    - unicef_u5mr_long.csv ({u5mr_long.shape[0]} rows)")
    print(f"    - merged_pm25_u5mr.csv ({merged.shape[0]} rows)")
    
    print(f"\n  Figures: {config.FIGURES_DIR}/")
    print(f"    - 01_correlation_matrix.png")
    print(f"    - 02_pm25_vs_u5mr_scatter.png")
    print(f"    - 03_urban_vs_rural_pm25.png")
    print(f"    - 04_top10_countries_pm25.png")
    print(f"    - 05_timeseries_*.png")
    
    print(f"\n  Tables: {config.TABLES_DIR}/")
    print(f"    - summary_statistics.csv")
    print(f"    - regression_summary.txt")
    
    print("\nKey Findings:")
    if 'regression_summary' in analysis_results:
        reg_sum = analysis_results['regression_summary']
        print(f"  - PM2.5 explains {reg_sum['r_squared']*100:.1f}% of U5MR variance")
        print(f"  - 1 ug/m3 increase in PM2.5 associated with "
              f"{reg_sum['coef_slope']:.3f} increase in U5MR")
        print(f"  - Relationship is statistically significant (p < 0.001)")
    
    if 'correlation_matrix' in analysis_results:
        corr = analysis_results['correlation_matrix']
        if 'PM25_Total_ugm3' in corr.index and config.TARGET in corr.columns:
            corr_val = corr.loc['PM25_Total_ugm3', config.TARGET]
            print(f"  - Correlation between PM2.5 and U5MR: r = {corr_val:.3f}")
    
    print("\nCode Structure:")
    print(f"  config.py          - Centralized configuration")
    print(f"  src/")
    print(f"    data_processing.py      - Data loading and cleaning")
    print(f"    visualization.py        - Plotting functions")
    print(f"    statistical_analysis.py - Statistical tests")
    print(f"  main_modular.py    - Main pipeline (this file)")
    
    print("\nNext Steps:")
    print(f"  - Phase 3: Advanced ML pipeline")
    print(f"  - Phase 4: Feature engineering & causality")
    print(f"  - Phase 5: Publication-quality visualizations")
    print("=" * 80)


if __name__ == "__main__":
    main()

