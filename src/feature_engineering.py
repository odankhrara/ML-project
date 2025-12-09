"""
Feature Engineering Module
Functions for creating additional features and downloading external data
"""

import pandas as pd
import numpy as np
import os
import requests
import zipfile
import io
from typing import Optional, List, Tuple, Dict
import config


def download_worldbank_indicator(indicator_code: str,
                                 save_path: str,
                                 verbose: bool = True) -> bool:
    """
    Download World Bank indicator data.
    
    Args:
        indicator_code: World Bank indicator code (e.g., 'NY.GDP.PCAP.KD')
        save_path: Path to save ZIP file
        verbose: Print progress
        
    Returns:
        True if successful, False otherwise
    """
    try:
        url = f"https://api.worldbank.org/v2/en/indicator/{indicator_code}?downloadformat=csv"
        
        if verbose:
            print(f"  Downloading {indicator_code}...", end=' ')
        
        response = requests.get(url, stream=True, allow_redirects=True, timeout=120)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        
        # Verify it's a valid ZIP file
        if not zipfile.is_zipfile(save_path):
            if verbose:
                print("FAILED (not a valid ZIP)")
            return False
        
        if verbose:
            print("OK")
        return True
        
    except Exception as e:
        if verbose:
            print(f"FAILED ({str(e)})")
        return False


def load_worldbank_data(zip_path: str, 
                       indicator_name: str,
                       verbose: bool = True) -> Optional[pd.DataFrame]:
    """
    Load World Bank data from ZIP file into long format.
    
    Args:
        zip_path: Path to ZIP file
        indicator_name: Name for the indicator column
        verbose: Print progress
        
    Returns:
        DataFrame with columns: Country_ISO3, Year, {indicator_name}
    """
    try:
        with zipfile.ZipFile(zip_path) as zf:
            # Find the main CSV file (usually starts with 'API')
            csv_files = [n for n in zf.namelist() 
                        if n.lower().endswith('.csv') 
                        and 'api' in n.lower() 
                        and 'metadata' not in n.lower()]
            
            if not csv_files:
                csv_files = [n for n in zf.namelist() if n.lower().endswith('.csv')]
            
            if not csv_files:
                return None
            
            # Read the CSV (skip first 4 rows which are metadata)
            with zf.open(csv_files[0]) as f:
                df = pd.read_csv(f, skiprows=4, encoding='latin-1')
        
        # Clean column names
        df.columns = [c.strip() for c in df.columns]
        
        # Rename Country Code to Country_ISO3
        if 'Country Code' not in df.columns:
            if verbose:
                print(f"    [WARNING] No 'Country Code' column found")
            return None
        
        df = df.rename(columns={'Country Code': 'Country_ISO3'})
        
        # Identify year columns
        year_cols = [c for c in df.columns if str(c).isdigit()]
        
        # Melt to long format
        df_long = df.melt(
            id_vars=['Country_ISO3'],
            value_vars=year_cols,
            var_name='Year',
            value_name=indicator_name
        )
        
        df_long['Year'] = pd.to_numeric(df_long['Year'], errors='coerce')
        df_long[indicator_name] = pd.to_numeric(df_long[indicator_name], errors='coerce')
        df_long = df_long.dropna(subset=[indicator_name])
        
        if verbose:
            print(f"    Loaded {len(df_long)} observations")
        
        return df_long
        
    except Exception as e:
        if verbose:
            print(f"    [ERROR] Failed to load: {e}")
        return None


def download_external_data(verbose: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Download and load external confounding variables from World Bank.
    
    Args:
        verbose: Print progress
        
    Returns:
        Dictionary of DataFrames with keys: gdp_pc, urban_pct, fertility, health_exp
    """
    if verbose:
        print("[DOWNLOAD] Fetching external confounding variables from World Bank")
    
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    
    # Define indicators
    indicators = {
        'gdp_pc': {
            'code': 'NY.GDP.PCAP.KD',
            'name': 'gdp_pc',
            'description': 'GDP per capita (constant 2015 US$)'
        },
        'urban_pct': {
            'code': 'SP.URB.TOTL.IN.ZS',
            'name': 'urban_pct',
            'description': 'Urban population (% of total)'
        },
        'fertility': {
            'code': 'SP.DYN.TFRT.IN',
            'name': 'fertility',
            'description': 'Fertility rate (births per woman)'
        },
        'health_exp': {
            'code': 'SH.XPD.CHEX.PC.CD',
            'name': 'health_exp',
            'description': 'Health expenditure per capita (current US$)'
        }
    }
    
    datasets = {}
    
    for key, info in indicators.items():
        zip_path = os.path.join(config.RAW_DATA_DIR, f"wb_{key}.zip")
        
        # Download if not already present
        if not os.path.exists(zip_path):
            success = download_worldbank_indicator(info['code'], zip_path, verbose)
            if not success:
                if verbose:
                    print(f"    [SKIP] {info['description']}")
                continue
        else:
            if verbose:
                print(f"  Using cached {info['code']}... OK")
        
        # Load data
        df = load_worldbank_data(zip_path, info['name'], verbose)
        if df is not None:
            datasets[key] = df
    
    if verbose:
        print(f"\n[OK] Loaded {len(datasets)} external datasets")
    
    return datasets


def merge_external_features(base_df: pd.DataFrame,
                           external_data: Dict[str, pd.DataFrame],
                           verbose: bool = True) -> pd.DataFrame:
    """
    Merge external features with base dataset.
    
    Args:
        base_df: Base DataFrame (must have Country_ISO3 and Year)
        external_data: Dictionary of external DataFrames
        verbose: Print progress
        
    Returns:
        Merged DataFrame
    """
    if verbose:
        print(f"[MERGE] Merging external features")
    
    df_merged = base_df.copy()
    
    for name, ext_df in external_data.items():
        df_merged = pd.merge(
            df_merged,
            ext_df,
            on=['Country_ISO3', 'Year'],
            how='left'
        )
        
        if verbose:
            n_matched = df_merged[name].notna().sum()
            print(f"  {name}: {n_matched}/{len(df_merged)} matched")
    
    return df_merged


def create_engineered_features(df: pd.DataFrame,
                               verbose: bool = True) -> pd.DataFrame:
    """
    Create engineered features (log transforms, interactions, etc.).
    
    Args:
        df: DataFrame with base features
        verbose: Print progress
        
    Returns:
        DataFrame with additional engineered features
    """
    if verbose:
        print(f"[ENGINEER] Creating engineered features")
    
    df_eng = df.copy()
    
    # Log transforms (for skewed variables)
    log_features = []
    
    if 'gdp_pc' in df_eng.columns:
        df_eng['log_gdp_pc'] = np.log1p(df_eng['gdp_pc'])
        log_features.append('log_gdp_pc')
    
    if 'health_exp' in df_eng.columns:
        df_eng['log_health_exp'] = np.log1p(df_eng['health_exp'])
        log_features.append('log_health_exp')
    
    if 'PM25_Total_ugm3' in df_eng.columns:
        df_eng['log_pm25'] = np.log1p(df_eng['PM25_Total_ugm3'])
        log_features.append('log_pm25')
    
    # Polynomial features
    poly_features = []
    
    if 'PM25_Total_ugm3' in df_eng.columns:
        df_eng['pm25_squared'] = df_eng['PM25_Total_ugm3'] ** 2
        poly_features.append('pm25_squared')
    
    # Interaction features
    interaction_features = []
    
    if 'PM25_Total_ugm3' in df_eng.columns and 'log_gdp_pc' in df_eng.columns:
        df_eng['pm25_x_gdp'] = df_eng['PM25_Total_ugm3'] * df_eng['log_gdp_pc']
        interaction_features.append('pm25_x_gdp')
    
    if 'PM25_Total_ugm3' in df_eng.columns and 'urban_pct' in df_eng.columns:
        df_eng['pm25_x_urban'] = df_eng['PM25_Total_ugm3'] * df_eng['urban_pct']
        interaction_features.append('pm25_x_urban')
    
    # Urban-rural gap
    if 'PM25_Urban_ugm3' in df_eng.columns and 'PM25_Rural_ugm3' in df_eng.columns:
        df_eng['pm25_urban_rural_gap'] = df_eng['PM25_Urban_ugm3'] - df_eng['PM25_Rural_ugm3']
        interaction_features.append('pm25_urban_rural_gap')
    
    if verbose:
        print(f"  Created {len(log_features)} log features: {log_features}")
        print(f"  Created {len(poly_features)} polynomial features: {poly_features}")
        print(f"  Created {len(interaction_features)} interaction features: {interaction_features}")
    
    return df_eng


def prepare_feature_sets(df: pd.DataFrame,
                        verbose: bool = True) -> Dict[str, List[str]]:
    """
    Prepare different feature sets for modeling.
    
    Args:
        df: DataFrame with all features
        verbose: Print information
        
    Returns:
        Dictionary of feature sets
    """
    feature_sets = {}
    
    # Set 1: PM2.5 only
    pm_features = [c for c in ['PM25_Total_ugm3', 'PM25_Urban_ugm3', 'PM25_Rural_ugm3'] 
                   if c in df.columns]
    if pm_features:
        feature_sets['pm25_only'] = pm_features
    
    # Set 2: PM2.5 + confounders
    confounders = ['log_gdp_pc', 'log_health_exp', 'urban_pct', 'fertility']
    pm_plus_conf = pm_features + [c for c in confounders if c in df.columns]
    if len(pm_plus_conf) > len(pm_features):
        feature_sets['pm25_plus_confounders'] = pm_plus_conf
    
    # Set 3: PM2.5 + confounders + engineered
    engineered = ['log_pm25', 'pm25_squared', 'pm25_x_gdp', 'pm25_x_urban', 'pm25_urban_rural_gap']
    all_features = pm_plus_conf + [c for c in engineered if c in df.columns]
    if len(all_features) > len(pm_plus_conf):
        feature_sets['full_engineered'] = all_features
    
    if verbose:
        print(f"\n[FEATURES] Prepared {len(feature_sets)} feature sets:")
        for name, features in feature_sets.items():
            print(f"  {name}: {len(features)} features")
    
    return feature_sets


def clip_outliers(df: pd.DataFrame,
                 columns: List[str],
                 lower_percentile: float = 0.01,
                 upper_percentile: float = 0.99,
                 verbose: bool = True) -> pd.DataFrame:
    """
    Clip outliers to specified percentiles.
    
    Args:
        df: DataFrame
        columns: List of columns to clip
        lower_percentile: Lower percentile (0-1)
        upper_percentile: Upper percentile (0-1)
        verbose: Print information
        
    Returns:
        DataFrame with clipped values
    """
    df_clipped = df.copy()
    
    if verbose:
        print(f"[CLIP] Clipping outliers to [{lower_percentile*100}%, {upper_percentile*100}%]")
    
    for col in columns:
        if col in df_clipped.columns:
            q_low = df_clipped[col].quantile(lower_percentile)
            q_high = df_clipped[col].quantile(upper_percentile)
            n_clipped = ((df_clipped[col] < q_low) | (df_clipped[col] > q_high)).sum()
            df_clipped[col] = df_clipped[col].clip(q_low, q_high)
            
            if verbose and n_clipped > 0:
                print(f"  {col}: clipped {n_clipped} values")
    
    return df_clipped

