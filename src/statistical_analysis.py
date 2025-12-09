"""
Statistical Analysis Module
Functions for performing statistical tests and regression analysis
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
import config
import os


def compute_summary_statistics(df: pd.DataFrame, 
                               columns: list,
                               save_path: str = None) -> pd.DataFrame:
    """
    Compute and save summary statistics for specified columns.
    
    Args:
        df: DataFrame
        columns: List of columns to summarize
        save_path: Path to save CSV (optional)
        
    Returns:
        DataFrame with summary statistics
    """
    summary = df[columns].describe()
    
    if save_path:
        summary.to_csv(save_path)
        print(f"[SAVED] Summary statistics to {save_path}")
    
    return summary


def simple_linear_regression(df: pd.DataFrame,
                             x_col: str,
                             y_col: str,
                             save_path: str = None) -> Tuple[object, Dict]:
    """
    Perform simple linear regression: y ~ x
    
    Args:
        df: DataFrame
        x_col: Independent variable column
        y_col: Dependent variable column
        save_path: Path to save regression summary
        
    Returns:
        Tuple of (fitted_model, summary_dict)
    """
    try:
        import statsmodels.api as sm
        
        # Prepare data
        analysis_df = df[[x_col, y_col]].dropna()
        X = analysis_df[[x_col]]
        y = analysis_df[y_col]
        X = sm.add_constant(X)
        
        # Fit model
        model = sm.OLS(y, X, missing="drop").fit()
        
        # Extract key metrics
        summary_dict = {
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'f_statistic': model.fvalue,
            'f_pvalue': model.f_pvalue,
            'coef_intercept': model.params['const'],
            'coef_slope': model.params[x_col],
            'pvalue_intercept': model.pvalues['const'],
            'pvalue_slope': model.pvalues[x_col],
            'n_observations': int(model.nobs)
        }
        
        # Save summary
        if save_path:
            with open(save_path, 'w') as f:
                f.write(str(model.summary()))
            print(f"[SAVED] Regression summary to {save_path}")
        
        return model, summary_dict
        
    except ImportError:
        print("[WARNING] statsmodels not installed. Cannot perform regression.")
        return None, {}


def compute_correlations(df: pd.DataFrame, 
                        columns: list) -> pd.DataFrame:
    """
    Compute correlation matrix for specified columns.
    
    Args:
        df: DataFrame
        columns: List of columns
        
    Returns:
        Correlation matrix DataFrame
    """
    return df[columns].corr()


def pearson_correlation_test(df: pd.DataFrame,
                             col1: str,
                             col2: str) -> Dict:
    """
    Perform Pearson correlation test between two columns.
    
    Args:
        df: DataFrame
        col1: First column
        col2: Second column
        
    Returns:
        Dictionary with correlation coefficient and p-value
    """
    try:
        from scipy.stats import pearsonr
        
        data = df[[col1, col2]].dropna()
        corr, pvalue = pearsonr(data[col1], data[col2])
        
        return {
            'correlation': corr,
            'p_value': pvalue,
            'n_observations': len(data),
            'significant': pvalue < 0.05
        }
    except ImportError:
        print("[WARNING] scipy not installed. Cannot perform correlation test.")
        return {}


def analyze_dataset(merged_df: pd.DataFrame, verbose: bool = True) -> Dict:
    """
    Perform comprehensive statistical analysis on merged dataset.
    
    Args:
        merged_df: Merged PM2.5 and U5MR DataFrame
        verbose: Print results
        
    Returns:
        Dictionary with all analysis results
    """
    results = {}
    
    if verbose:
        print("[ANALYSIS] Performing statistical analysis")
    
    # Summary statistics
    pm_cols = [c for c in config.PM25_FEATURES if c in merged_df.columns]
    summary_cols = pm_cols + [config.TARGET]
    
    summary_stats = compute_summary_statistics(
        merged_df,
        summary_cols,
        save_path=os.path.join(config.TABLES_DIR, 'summary_statistics.csv')
    )
    results['summary_statistics'] = summary_stats
    
    if verbose:
        print("\nSummary Statistics:")
        print(summary_stats.to_string())
    
    # Correlation matrix
    if pm_cols and config.TARGET in merged_df.columns:
        corr_matrix = compute_correlations(merged_df, summary_cols)
        results['correlation_matrix'] = corr_matrix
        
        if verbose:
            print("\nCorrelation Matrix:")
            print(corr_matrix.round(3).to_string())
    
    # Linear regression: U5MR ~ PM2.5 Total
    if 'PM25_Total_ugm3' in merged_df.columns and config.TARGET in merged_df.columns:
        model, summary_dict = simple_linear_regression(
            merged_df,
            'PM25_Total_ugm3',
            config.TARGET,
            save_path=os.path.join(config.TABLES_DIR, 'regression_summary.txt')
        )
        results['regression_model'] = model
        results['regression_summary'] = summary_dict
        
        if verbose and summary_dict:
            print(f"\nLinear Regression: {config.TARGET} ~ PM25_Total_ugm3")
            print(f"  R-squared: {summary_dict['r_squared']:.4f}")
            print(f"  Slope: {summary_dict['coef_slope']:.4f} (p={summary_dict['pvalue_slope']:.4e})")
            print(f"  Intercept: {summary_dict['coef_intercept']:.4f}")
    
    # Pearson correlations for all PM2.5 measures with U5MR
    if verbose:
        print("\nPearson Correlations with U5MR:")
    
    for pm_col in pm_cols:
        if pm_col in merged_df.columns:
            corr_result = pearson_correlation_test(merged_df, pm_col, config.TARGET)
            results[f'correlation_{pm_col}'] = corr_result
            
            if verbose and corr_result:
                sig_marker = "***" if corr_result['significant'] else ""
                print(f"  {pm_col}: r={corr_result['correlation']:.3f}, "
                      f"p={corr_result['p_value']:.4e} {sig_marker}")
    
    if verbose:
        print("\n[DONE] Statistical analysis complete")
    
    return results

