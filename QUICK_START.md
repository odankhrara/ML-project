# Quick Start Guide
## Air Pollution & Under-5 Mortality Analysis

Get started with this project in under 5 minutes!

---

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required Packages**:
- pandas, numpy - Data manipulation
- scikit-learn, xgboost - Machine learning
- matplotlib, seaborn - Visualization
- statsmodels - Statistical analysis
- openpyxl - Excel file reading
- country-converter - ISO3 codes

---

## Running the Analysis

### Option 1: Complete Pipeline (Recommended)
Runs all phases including ML models and feature engineering:

```bash
python main_complete.py
```

**Output**: 
- 10+ visualizations
- 4+ statistical tables
- Trained ML models
- Extended dataset with World Bank data

**Duration**: ~45 seconds

---

### Option 2: Modular Version
Runs data processing, basic EDA, and statistical analysis:

```bash
python main_modular.py
```

**Output**:
- 5 exploratory plots
- Basic statistical summaries
- Linear regression results

**Duration**: ~10 seconds

---

### Option 3: Basic Version
Simple runnable version (Phase 1):

```bash
python main.py
```

---

## What Gets Generated

### Data Files (data/processed/)
- `who_pm25_long.csv` - WHO PM2.5 in long format (5,810 rows)
- `who_pm25_wide.csv` - WHO PM2.5 pivoted (1,950 rows)
- `unicef_u5mr_long.csv` - UNICEF mortality data (7,000 rows)
- `merged_pm25_u5mr.csv` - Combined dataset (1,950 rows)
- `merged_extended.csv` - With World Bank variables (1,950 rows)

### Figures (reports/figures/)
- `01_correlation_matrix.png` - Heatmap of relationships
- `02_pm25_vs_u5mr_scatter.png` - Regression plot
- `03_urban_vs_rural_pm25.png` - Urban vs rural comparison
- `04_top10_countries_pm25.png` - Highest pollution countries
- `05_timeseries_Afghanistan.png` - Example time series
- `model_comparison_pm25_only.png` - ML model performance
- `predictions_champion_model.png` - Best model results
- `feature_importance_*.png` - Feature importance plots

### Tables (reports/tables/)
- `summary_statistics.csv` - Descriptive stats
- `regression_summary.txt` - Linear regression output
- `model_results_pm25_only.csv` - All ML model metrics
- `feature_set_comparison.csv` - Feature set performance

### Models (models/)
- `champion_model.pkl` - Best performing model (Random Forest)

---

## Using the Modules

### Load Processed Data
```python
from src import data_processing

# Load all processed datasets
data = data_processing.load_processed_data()
merged_df = data['merged']
```

### Create Custom Visualizations
```python
from src import visualization

# Plot scatter with regression line
visualization.plot_scatter_with_regression(
    merged_df,
    'PM25_Total_ugm3',
    'U5MR_per_1000',
    title="Custom PM2.5 vs Mortality Plot"
)
```

### Run Statistical Tests
```python
from src import statistical_analysis

# Perform regression
model, summary = statistical_analysis.simple_linear_regression(
    merged_df,
    'PM25_Total_ugm3',
    'U5MR_per_1000'
)

print(f"R-squared: {summary['r_squared']:.4f}")
print(f"Slope: {summary['coef_slope']:.4f}")
```

### Train Custom Models
```python
from src import ml_pipeline
import config

# Prepare data
features = ['PM25_Total_ugm3', 'PM25_Urban_ugm3', 'PM25_Rural_ugm3']
X_train, X_test, y_train, y_test, _, _ = ml_pipeline.create_time_aware_split(
    merged_df, features, config.TARGET
)

# Train models
models, results = ml_pipeline.train_and_evaluate_models(
    X_train, X_test, y_train, y_test, features
)

# Get best model
best_model_name = results.iloc[0]['Model']
best_model = models[best_model_name]
```

### Download Additional Data
```python
from src import feature_engineering

# Download World Bank indicators
external_data = feature_engineering.download_external_data()

# Merge with your dataset
merged_extended = feature_engineering.merge_external_features(
    merged_df, external_data
)

# Create engineered features
merged_extended = feature_engineering.create_engineered_features(
    merged_extended
)
```

---

## Configuration

All settings are in `config.py`:

```python
# Change model parameters
RF_N_ESTIMATORS = 600  # Number of trees in Random Forest
CV_FOLDS = 5           # Cross-validation folds

# Change paths
FIGURES_DIR = 'custom_figures/'

# Change visualization settings
FIGURE_DPI = 300  # Higher resolution
```

---

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

### Issue: FileNotFoundError for data files
**Solution**: Ensure `who_pm25_2022.csv` and `unicef_u5mr_2023.xlsx` are in the project directory

### Issue: UnicodeError on Windows
**Solution**: Already fixed! All print statements use ASCII-compatible text

### Issue: Memory Error
**Solution**: Reduce number of trees in Random Forest
```python
# In config.py
RF_N_ESTIMATORS = 300  # Instead of 600
```

---

## Project Structure

```
Project/
├── config.py              # Settings
├── requirements.txt       # Dependencies
├── README.md             # Full documentation
├── QUICK_START.md        # This file
├── PROJECT_REPORT.md     # Comprehensive report
│
├── main_complete.py      # Run everything
├── main_modular.py       # Run basic analysis
├── main.py               # Run Phase 1 only
│
├── src/                  # Reusable modules
│   ├── data_processing.py
│   ├── visualization.py
│   ├── statistical_analysis.py
│   ├── ml_pipeline.py
│   └── feature_engineering.py
│
├── data/                 # Data files
│   ├── raw/              # Original data
│   └── processed/        # Clean CSVs
│
├── reports/              # Outputs
│   ├── figures/          # Plots (PNG)
│   └── tables/           # Tables (CSV)
│
└── models/               # Trained models
    └── champion_model.pkl
```

---

## Key Results at a Glance

**Dataset**:
- 195 countries, 1,950 observations (2010-2018)
- PM2.5 mean: 22.7 µg/m³ (range: 5-72)
- U5MR mean: 33.4 per 1,000 (range: 1.7-479)

**Statistical Findings**:
- Correlation PM2.5 ↔ U5MR: r = 0.33 (p < 0.001)
- Each 1 µg/m³ increase → +0.85 deaths per 1,000
- Urban PM2.5 14% higher than rural

**Best ML Model**:
- Random Forest: R² = 0.437, MAE = 15.25
- Explains 43.7% of variance
- Average error: 15.2 deaths per 1,000

---

## Next Steps

1. **Explore the data**: Open `merged_pm25_u5mr.csv` in Excel/Pandas
2. **View visualizations**: Check `reports/figures/` folder
3. **Read the report**: Open `PROJECT_REPORT.md` for detailed analysis
4. **Customize analysis**: Modify `config.py` and re-run
5. **Add your own features**: Edit `src/feature_engineering.py`

---

## Getting Help

- **Documentation**: See `README.md` for comprehensive guide
- **Report**: See `PROJECT_REPORT.md` for methodology and results
- **Code**: All functions have detailed docstrings

---

**Happy Analyzing!** 🚀

