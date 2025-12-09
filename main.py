"""
Air Pollution and Under-5 Mortality Analysis
Phase 1: Local runnable version with basic improvements
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Set up directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
FIGURES_DIR = os.path.join(REPORTS_DIR, 'figures')
TABLES_DIR = os.path.join(REPORTS_DIR, 'tables')

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, FIGURES_DIR, TABLES_DIR]:
    os.makedirs(directory, exist_ok=True)

# File paths (checking for files in current directory first)
WHO_CSV = 'who_pm25_2022.csv' if os.path.exists('who_pm25_2022.csv') else os.path.join(RAW_DATA_DIR, 'who_pm25_2022.csv')
UNICEF_XLSX = 'unicef_u5mr_2023.xlsx' if os.path.exists('unicef_u5mr_2023.xlsx') else os.path.join(RAW_DATA_DIR, 'unicef_u5mr_2023.xlsx')

print("="*80)
print("AIR POLLUTION & UNDER-5 MORTALITY ANALYSIS - PHASE 1")
print("="*80)
print(f"\nBase Directory: {BASE_DIR}")
print(f"Looking for data files:")
print(f"  - WHO PM2.5: {WHO_CSV}")
print(f"  - UNICEF U5MR: {UNICEF_XLSX}")

# ============================================================================
# STEP 1: LOAD AND PROCESS WHO PM2.5 DATA
# ============================================================================

print("\n" + "="*80)
print("STEP 1: Loading WHO PM2.5 Data")
print("="*80)

try:
    df_raw = pd.read_csv(WHO_CSV, low_memory=False)
    print(f"[OK] Loaded WHO data: {df_raw.shape}")
    print(f"   Columns: {sorted(df_raw.columns.tolist())[:10]}...")
except FileNotFoundError:
    print(f"[ERROR] Cannot find {WHO_CSV}")
    print(f"   Please ensure the file is in the current directory or {RAW_DATA_DIR}")
    exit(1)

# Detect column names
def pick_column(colnames, df):
    """Find the first matching column name from a list of candidates"""
    for c in colnames:
        if c in df.columns:
            return c
    return None

COL_COUNTRY = pick_column(['Location','Country','SpatialDim','SpatialDimName'], df_raw)
COL_YEAR = pick_column(['Period','Year'], df_raw)
COL_VALUE = pick_column(['FactValueNumeric','Value','NumericValue'], df_raw)
COL_IND = pick_column(['Indicator','IndicatorName','Indicator Code','IndicatorCode'], df_raw)

print(f"\nDetected columns:")
print(f"  Country: {COL_COUNTRY}")
print(f"  Year: {COL_YEAR}")
print(f"  Value: {COL_VALUE}")
print(f"  Indicator: {COL_IND}")

if not all([COL_COUNTRY, COL_YEAR, COL_VALUE]):
    raise ValueError(f"Missing key columns. Found -> Country:{COL_COUNTRY}, Year:{COL_YEAR}, Value:{COL_VALUE}")

# Filter for PM2.5 data
df = df_raw.copy()
if COL_IND and df[COL_IND].notna().any():
    pm_mask = df[COL_IND].astype(str).str.contains(r'PM2\.5|fine particulate', case=False, na=False)
    df = df[pm_mask].copy()
    print(f"  Filtered to PM2.5 data: {df.shape[0]} rows")

# Detect residence column (Urban/Rural/Total)
import re
res_candidates = [c for c in df.columns if re.search(r'dim1|residence|urban|rural|total', c, flags=re.I)]

def detect_residence_column(frame, candidates):
    for c in candidates:
        vals = frame[c].astype(str).str.lower()
        if vals.str.contains('urban|rural|total', regex=True).any():
            return c
    return None

COL_RES = detect_residence_column(df, res_candidates)

def to_residence(v):
    s = str(v).lower()
    if 'urban' in s: return 'Urban'
    if 'rural' in s: return 'Rural'
    if 'total' in s or 'national' in s or 'both sexes' in s: return 'Total'
    return None

if COL_RES:
    df['Residence'] = df[COL_RES].apply(to_residence)
    df = df[df['Residence'].notna()]
    print(f"  Detected residence column: {COL_RES}")
else:
    df['Residence'] = 'Total'
    print(f"  No residence column found, using 'Total' for all records")

# Rename columns
df = df.rename(columns={COL_COUNTRY:'Country', COL_YEAR:'Year', COL_VALUE:'PM25_ugm3'})
df['Country'] = df['Country'].astype(str).str.strip()
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
df['PM25_ugm3'] = pd.to_numeric(df['PM25_ugm3'], errors='coerce')
df = df.dropna(subset=['Country','Year','PM25_ugm3'])

print(f"  After cleaning: {df.shape[0]} rows")

# Add ISO3 country codes
try:
    import country_converter as coco
    
    if 'SpatialDimValueCode' in df.columns:
        iso = df['SpatialDimValueCode'].where(df['SpatialDimValueCode'].astype(str).str.len()==3)
    else:
        iso = None
    df['Country_ISO3'] = iso
    
    fixes = {
        "Côte d'Ivoire": "Cote d'Ivoire",
        "Côte d\\'Ivoire": "Cote d'Ivoire",
        'Congo, Dem. Rep.': 'Democratic Republic of the Congo',
        'Congo, Rep.': 'Congo',
        'United States of America': 'United States',
        'Russian Federation': 'Russia',
        'Viet Nam': 'Vietnam',
    }
    need_iso = df['Country_ISO3'].isna()
    df.loc[need_iso, 'Country_ISO3'] = coco.convert(
        df.loc[need_iso, 'Country'].replace(fixes), 
        to='ISO3', 
        not_found=None
    )
    print(f"  Added ISO3 codes for {df['Country_ISO3'].notna().sum()} countries")
except ImportError:
    print("  [WARNING] country_converter not installed. Run: pip install country-converter")
    df['Country_ISO3'] = None

# Create LONG format (Country–Year–Residence)
who_long = (df[['Country','Country_ISO3','Year','Residence','PM25_ugm3']]
            .groupby(['Country','Country_ISO3','Year','Residence'], as_index=False)
            .agg({'PM25_ugm3':'mean'}))
print(f"\n[OK] WHO Long format: {who_long.shape}")
print(who_long.head(10).to_string())

# Create WIDE format (pivot by Residence)
who_wide = who_long.pivot_table(
    index=['Country','Country_ISO3','Year'],
    columns='Residence',
    values='PM25_ugm3',
    aggfunc='mean'
).reset_index()
who_wide.columns.name = None
who_wide = who_wide.rename(columns={
    'Rural':'PM25_Rural_ugm3',
    'Urban':'PM25_Urban_ugm3',
    'Total':'PM25_Total_ugm3'
})
who_wide = who_wide.sort_values(['Country','Year']).reset_index(drop=True)
print(f"\n[OK] WHO Wide format: {who_wide.shape}")
print(who_wide.head(10).to_string())

# Save processed WHO data
who_long.to_csv(os.path.join(PROCESSED_DATA_DIR, 'who_pm25_long.csv'), index=False)
who_wide.to_csv(os.path.join(PROCESSED_DATA_DIR, 'who_pm25_wide.csv'), index=False)
print(f"\n[SAVED] Processed WHO data to {PROCESSED_DATA_DIR}")

# ============================================================================
# STEP 2: LOAD AND PROCESS UNICEF U5MR DATA
# ============================================================================

print("\n" + "="*80)
print("STEP 2: Loading UNICEF Under-5 Mortality Data")
print("="*80)

try:
    # Read with first row as header after skipping metadata
    u5mr_raw = pd.read_excel(UNICEF_XLSX, skiprows=13)
    # Use first row as column names
    u5mr = u5mr_raw.copy()
    u5mr.columns = u5mr_raw.iloc[0]
    u5mr = u5mr[1:].reset_index(drop=True)
    
    print(f"[OK] Loaded UNICEF data: {u5mr.shape}")
    print(f"   Columns: {list(u5mr.columns)[:10]}...")
except FileNotFoundError:
    print(f"[ERROR] Cannot find {UNICEF_XLSX}")
    print(f"   Please ensure the file is in the current directory or {RAW_DATA_DIR}")
    exit(1)

# Filter for median estimates
if "Uncertainty.Bounds*" in u5mr.columns:
    u5mr = u5mr[u5mr["Uncertainty.Bounds*"].astype(str).str.contains("Median", case=False, na=False)]
    print(f"  Filtered to median estimates: {u5mr.shape[0]} rows")

# Identify year columns (should be numeric like 1950.5, 1951.5, etc.)
year_cols = [c for c in u5mr.columns if str(c).replace(".", "", 1).replace("-", "", 1).isdigit()]
print(f"  Found {len(year_cols)} year columns: {year_cols[:5] if len(year_cols) >= 5 else year_cols}...{year_cols[-3:] if len(year_cols) >= 3 else []}")

# Melt to long format
u5mr_long = u5mr.melt(
    id_vars=["ISO.Code", "Country.Name"],
    value_vars=year_cols,
    var_name="Year",
    value_name="U5MR_per_1000"
)

u5mr_long["Year"] = pd.to_numeric(u5mr_long["Year"], errors="coerce").round().astype("Int64")
u5mr_long["U5MR_per_1000"] = pd.to_numeric(u5mr_long["U5MR_per_1000"], errors="coerce")
u5mr_long = u5mr_long.dropna(subset=["U5MR_per_1000"])
u5mr_long = u5mr_long.query("Year >= 1990")

u5mr_long = u5mr_long.rename(columns={
    "ISO.Code": "Country_ISO3",
    "Country.Name": "Country"
})

print(f"\n[OK] UNICEF Long format: {u5mr_long.shape}")
print(u5mr_long.head(10).to_string())

# Save processed UNICEF data
u5mr_long.to_csv(os.path.join(PROCESSED_DATA_DIR, 'unicef_u5mr_long.csv'), index=False)
print(f"\n[SAVED] Processed UNICEF data to {PROCESSED_DATA_DIR}")

# ============================================================================
# STEP 3: MERGE WHO PM2.5 AND UNICEF U5MR DATA
# ============================================================================

print("\n" + "="*80)
print("STEP 3: Merging WHO PM2.5 and UNICEF U5MR Data")
print("="*80)

who_wide["Year"] = pd.to_numeric(who_wide["Year"], errors="coerce").astype("Int64")

merged = pd.merge(
    who_wide,
    u5mr_long,
    on=["Country_ISO3", "Year"],
    how="inner",
    suffixes=('_WHO', '_UNICEF')
)

print(f"[OK] Merged dataset: {merged.shape}")
print(f"   Countries: {merged['Country_ISO3'].nunique()}")
print(f"   Year range: {merged['Year'].min()} - {merged['Year'].max()}")
print(f"   Total observations: {len(merged)}")
print("\nFirst few rows:")
print(merged.head(10).to_string())

# Save merged data
merged.to_csv(os.path.join(PROCESSED_DATA_DIR, 'merged_pm25_u5mr.csv'), index=False)
print(f"\n[SAVED] Merged data to {PROCESSED_DATA_DIR}")

# ============================================================================
# STEP 4: BASIC EXPLORATORY DATA ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("STEP 4: Basic Exploratory Data Analysis")
print("="*80)

# Correlation analysis
pm_cols = [c for c in ["PM25_Total_ugm3", "PM25_Urban_ugm3", "PM25_Rural_ugm3"] if c in merged.columns]
corr = merged[pm_cols + ["U5MR_per_1000"]].corr()
print("\nCorrelation Matrix:")
print(corr.round(3).to_string())

# Save correlation matrix
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", center=0)
plt.title("Correlation Matrix: PM2.5 vs Under-5 Mortality")
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, '01_correlation_matrix.png'), dpi=200, bbox_inches='tight')
print(f"\n[SAVED] Correlation heatmap to {FIGURES_DIR}")
plt.close()

# Scatter plot: PM2.5 vs U5MR
if 'PM25_Total_ugm3' in merged.columns:
    plt.figure(figsize=(10, 6))
    sns.regplot(data=merged, x="PM25_Total_ugm3", y="U5MR_per_1000", 
                scatter_kws={"alpha":0.4}, line_kws={"color":"red"})
    plt.title("PM2.5 (Total) vs Under-5 Mortality Rate")
    plt.xlabel("PM2.5 (ug/m3)")
    plt.ylabel("Under-5 Mortality (per 1,000)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, '02_pm25_vs_u5mr_scatter.png'), dpi=200, bbox_inches='tight')
    print(f"[SAVED] Scatter plot to {FIGURES_DIR}")
    plt.close()

# Urban vs Rural PM2.5
if 'PM25_Rural_ugm3' in merged.columns and 'PM25_Urban_ugm3' in merged.columns:
    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=merged, x='PM25_Rural_ugm3', y='PM25_Urban_ugm3', alpha=0.5)
    max_val = max(merged['PM25_Rural_ugm3'].max(), merged['PM25_Urban_ugm3'].max())
    plt.plot([0, max_val], [0, max_val], 'r--', label='y=x')
    plt.xlabel('Rural PM2.5 (ug/m3)')
    plt.ylabel('Urban PM2.5 (ug/m3)')
    plt.title('Urban vs Rural PM2.5 Concentration')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, '03_urban_vs_rural_pm25.png'), dpi=200, bbox_inches='tight')
    print(f"[SAVED] Urban vs rural plot to {FIGURES_DIR}")
    plt.close()

# Top 10 countries by PM2.5
if 'PM25_Total_ugm3' in merged.columns:
    avg_pm25 = (merged.groupby('Country_WHO')['PM25_Total_ugm3']
                .mean().sort_values(ascending=False).head(10))
    
    plt.figure(figsize=(10, 6))
    avg_pm25.plot(kind='bar', color='salmon')
    plt.title("Top 10 Countries by Average PM2.5 (Total)")
    plt.ylabel("PM2.5 (ug/m3)")
    plt.xlabel("Country")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, '04_top10_countries_pm25.png'), dpi=200, bbox_inches='tight')
    print(f"[SAVED] Top 10 countries plot to {FIGURES_DIR}")
    plt.close()

# Example time series for a country
country_col = 'Country_WHO' if 'Country_WHO' in merged.columns else 'Country_ISO3'
sample_countries = merged[country_col].value_counts().head(5).index.tolist()

if sample_countries and 'PM25_Total_ugm3' in merged.columns:
    country = sample_countries[0]
    sub = merged[merged[country_col] == country].sort_values('Year')
    
    if len(sub) > 0:
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        ax1.plot(sub["Year"], sub["PM25_Total_ugm3"], "b-o", label="PM2.5 Total")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("PM2.5 (µg/m³)", color="b")
        ax1.tick_params(axis='y', labelcolor='b')
        
        ax2 = ax1.twinx()
        ax2.plot(sub["Year"], sub["U5MR_per_1000"], "r--s", label="U5MR")
        ax2.set_ylabel("Under-5 Mortality (per 1,000)", color="r")
        ax2.tick_params(axis='y', labelcolor='r')
        
        plt.title(f"{country}: PM2.5 and Under-5 Mortality Over Time")
        fig.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f'05_timeseries_{country}.png'), dpi=200, bbox_inches='tight')
        print(f"[SAVED] Time series plot for {country} to {FIGURES_DIR}")
        plt.close()

# ============================================================================
# STEP 5: BASIC STATISTICAL ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("STEP 5: Basic Statistical Analysis")
print("="*80)

try:
    import statsmodels.api as sm
    
    if 'PM25_Total_ugm3' in merged.columns:
        # Simple linear regression: U5MR ~ PM2.5_Total
        analysis_df = merged[['PM25_Total_ugm3', 'U5MR_per_1000']].dropna()
        
        X = analysis_df[["PM25_Total_ugm3"]]
        y = analysis_df["U5MR_per_1000"]
        X = sm.add_constant(X)
        
        model = sm.OLS(y, X, missing="drop").fit()
        print("\n" + "="*50)
        print("Linear Regression: U5MR ~ PM2.5 Total")
        print("="*50)
        print(model.summary())
        
        # Save regression summary
        with open(os.path.join(TABLES_DIR, 'regression_summary.txt'), 'w') as f:
            f.write(str(model.summary()))
        print(f"\n[SAVED] Regression summary to {TABLES_DIR}")
        
except ImportError:
    print("  [WARNING] statsmodels not installed. Run: pip install statsmodels")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

summary_stats = merged[pm_cols + ["U5MR_per_1000"]].describe()
print("\nDescriptive Statistics:")
print(summary_stats.to_string())

# Save summary statistics
summary_stats.to_csv(os.path.join(TABLES_DIR, 'summary_statistics.csv'))
print(f"\n[SAVED] Summary statistics to {TABLES_DIR}")

# ============================================================================
# PHASE 1 COMPLETE
# ============================================================================

print("\n" + "="*80)
print("[SUCCESS] PHASE 1 COMPLETE!")
print("="*80)
print(f"\nGenerated files:")
print(f"  Processed data: {PROCESSED_DATA_DIR}/")
print(f"    - who_pm25_long.csv")
print(f"    - who_pm25_wide.csv")
print(f"    - unicef_u5mr_long.csv")
print(f"    - merged_pm25_u5mr.csv")
print(f"\n  Figures: {FIGURES_DIR}/")
print(f"    - 01_correlation_matrix.png")
print(f"    - 02_pm25_vs_u5mr_scatter.png")
print(f"    - 03_urban_vs_rural_pm25.png")
print(f"    - 04_top10_countries_pm25.png")
print(f"    - 05_timeseries_*.png")
print(f"\n  Tables: {TABLES_DIR}/")
print(f"    - summary_statistics.csv")
print(f"    - regression_summary.txt")
print("\nNext: Run Phase 2 for modularized code structure")
print("="*80)

