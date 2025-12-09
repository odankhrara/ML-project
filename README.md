# Air Pollution and Under-5 Mortality Analysis

A comprehensive machine learning analysis exploring the relationship between PM2.5 air pollution levels and under-5 mortality rates across countries.

## 📊 Project Overview

This project analyzes WHO air pollution data (PM2.5 concentrations) and UNICEF under-5 mortality rates to:
- Understand the correlation between air quality and child health outcomes
- Build predictive models for mortality rates based on pollution levels
- Identify countries and regions most affected by air pollution

## 🎯 Key Findings

- **PM2.5 explains 10.9%** of the variance in under-5 mortality rates
- Every **1 µg/m³ increase in PM2.5** is associated with **0.85 additional deaths per 1,000 children**
- Urban areas show **higher PM2.5 concentrations** than rural areas
- Correlation between PM2.5 and U5MR: **r = 0.33** (p < 0.001)

## 📁 Project Structure

```
Project/
├── config.py                 # Centralized configuration
├── requirements.txt          # Python dependencies
├── main.py                   # Phase 1: Basic runnable version
├── main_modular.py          # Phase 2: Modular version (recommended)
│
├── src/                     # Source code modules
│   ├── __init__.py
│   ├── data_processing.py   # Data loading and cleaning
│   ├── visualization.py     # Plotting functions
│   └── statistical_analysis.py  # Statistical tests
│
├── data/
│   ├── raw/                 # Original data files
│   └── processed/           # Cleaned datasets
│       ├── who_pm25_long.csv
│       ├── who_pm25_wide.csv
│       ├── unicef_u5mr_long.csv
│       └── merged_pm25_u5mr.csv
│
├── reports/
│   ├── figures/             # Generated plots
│   └── tables/              # Statistical summaries
│
└── models/                  # Trained ML models (Phase 3+)
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Analysis

**Option 1: Modular Version (Recommended)**
```bash
python main_modular.py
```

**Option 2: Basic Version**
```bash
python main.py
```

## 📦 Data Sources

- **WHO PM2.5 Data**: `who_pm25_2022.csv` - Global PM2.5 concentrations (2010-2019)
  - Urban, Rural, and Total population exposure
  - 195 countries, 5,810 observations
  
- **UNICEF U5MR Data**: `unicef_u5mr_2023.xlsx` - Under-5 Mortality Rates (1990-2023)
  - Deaths per 1,000 live births
  - 200 countries, 7,000 observations

## 📈 Analysis Pipeline

### Phase 1: Data Processing ✅
- Load and clean WHO PM2.5 data
- Load and clean UNICEF U5MR data
- Merge datasets on Country + Year
- Handle missing values and outliers
- Generate processed datasets

### Phase 2: Modular Code Structure ✅
- Separate modules for different functionalities
- Centralized configuration
- Clean, maintainable code
- Comprehensive documentation

### Phase 3: Machine Learning Pipeline 🚧 (In Progress)
- Time-aware train/test splits
- Multiple model comparison (Ridge, Lasso, Random Forest, XGBoost, etc.)
- Cross-validation
- Feature importance analysis
- SHAP value explanations

### Phase 4: Advanced Analysis 📋 (Planned)
- Feature engineering (GDP, health expenditure, urbanization)
- Causality analysis
- Regional heterogeneity
- Interaction effects

### Phase 5: Enhanced Reporting 📋 (Planned)
- Publication-quality visualizations
- Interactive dashboards
- Geographic heat maps
- Comprehensive final report

## 📊 Generated Outputs

### Processed Data
- `who_pm25_long.csv` - WHO data in long format
- `who_pm25_wide.csv` - WHO data pivoted by residence type
- `unicef_u5mr_long.csv` - UNICEF data in long format
- `merged_pm25_u5mr.csv` - Combined dataset for analysis

### Visualizations
- Correlation heatmap
- PM2.5 vs U5MR scatter plot with regression line
- Urban vs Rural PM2.5 comparison
- Top 10 countries by PM2.5
- Time series plots for sample countries

### Statistical Reports
- Summary statistics (mean, std, min, max, quartiles)
- Linear regression results
- Pearson correlation tests

## 🔧 Configuration

All settings can be modified in `config.py`:
- File paths
- Column mappings
- Analysis parameters
- Visualization settings
- Model hyperparameters

## 📝 Code Quality Improvements

### What Was Fixed from Original Code:
1. ✅ **Removed Google Colab dependencies** (`drive.mount`, `!pip`, `display()`)
2. ✅ **Fixed file paths** for local execution
3. ✅ **Modularized code** into separate, reusable functions
4. ✅ **Added error handling** for missing files and columns
5. ✅ **Centralized configuration** in `config.py`
6. ✅ **Removed code duplication** (WHO data processed 3 times in original)
7. ✅ **Added comprehensive documentation** and docstrings
8. ✅ **Fixed Unicode issues** for Windows console compatibility
9. ✅ **Improved data validation** and cleaning
10. ✅ **Better variable naming** and code organization

## 🎓 Technologies Used

- **Python 3.10+**
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **matplotlib** & **seaborn** - Visualization
- **scikit-learn** - Machine learning
- **statsmodels** - Statistical analysis
- **xgboost** - Gradient boosting
- **shap** - Model interpretability
- **country-converter** - ISO3 code conversion

## 📖 Usage Examples

### Load Processed Data
```python
from src import data_processing
import config

# Load all processed datasets
data = data_processing.load_processed_data()
merged_df = data['merged']
```

### Create Custom Visualizations
```python
from src import visualization

# Plot scatter with regression
visualization.plot_scatter_with_regression(
    merged_df, 
    'PM25_Total_ugm3', 
    'U5MR_per_1000',
    title="My Custom Plot"
)
```

### Perform Statistical Tests
```python
from src import statistical_analysis

# Run regression analysis
model, summary = statistical_analysis.simple_linear_regression(
    merged_df,
    'PM25_Total_ugm3',
    'U5MR_per_1000'
)
```

## 🤝 Contributing

This is an academic project. Suggestions for improvements:
1. Add more confounding variables (GDP, education, healthcare access)
2. Implement causal inference methods (propensity scores, IV analysis)
3. Add time-series forecasting
4. Create interactive dashboards with Plotly/Dash
5. Implement deep learning models

## 📄 License

Academic project for educational purposes.

## ✉️ Contact

For questions or collaboration opportunities, please reach out through the course channels.

---

**Last Updated**: December 8, 2025  
**Status**: Phase 2 Complete | Phase 3 In Progress

