"""
Causal Inference Module
Implement propensity score matching and other causal methods
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
import os
import config


def compute_propensity_scores(df: pd.DataFrame,
                              treatment_col: str,
                              confounders: list,
                              verbose: bool = True) -> pd.DataFrame:
    """
    Compute propensity scores for treatment assignment.
    
    Args:
        df: DataFrame
        treatment_col: Binary treatment column
        confounders: List of confounder columns
        verbose: Print progress
        
    Returns:
        DataFrame with propensity scores
    """
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        
        if verbose:
            print(f"[PSM] Computing propensity scores")
        
        # Prepare data
        df_clean = df.dropna(subset=[treatment_col] + confounders).copy()
        X = df_clean[confounders]
        y = df_clean[treatment_col]
        
        # Standardize confounders
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Fit logistic regression
        model = LogisticRegression(random_state=config.RANDOM_SEED, max_iter=1000)
        model.fit(X_scaled, y)
        
        # Predict propensity scores
        df_clean['propensity_score'] = model.predict_proba(X_scaled)[:, 1]
        
        if verbose:
            print(f"  Computed for {len(df_clean)} observations")
            print(f"  Mean propensity score: {df_clean['propensity_score'].mean():.3f}")
        
        return df_clean
        
    except Exception as e:
        print(f"[ERROR] Propensity score computation failed: {e}")
        return df


def propensity_score_matching(df: pd.DataFrame,
                              treatment_col: str,
                              outcome_col: str,
                              confounders: list,
                              caliper: float = 0.1,
                              verbose: bool = True) -> Dict:
    """
    Perform propensity score matching.
    
    Args:
        df: DataFrame with treatment and outcome
        treatment_col: Binary treatment variable
        outcome_col: Outcome variable
        confounders: List of confounding variables
        caliper: Maximum allowed difference in propensity scores
        verbose: Print results
        
    Returns:
        Dictionary with matching results
    """
    if verbose:
        print(f"\n[PSM] Propensity Score Matching Analysis")
        print(f"  Treatment: {treatment_col}")
        print(f"  Outcome: {outcome_col}")
        print(f"  Confounders: {confounders}")
    
    # Compute propensity scores
    df_ps = compute_propensity_scores(df, treatment_col, confounders, verbose=False)
    
    # Separate treated and control
    treated = df_ps[df_ps[treatment_col] == 1].copy()
    control = df_ps[df_ps[treatment_col] == 0].copy()
    
    if verbose:
        print(f"  Treated: {len(treated)}, Control: {len(control)}")
    
    # Match each treated to nearest control within caliper
    matched_pairs = []
    
    for idx, treated_row in treated.iterrows():
        ps_treated = treated_row['propensity_score']
        
        # Find controls within caliper
        candidates = control[
            abs(control['propensity_score'] - ps_treated) <= caliper
        ].copy()
        
        if len(candidates) > 0:
            # Find nearest match
            candidates['ps_diff'] = abs(candidates['propensity_score'] - ps_treated)
            best_match = candidates.nsmallest(1, 'ps_diff')
            
            matched_pairs.append({
                'treated_idx': idx,
                'control_idx': best_match.index[0],
                'treated_outcome': treated_row[outcome_col],
                'control_outcome': best_match[outcome_col].iloc[0],
                'ps_treated': ps_treated,
                'ps_control': best_match['propensity_score'].iloc[0]
            })
    
    matched_df = pd.DataFrame(matched_pairs)
    
    if len(matched_df) == 0:
        print("[WARNING] No matches found within caliper")
        return {}
    
    # Calculate treatment effect
    matched_df['treatment_effect'] = (matched_df['treated_outcome'] - 
                                      matched_df['control_outcome'])
    
    ate = matched_df['treatment_effect'].mean()
    se = matched_df['treatment_effect'].std() / np.sqrt(len(matched_df))
    ci_lower = ate - 1.96 * se
    ci_upper = ate + 1.96 * se
    
    results = {
        'n_matched': len(matched_df),
        'n_treated_total': len(treated),
        'n_control_total': len(control),
        'matching_rate': len(matched_df) / len(treated),
        'ate': ate,
        'se': se,
        'ci_95': (ci_lower, ci_upper),
        'p_value': 2 * (1 - stats.norm.cdf(abs(ate / se))) if se > 0 else None,
        'matched_data': matched_df
    }
    
    if verbose:
        print(f"\n[RESULTS] PSM Analysis:")
        print(f"  Matched pairs: {results['n_matched']} ({results['matching_rate']*100:.1f}%)")
        print(f"  Average Treatment Effect (ATE): {ate:.4f}")
        print(f"  95% CI: ({ci_lower:.4f}, {ci_upper:.4f})")
        if results['p_value']:
            print(f"  P-value: {results['p_value']:.4f}")
    
    # Save results
    matched_df.to_csv(
        os.path.join(config.TABLES_DIR, 'psm_matched_pairs.csv'),
        index=False
    )
    print(f"[SAVED] Matched pairs to {config.TABLES_DIR}")
    
    return results


def difference_in_differences(df: pd.DataFrame,
                             outcome_col: str,
                             treatment_col: str,
                             time_col: str,
                             pre_period: int,
                             post_period: int,
                             verbose: bool = True) -> Dict:
    """
    Perform difference-in-differences analysis.
    
    Args:
        df: DataFrame with panel data
        outcome_col: Outcome variable
        treatment_col: Binary treatment indicator
        time_col: Time column (e.g., Year)
        pre_period: Pre-treatment time value
        post_period: Post-treatment time value
        verbose: Print results
        
    Returns:
        Dictionary with DiD results
    """
    if verbose:
        print(f"\n[DiD] Difference-in-Differences Analysis")
    
    # Filter to pre and post periods
    df_analysis = df[df[time_col].isin([pre_period, post_period])].copy()
    
    # Create time dummy (0 = pre, 1 = post)
    df_analysis['post'] = (df_analysis[time_col] == post_period).astype(int)
    
    # Calculate means
    treated_pre = df_analysis[(df_analysis[treatment_col] == 1) & 
                             (df_analysis['post'] == 0)][outcome_col].mean()
    treated_post = df_analysis[(df_analysis[treatment_col] == 1) & 
                              (df_analysis['post'] == 1)][outcome_col].mean()
    control_pre = df_analysis[(df_analysis[treatment_col] == 0) & 
                             (df_analysis['post'] == 0)][outcome_col].mean()
    control_post = df_analysis[(df_analysis[treatment_col] == 0) & 
                              (df_analysis['post'] == 1)][outcome_col].mean()
    
    # Calculate DiD estimator
    treated_diff = treated_post - treated_pre
    control_diff = control_post - control_pre
    did_effect = treated_diff - control_diff
    
    results = {
        'treated_pre': treated_pre,
        'treated_post': treated_post,
        'control_pre': control_pre,
        'control_post': control_post,
        'treated_change': treated_diff,
        'control_change': control_diff,
        'did_effect': did_effect
    }
    
    if verbose:
        print(f"\n[RESULTS] DiD Analysis:")
        print(f"  Treated: {treated_pre:.2f} → {treated_post:.2f} (Δ={treated_diff:.2f})")
        print(f"  Control: {control_pre:.2f} → {control_post:.2f} (Δ={control_diff:.2f})")
        print(f"  DiD Effect: {did_effect:.2f}")
    
    return results


def analyze_causality(df: pd.DataFrame, verbose: bool = True) -> Dict:
    """
    Perform comprehensive causal analysis on PM2.5 and U5MR.
    
    Args:
        df: Merged dataset
        verbose: Print results
        
    Returns:
        Dictionary with all causal inference results
    """
    if verbose:
        print("\n" + "="*80)
        print("CAUSAL INFERENCE ANALYSIS")
        print("="*80)
    
    results = {}
    
    # 1. Create high pollution treatment variable
    if 'PM25_Total_ugm3' in df.columns:
        df['high_pollution'] = (df['PM25_Total_ugm3'] > 
                                df['PM25_Total_ugm3'].median()).astype(int)
        
        # Try PSM if we have confounders
        confounders = [c for c in ['gdp_pc', 'urban_pct', 'fertility', 'health_exp'] 
                      if c in df.columns]
        
        if len(confounders) >= 2:
            try:
                psm_results = propensity_score_matching(
                    df, 'high_pollution', 'U5MR_per_1000',
                    confounders[:2],  # Use first 2 confounders
                    verbose=verbose
                )
                results['psm'] = psm_results
            except Exception as e:
                if verbose:
                    print(f"[INFO] PSM analysis skipped: {e}")
        
        # 2. DiD analysis if we have time series
        if 'Year' in df.columns and df['Year'].nunique() >= 2:
            years = sorted(df['Year'].unique())
            if len(years) >= 2:
                try:
                    did_results = difference_in_differences(
                        df, 'U5MR_per_1000', 'high_pollution', 'Year',
                        pre_period=years[0],
                        post_period=years[-1],
                        verbose=verbose
                    )
                    results['did'] = did_results
                except Exception as e:
                    if verbose:
                        print(f"[INFO] DiD analysis skipped: {e}")
    
    if verbose and results:
        print("\n[DONE] Causal inference analysis complete")
    elif verbose:
        print("[INFO] Insufficient data for causal inference")
    
    return results


# Import scipy.stats for p-value calculation
try:
    from scipy import stats
except ImportError:
    stats = None

