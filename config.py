"""
Configuration file for Air Pollution & U5MR Analysis
Centralized settings for paths, parameters, and constants
"""

import os

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
FIGURES_DIR = os.path.join(REPORTS_DIR, 'figures')
TABLES_DIR = os.path.join(REPORTS_DIR, 'tables')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Create all directories
ALL_DIRS = [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, 
            REPORTS_DIR, FIGURES_DIR, TABLES_DIR, MODELS_DIR]

for directory in ALL_DIRS:
    os.makedirs(directory, exist_ok=True)

# ============================================================================
# DATA FILES
# ============================================================================

# Input files (check current directory first, then raw data directory)
WHO_CSV = 'who_pm25_2022.csv' if os.path.exists('who_pm25_2022.csv') \
          else os.path.join(RAW_DATA_DIR, 'who_pm25_2022.csv')

UNICEF_XLSX = 'unicef_u5mr_2023.xlsx' if os.path.exists('unicef_u5mr_2023.xlsx') \
              else os.path.join(RAW_DATA_DIR, 'unicef_u5mr_2023.xlsx')

# Processed files
WHO_LONG_CSV = os.path.join(PROCESSED_DATA_DIR, 'who_pm25_long.csv')
WHO_WIDE_CSV = os.path.join(PROCESSED_DATA_DIR, 'who_pm25_wide.csv')
UNICEF_LONG_CSV = os.path.join(PROCESSED_DATA_DIR, 'unicef_u5mr_long.csv')
MERGED_CSV = os.path.join(PROCESSED_DATA_DIR, 'merged_pm25_u5mr.csv')

# ============================================================================
# COLUMN NAME MAPPINGS
# ============================================================================

# WHO PM2.5 column candidates
WHO_COUNTRY_COLS = ['Location', 'Country', 'SpatialDim', 'SpatialDimName']
WHO_YEAR_COLS = ['Period', 'Year']
WHO_VALUE_COLS = ['FactValueNumeric', 'Value', 'NumericValue']
WHO_INDICATOR_COLS = ['Indicator', 'IndicatorName', 'Indicator Code', 'IndicatorCode']

# Country name fixes for ISO3 conversion
COUNTRY_NAME_FIXES = {
    "Côte d'Ivoire": "Cote d'Ivoire",
    "Côte d\\'Ivoire": "Cote d'Ivoire",
    'Congo, Dem. Rep.': 'Democratic Republic of the Congo',
    'Congo, Rep.': 'Congo',
    'United States of America': 'United States',
    'Russian Federation': 'Russia',
    'Viet Nam': 'Vietnam',
}

# ============================================================================
# ANALYSIS PARAMETERS
# ============================================================================

# Data filtering
MIN_YEAR = 1990  # Minimum year for analysis
PM25_INDICATOR_PATTERN = r'PM2\.5|fine particulate'

# Visualization settings
FIGURE_DPI = 200
FIGURE_SIZE_STANDARD = (10, 6)
FIGURE_SIZE_SQUARE = (8, 8)
FIGURE_SIZE_LARGE = (12, 8)

# Correlation colormap
CORRELATION_CMAP = 'coolwarm'

# Random seed for reproducibility
RANDOM_SEED = 42

# ============================================================================
# MODEL PARAMETERS
# ============================================================================

# Train-test split
TEST_SIZE = 0.2
TRAIN_YEAR_QUANTILE = 0.8  # Use 80% oldest years for training

# Cross-validation
CV_FOLDS = 5

# Model grid search parameters
RIDGE_ALPHAS = [0.1, 1, 3, 10, 30]
LASSO_ALPHAS = [0.001, 0.01, 0.1, 1, 3]
RF_MAX_DEPTHS = [None, 6, 10]
RF_MIN_SAMPLES_LEAF = [1, 2, 4]
RF_N_ESTIMATORS = 600
GBR_N_ESTIMATORS = [300, 600, 1000]
GBR_LEARNING_RATES = [0.03, 0.05, 0.08]
GBR_MAX_DEPTHS = [2, 3, 4]

# Feature names
PM25_FEATURES = ['PM25_Total_ugm3', 'PM25_Urban_ugm3', 'PM25_Rural_ugm3']
TARGET = 'U5MR_per_1000'

# ============================================================================
# LOGGING
# ============================================================================

LOG_FORMAT = '[%(levelname)s] %(message)s'

