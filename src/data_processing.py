"""
Data Processing Module
Functions for loading, cleaning, and transforming WHO PM2.5 and UNICEF U5MR data
"""

import pandas as pd
import numpy as np
import re
from typing import Optional, Dict, List, Tuple
import config


def pick_column(column_candidates: List[str], df: pd.DataFrame) -> Optional[str]:
    """
    Find the first matching column name from a list of candidates.
    
    Args:
        column_candidates: List of possible column names
        df: DataFrame to search in
        
    Returns:
        First matching column name, or None if not found
    """
    for col in column_candidates:
        if col in df.columns:
            return col
    return None


def detect_residence_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """
    Detect which column contains residence information (Urban/Rural/Total).
    
    Args:
        df: DataFrame to search
        candidates: List of candidate column names
        
    Returns:
        Column name containing residence data, or None
    """
    for col in candidates:
        if col not in df.columns:
            continue
        vals = df[col].astype(str).str.lower()
        if vals.str.contains('urban|rural|total', regex=True).any():
            return col
    return None


def categorize_residence(value: any) -> Optional[str]:
    """
    Categorize a value as Urban, Rural, or Total residence type.
    
    Args:
        value: Raw residence value
        
    Returns:
        'Urban', 'Rural', 'Total', or None
    """
    s = str(value).lower()
    if 'urban' in s:
        return 'Urban'
    if 'rural' in s:
        return 'Rural'
    if 'total' in s or 'national' in s or 'both sexes' in s:
        return 'Total'
    return None


def load_who_pm25_data(filepath: str, verbose: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and process WHO PM2.5 data from CSV file.
    
    Args:
        filepath: Path to WHO CSV file
        verbose: Print progress messages
        
    Returns:
        Tuple of (long_format_df, wide_format_df)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    if verbose:
        print(f"[LOAD] Loading WHO PM2.5 data from {filepath}")
    
    # Load raw data
    df_raw = pd.read_csv(filepath, low_memory=False)
    if verbose:
        print(f"  Loaded {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
    
    # Detect column names
    col_country = pick_column(config.WHO_COUNTRY_COLS, df_raw)
    col_year = pick_column(config.WHO_YEAR_COLS, df_raw)
    col_value = pick_column(config.WHO_VALUE_COLS, df_raw)
    col_indicator = pick_column(config.WHO_INDICATOR_COLS, df_raw)
    
    if verbose:
        print(f"  Detected columns: Country={col_country}, Year={col_year}, "
              f"Value={col_value}, Indicator={col_indicator}")
    
    # Validate required columns
    if not all([col_country, col_year, col_value]):
        raise ValueError(f"Missing required columns. Found: Country={col_country}, "
                        f"Year={col_year}, Value={col_value}")
    
    # Filter for PM2.5 data
    df = df_raw.copy()
    if col_indicator and df[col_indicator].notna().any():
        pm_mask = df[col_indicator].astype(str).str.contains(
            config.PM25_INDICATOR_PATTERN, case=False, na=False
        )
        df = df[pm_mask].copy()
        if verbose:
            print(f"  Filtered to PM2.5 data: {df.shape[0]} rows")
    
    # Detect and process residence column
    res_candidates = [c for c in df.columns 
                     if re.search(r'dim1|residence|urban|rural|total', c, flags=re.I)]
    col_residence = detect_residence_column(df, res_candidates)
    
    if col_residence:
        df['Residence'] = df[col_residence].apply(categorize_residence)
        df = df[df['Residence'].notna()]
        if verbose:
            print(f"  Detected residence column: {col_residence}")
    else:
        df['Residence'] = 'Total'
        if verbose:
            print(f"  No residence column found, using 'Total' for all records")
    
    # Rename and clean columns
    df = df.rename(columns={
        col_country: 'Country',
        col_year: 'Year',
        col_value: 'PM25_ugm3'
    })
    
    df['Country'] = df['Country'].astype(str).str.strip()
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
    df['PM25_ugm3'] = pd.to_numeric(df['PM25_ugm3'], errors='coerce')
    df = df.dropna(subset=['Country', 'Year', 'PM25_ugm3'])
    
    if verbose:
        print(f"  After cleaning: {df.shape[0]} rows")
    
    # Add ISO3 country codes
    df = add_iso3_codes(df, verbose=verbose)
    
    # Create long format
    who_long = (df[['Country', 'Country_ISO3', 'Year', 'Residence', 'PM25_ugm3']]
                .groupby(['Country', 'Country_ISO3', 'Year', 'Residence'], as_index=False)
                .agg({'PM25_ugm3': 'mean'}))
    
    if verbose:
        print(f"  Created long format: {who_long.shape}")
    
    # Create wide format
    who_wide = who_long.pivot_table(
        index=['Country', 'Country_ISO3', 'Year'],
        columns='Residence',
        values='PM25_ugm3',
        aggfunc='mean'
    ).reset_index()
    
    who_wide.columns.name = None
    who_wide = who_wide.rename(columns={
        'Rural': 'PM25_Rural_ugm3',
        'Urban': 'PM25_Urban_ugm3',
        'Total': 'PM25_Total_ugm3'
    })
    who_wide = who_wide.sort_values(['Country', 'Year']).reset_index(drop=True)
    
    if verbose:
        print(f"  Created wide format: {who_wide.shape}")
    
    return who_long, who_wide


def add_iso3_codes(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Add ISO3 country codes to DataFrame.
    
    Args:
        df: DataFrame with 'Country' column
        verbose: Print progress messages
        
    Returns:
        DataFrame with 'Country_ISO3' column added
    """
    try:
        import country_converter as coco
        
        # Try to use existing ISO3 codes if available
        if 'SpatialDimValueCode' in df.columns:
            iso = df['SpatialDimValueCode'].where(
                df['SpatialDimValueCode'].astype(str).str.len() == 3
            )
        else:
            iso = None
        
        df['Country_ISO3'] = iso
        
        # Convert missing ISO3 codes
        need_iso = df['Country_ISO3'].isna()
        df.loc[need_iso, 'Country_ISO3'] = coco.convert(
            df.loc[need_iso, 'Country'].replace(config.COUNTRY_NAME_FIXES),
            to='ISO3',
            not_found=None
        )
        
        if verbose:
            n_with_iso = df['Country_ISO3'].notna().sum()
            print(f"  Added ISO3 codes for {n_with_iso} records")
            
    except ImportError:
        if verbose:
            print("  [WARNING] country_converter not installed. ISO3 codes not added.")
        df['Country_ISO3'] = None
    
    return df


def load_unicef_u5mr_data(filepath: str, verbose: bool = True) -> pd.DataFrame:
    """
    Load and process UNICEF Under-5 Mortality Rate data from Excel file.
    
    Args:
        filepath: Path to UNICEF Excel file
        verbose: Print progress messages
        
    Returns:
        DataFrame in long format (Country_ISO3, Country, Year, U5MR_per_1000)
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if verbose:
        print(f"[LOAD] Loading UNICEF U5MR data from {filepath}")
    
    # Read Excel file (skip metadata rows)
    u5mr_raw = pd.read_excel(filepath, skiprows=13)
    
    # Use first row as column names
    u5mr = u5mr_raw.copy()
    u5mr.columns = u5mr_raw.iloc[0]
    u5mr = u5mr[1:].reset_index(drop=True)
    
    if verbose:
        print(f"  Loaded {u5mr.shape[0]} rows, {u5mr.shape[1]} columns")
    
    # Filter for median estimates
    if "Uncertainty.Bounds*" in u5mr.columns:
        u5mr = u5mr[u5mr["Uncertainty.Bounds*"].astype(str).str.contains(
            "Median", case=False, na=False
        )]
        if verbose:
            print(f"  Filtered to median estimates: {u5mr.shape[0]} rows")
    
    # Identify year columns
    year_cols = [c for c in u5mr.columns 
                 if str(c).replace(".", "", 1).replace("-", "", 1).isdigit()]
    
    if verbose:
        print(f"  Found {len(year_cols)} year columns")
    
    # Melt to long format
    u5mr_long = u5mr.melt(
        id_vars=["ISO.Code", "Country.Name"],
        value_vars=year_cols,
        var_name="Year",
        value_name="U5MR_per_1000"
    )
    
    # Clean data
    u5mr_long["Year"] = pd.to_numeric(u5mr_long["Year"], errors="coerce").round().astype("Int64")
    u5mr_long["U5MR_per_1000"] = pd.to_numeric(u5mr_long["U5MR_per_1000"], errors="coerce")
    u5mr_long = u5mr_long.dropna(subset=["U5MR_per_1000"])
    u5mr_long = u5mr_long.query(f"Year >= {config.MIN_YEAR}")
    
    # Rename columns
    u5mr_long = u5mr_long.rename(columns={
        "ISO.Code": "Country_ISO3",
        "Country.Name": "Country"
    })
    
    if verbose:
        print(f"  Created long format: {u5mr_long.shape}")
    
    return u5mr_long


def merge_pm25_u5mr(who_wide: pd.DataFrame, 
                    u5mr_long: pd.DataFrame, 
                    verbose: bool = True) -> pd.DataFrame:
    """
    Merge WHO PM2.5 and UNICEF U5MR datasets.
    
    Args:
        who_wide: WHO PM2.5 data in wide format
        u5mr_long: UNICEF U5MR data in long format
        verbose: Print progress messages
        
    Returns:
        Merged DataFrame
    """
    if verbose:
        print(f"[MERGE] Merging WHO PM2.5 and UNICEF U5MR data")
    
    # Ensure Year columns are compatible
    who_wide["Year"] = pd.to_numeric(who_wide["Year"], errors="coerce").astype("Int64")
    
    # Merge on Country_ISO3 and Year
    merged = pd.merge(
        who_wide,
        u5mr_long,
        on=["Country_ISO3", "Year"],
        how="inner",
        suffixes=('_WHO', '_UNICEF')
    )
    
    if verbose:
        print(f"  Merged dataset: {merged.shape}")
        print(f"  Countries: {merged['Country_ISO3'].nunique()}")
        print(f"  Year range: {merged['Year'].min()} - {merged['Year'].max()}")
    
    return merged


def save_processed_data(who_long: pd.DataFrame,
                       who_wide: pd.DataFrame,
                       u5mr_long: pd.DataFrame,
                       merged: pd.DataFrame,
                       verbose: bool = True) -> None:
    """
    Save all processed datasets to CSV files.
    
    Args:
        who_long: WHO PM2.5 long format
        who_wide: WHO PM2.5 wide format
        u5mr_long: UNICEF U5MR long format
        merged: Merged dataset
        verbose: Print progress messages
    """
    if verbose:
        print(f"[SAVE] Saving processed data")
    
    who_long.to_csv(config.WHO_LONG_CSV, index=False)
    who_wide.to_csv(config.WHO_WIDE_CSV, index=False)
    u5mr_long.to_csv(config.UNICEF_LONG_CSV, index=False)
    merged.to_csv(config.MERGED_CSV, index=False)
    
    if verbose:
        print(f"  Saved to {config.PROCESSED_DATA_DIR}")


def load_processed_data(verbose: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Load all processed datasets from CSV files.
    
    Args:
        verbose: Print progress messages
        
    Returns:
        Dictionary with keys: 'who_long', 'who_wide', 'u5mr_long', 'merged'
    """
    if verbose:
        print(f"[LOAD] Loading processed data from {config.PROCESSED_DATA_DIR}")
    
    data = {
        'who_long': pd.read_csv(config.WHO_LONG_CSV),
        'who_wide': pd.read_csv(config.WHO_WIDE_CSV),
        'u5mr_long': pd.read_csv(config.UNICEF_LONG_CSV),
        'merged': pd.read_csv(config.MERGED_CSV)
    }
    
    if verbose:
        for name, df in data.items():
            print(f"  {name}: {df.shape}")
    
    return data

