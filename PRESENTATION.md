# Air Pollution and Child Mortality: A Machine Learning Analysis

## Presentation Slide Structure

---

## SLIDE 1: Title Slide
**Title:** Air Pollution and Child Mortality: A Machine Learning Analysis

**Subtitle:** Predicting Under-5 Mortality Rates using PM2.5 and Socio-Economic Factors

**Your Name**  
Machine Learning - Fall 2025  
San Jose State University

---

## SLIDE 2: Research Question & Motivation

**Research Question:**
> Can we predict child mortality rates from air pollution levels? What is the causal impact of PM2.5 pollution on under-5 mortality?

**Motivation:**
- 7 million premature deaths annually from air pollution (WHO)
- Children are especially vulnerable to environmental hazards
- Understanding this relationship can inform public health policy

**Key Innovation:**
- Moving beyond correlation to establish causation
- Using machine learning + causal inference methods
- Controlling for socio-economic confounders

---

## SLIDE 3: Data Sources

### WHO PM2.5 Data
- **Source:** World Health Organization Global Health Observatory
- **Coverage:** 195 countries, 2010-2022
- **Features:** Urban, rural, and total PM2.5 concentrations (μg/m³)

### UNICEF U5MR Data
- **Source:** UNICEF Child Mortality Database
- **Coverage:** 7,000+ observations across countries and years
- **Target:** Under-5 Mortality Rate (deaths per 1,000 live births)

### World Bank Socio-Economic Data
- **Features:** GDP per capita, urbanization rate, fertility rate, health expenditure
- **Purpose:** Control for confounding factors

**Final Dataset:** 1,950 country-year observations

---

## SLIDE 4: Exploratory Data Analysis (Heatmap)

[INSERT: correlation_matrix.png]

**Key Findings:**
- Moderate positive correlation between PM2.5 and U5MR (r ≈ 0.5)
- Urban PM2.5 > Rural PM2.5 in most countries
- Suggests relationship exists, but need to control for confounders

---

## SLIDE 5: Geographic Patterns (World Map)

[INSERT: pm25_world_map.png OR choropleth_pm25_2022.html screenshot]

**Observations:**
- Highest PM2.5: South Asia, Middle East, North Africa
- Lowest PM2.5: Northern Europe, Australia, North America
- Clear geographic clustering suggests socio-economic factors at play

---

## SLIDE 6: The Confounding Problem

### Why We Can't Just Use PM2.5 Alone

**The Challenge:**
```
PM2.5 → U5MR ✓
   ↑
   |
GDP, Health Spending, Education → U5MR ✓
```

**Confounders We Control For:**
1. **GDP per capita** - Wealthier countries have better healthcare
2. **Health expenditure** - More spending = better outcomes
3. **Urbanization** - Urban areas have different health infrastructure
4. **Fertility rate** - Family size affects child health

**Without controlling for these, we measure correlation, not causation!**

---

## SLIDE 7: Machine Learning Approach

### Feature Sets Tested

#### Set 1: PM2.5 Only (3 features)
- PM2.5 Total, Urban, Rural

#### Set 2: PM2.5 + Confounders (7 features)
- PM2.5 variables
- Log(GDP per capita)
- Log(Health expenditure)
- Urbanization rate
- Fertility rate

#### Set 3: Full with Interactions (12 features)
- All above + engineered features
- PM2.5 × GDP interaction
- PM2.5 × Urbanization interaction
- Polynomial terms

---

## SLIDE 8: Models Tested

### 6 Machine Learning Models

**Linear Models:**
- Ridge Regression
- Lasso Regression
- ElasticNet

**Tree-Based Models:**
- Random Forest ⭐ (Best performance)
- XGBoost
- Gradient Boosting

**Training Strategy:**
- Time-aware split: Train on ≤2015, Test on >2015
- 5-fold cross-validation
- Grid search for hyperparameter tuning

---

## SLIDE 9: **THE KEY RESULT** - Impact of Confounders

[INSERT: confounder_impact.png]

### Performance Comparison

| Metric | PM2.5 Only | PM2.5 + Confounders | Improvement |
|--------|-----------|---------------------|-------------|
| **R² Score** | 0.22 | **0.89** | **+305%** |
| **MAE** | 17.5 | **6.2** | **-65%** |
| **Variance Explained** | 22% | **89%** | **+67 pp** |

**Best Model:** Random Forest with Socio-Economic Confounders

**Interpretation:**
- PM2.5 alone explains only 22% of child mortality variation
- Adding socio-economic factors explains 89% of variation
- **This shows confounders are CRITICAL for accurate prediction**

---

## SLIDE 10: Feature Importance - What Really Matters?

[INSERT: feature_importance_with_confounders.png]

### Top 5 Most Important Features:

1. **Fertility Rate** - 71.1%
2. **Log(GDP per capita)** - 11.9%
3. **Log(Health expenditure)** - 8.2%
4. **PM2.5 Total** - 3.7%
5. **PM2.5 Urban** - 2.9%

**Key Insight:**
- Socio-economic factors dominate predictions
- **BUT** PM2.5 still has independent predictive power
- This suggests a causal pathway even after controlling for confounders

---

## SLIDE 11: Causal Inference - Propensity Score Matching

### Moving from Prediction to Causation

**Method:** Propensity Score Matching (PSM)

**Goal:** Estimate the causal effect of "high pollution" vs "low pollution"

**Approach:**
1. Split countries into High PM2.5 (>25 μg/m³) vs Low PM2.5 (≤25 μg/m³)
2. Match similar countries on confounders (GDP, health spending, etc.)
3. Compare U5MR between matched pairs

**Results:**
[INSERT: Key numbers from causal_inference_summary.csv]

**Interpretation:**
- After controlling for confounders through matching...
- High-pollution countries still have higher child mortality
- **This is evidence of a causal effect, not just correlation**

---

## SLIDE 12: SHAP Analysis - Model Interpretability

[INSERT: shap_beeswarm.png OR shap_summary.png]

### What is SHAP?
- **SH**apley **A**dditive ex**P**lanations
- Shows how each feature contributes to individual predictions
- Answers: "Why did the model predict X for this country?"

**What the plot shows:**
- Each dot = one country-year observation
- Red = high feature value, Blue = low feature value
- Position shows impact on prediction

**Key Findings:**
- High fertility → increases U5MR prediction
- High GDP → decreases U5MR prediction
- High PM2.5 → increases U5MR prediction (even after controlling for GDP!)

---

## SLIDE 13: Model Performance Across All Feature Sets

[INSERT: feature_set_comparison.png]

### Comparison of All Models and Feature Sets

**Observations:**
1. **Random Forest performs best** across all feature sets
2. **Massive jump** when adding socio-economic confounders
3. Interaction terms provide small additional improvement

**Why Random Forest Wins:**
- Handles non-linear relationships well
- Robust to outliers
- Captures interactions automatically
- Less prone to overfitting than individual trees

---

## SLIDE 14: Statistical Validation

### Model Reliability Metrics

**Cross-Validation Score:** 0.887
- Model performs consistently across different data splits

**Time-Based Validation:**
- Trained on 2010-2015 data
- Tested on 2016-2022 data
- Strong performance suggests model generalizes to new time periods

**Error Analysis:**
- Mean Absolute Error: 6.2 deaths per 1,000 births
- Median Absolute Error: 3.5 (most predictions very close)
- RMSE: 10.0 (reasonable given U5MR ranges from 1-130)

---

## SLIDE 15: Lessons Learned

### Technical Lessons

1. **Confounders Matter!** 
   - Always control for obvious confounding variables
   - PM2.5-only model was essentially useless (R²=0.22)

2. **Feature Engineering is Powerful**
   - Log transforms for skewed variables (GDP, health spending)
   - Interaction terms (PM2.5 × GDP) capture complex relationships

3. **Tree-Based Models Excel Here**
   - Random Forest > XGBoost > Gradient Boosting > Linear models
   - Non-linear relationships are important in this domain

### Domain Lessons

4. **Socio-Economic Context Dominates**
   - Fertility rate is the #1 predictor
   - GDP and health spending are crucial
   - But pollution still has independent effect!

5. **Geographic Patterns Are Stark**
   - Highest burden: South Asia, Sub-Saharan Africa
   - Policy implications: Need both pollution control AND economic development

---

## SLIDE 16: Project Management & Tools

### Version Control
- **GitHub Repository:** https://github.com/odankhrara/ML-project
- 50+ commits with clear messages
- Modular code structure

### Agile Development
- **Phase 1:** Data cleaning & EDA
- **Phase 2:** Basic ML models
- **Phase 3:** Feature engineering & confounders
- **Phase 4:** Advanced features (SHAP, causality, dashboard)
- **Phase 5:** Presentation preparation

### Pair Programming with AI
- Used **Cursor AI** for:
  - Code refactoring and optimization
  - Debugging (Unicode errors, data loading issues)
  - Best practices suggestions
  - Documentation generation

---

## SLIDE 17: Code Walkthrough - Key Components

### Project Structure
```
├── src/
│   ├── data_processing.py      # Data loading & cleaning
│   ├── feature_engineering.py  # World Bank data & features
│   ├── ml_pipeline.py          # Model training & evaluation
│   ├── interpretability.py     # SHAP analysis
│   ├── causal_inference.py     # PSM, DiD, IV
│   └── visualization.py        # Plots
├── tests/
│   └── test_data_processing.py # Unit tests (pytest)
├── streamlit_dashboard.py      # Interactive dashboard
├── config.py                   # Centralized configuration
├── requirements.txt            # Dependencies
└── run_with_confounders.py     # Main analysis script
```

---

## SLIDE 18: Live Demo

### Streamlit Dashboard

**Features:**
1. **Data Explorer** - Filter by country, year, pollution level
2. **Geographic Maps** - Interactive world maps, animations
3. **Statistical Analysis** - Correlation, regression results
4. **Machine Learning** - Model comparison, predictions
5. **Causal Inference** - PSM results, treatment effects
6. **Download Results** - Export tables and figures

**Demo Plan:**
1. Show PM2.5 world map for 2022
2. Filter to high-pollution countries
3. Display model predictions vs actual U5MR
4. Show SHAP force plot for a specific country
5. Demonstrate PSM matched pairs

---

## SLIDE 19: Key Findings Summary

### What We Discovered

1. **PM2.5 pollution has a measurable but modest independent effect on child mortality**
   - After controlling for GDP, health spending, fertility, and urbanization
   - PM2.5 contributes ~4-6% of feature importance

2. **Socio-economic factors are the dominant drivers**
   - Fertility rate alone explains 71% of model importance
   - Economic development (GDP) is crucial

3. **Model performance dramatically improves with confounders**
   - R² jumps from 0.22 → 0.89 (+305%)
   - Essential for policy-relevant predictions

4. **Tree-based ML models outperform linear models**
   - Random Forest is best: R²=0.89, MAE=6.2

5. **Causal inference confirms effect**
   - Propensity Score Matching shows pollution effect persists after matching

---

## SLIDE 20: Policy Implications

### What Should Policymakers Do?

1. **Integrated Approach Required**
   - Reducing PM2.5 alone won't drastically reduce child mortality
   - Must combine with:
     - Economic development (↑ GDP)
     - Healthcare investment (↑ health spending)
     - Family planning (↓ fertility rate)

2. **Target High-Burden Regions**
   - South Asia: High PM2.5 + moderate U5MR
   - Sub-Saharan Africa: Moderate PM2.5 + very high U5MR
   - Different interventions needed for different contexts

3. **Monitor Both Environmental and Socio-Economic Indicators**
   - PM2.5 monitoring is important but insufficient
   - Track GDP, health spending, fertility together

4. **Use Predictive Models for Resource Allocation**
   - Our model can identify countries at highest risk
   - Target interventions where they'll have most impact

---

## SLIDE 21: Future Work

### How to Extend This Project

1. **More Confounders**
   - Education levels (maternal education especially)
   - Access to clean water and sanitation
   - Vaccination rates
   - Healthcare infrastructure (doctors per capita)

2. **Other Pollutants**
   - PM10, NO₂, SO₂, Ozone
   - Indoor air pollution (cooking fuel)

3. **Time-Series Forecasting**
   - Predict future U5MR trends
   - Simulate policy interventions

4. **Deep Learning**
   - Neural networks for non-linear relationships
   - Embedding techniques for country representations

5. **Causal Methods**
   - Difference-in-Differences for policy changes
   - Instrumental Variables (e.g., monsoon wind patterns for PM2.5)

---

## SLIDE 22: Technical Challenges & Solutions

### Challenges We Overcame

| Challenge | Solution |
|-----------|----------|
| Google Colab code won't run locally | Refactored to remove Colab dependencies |
| Missing data in socio-economic variables | Used left join + dropna strategy |
| Unicode encoding errors (Windows) | Replaced emoji with ASCII indicators |
| Overfitting with PM2.5-only models | Added cross-validation + time-based split |
| Model interpretability | Implemented SHAP analysis |
| Correlation vs causation | Added Propensity Score Matching |
| Large dataset visualization | Built interactive Streamlit dashboard |
| Feature collinearity | Used tree-based models (handle collinearity well) |

---

## SLIDE 23: Testing & Validation

### Ensuring Code Quality

**Unit Tests (pytest):**
- `test_data_processing.py`
- Tests for column picking, residence categorization, ISO3 codes, merging
- All tests pass ✅

**Model Validation:**
- Time-based train/test split (prevent data leakage)
- 5-fold cross-validation
- Hyperparameter tuning with GridSearchCV

**Data Validation:**
- Check for missing values
- Verify country code mappings (195 countries)
- Outlier detection and handling

**Code Quality:**
- Modular structure (separate .py files for each component)
- Type hints in function signatures
- Docstrings for all functions
- Configuration management (config.py)

---

## SLIDE 24: Reproducibility

### How to Run This Project

1. **Clone the repository:**
   ```bash
   git clone https://github.com/odankhrara/ML-project
   cd ML-project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analysis:**
   ```bash
   python run_with_confounders.py
   ```

4. **Launch dashboard:**
   ```bash
   streamlit run streamlit_dashboard.py
   ```

**All code, data, and documentation available on GitHub!**

---

## SLIDE 25: Conclusion

### Summary

- **Built a machine learning pipeline** to predict child mortality from air pollution and socio-economic factors

- **Demonstrated the critical importance of controlling for confounders** (R² 0.22 → 0.89)

- **Used causal inference** to move beyond correlation to establish causation

- **Created production-quality code** with testing, documentation, and interactive dashboard

- **Discovered that while PM2.5 has an effect, socio-economic factors dominate**

### The Big Picture
Air pollution is a serious health threat, but addressing child mortality requires **integrated solutions** that tackle poverty, healthcare access, and environmental quality together.

---

## SLIDE 26: Q&A

**Questions?**

Thank you for your attention!

**Resources:**
- 📊 GitHub: https://github.com/odankhrara/ML-project
- 📧 Contact: [Your Email]
- 📄 Full Report: See `PROJECT_REPORT.md`

---

## APPENDIX SLIDES (If Needed)

### A1: Data Preprocessing Details
- WHO PM2.5 data: Wide to long format conversion
- UNICEF data: Skipping header rows, median estimates only
- Country name standardization using country_converter
- ISO3 code matching (195 countries successfully matched)

### A2: Hyperparameter Tuning Details
- Random Forest: max_depth, min_samples_leaf
- XGBoost: learning_rate, max_depth, n_estimators, subsample
- Gradient Boosting: learning_rate, max_depth, n_estimators
- Grid search with 5-fold CV on training set

### A3: Mathematical Formulation
- Target: U5MR_t,c (Under-5 Mortality Rate for country c at time t)
- Features: PM25_t,c, GDP_t,c, Health_t,c, Urban_t,c, Fertility_t,c
- Model: U5MR = f(PM25, GDP, Health, Urban, Fertility) + ε
- Loss function: Mean Squared Error (for regression)

### A4: Propensity Score Matching Details
- Treatment: PM2.5 > 25 μg/m³
- Control: PM2.5 ≤ 25 μg/m³
- Matching variables: log(GDP), log(health exp), urban%, fertility
- Matching method: Nearest neighbor with caliper
- Balance check: Standardized mean differences < 0.1

### A5: SHAP Mathematical Background
- Shapley values from cooperative game theory
- Additive feature attribution method
- SHAP value = contribution of feature to deviation from expected prediction
- Properties: local accuracy, missingness, consistency

---

## PRESENTATION TIPS

### Timing (15-20 minutes)
- Slides 1-6: Problem & Data (5 min)
- Slides 7-14: Methods & Results (7 min)
- Slides 15-18: Technical Details & Demo (5 min)
- Slides 19-25: Findings & Conclusion (3 min)
- Slide 26: Q&A (5 min)

### What to Emphasize
1. **The confounder result** (Slide 9) - This is your main finding!
2. **Feature importance** (Slide 10) - Shows what really matters
3. **Live demo** (Slide 18) - Makes it tangible
4. **Lessons learned** (Slide 15) - Shows reflection

### Demo Preparation
- Have dashboard running before presentation
- Prepare 3-4 specific examples to show:
  - Country with high PM2.5 and high U5MR (e.g., India)
  - Country with high PM2.5 but low U5MR (e.g., Saudi Arabia) - shows confounders matter!
  - Matched pairs from PSM
  - SHAP force plot for one specific prediction

### Handling Q&A
**Likely questions:**
1. "Why not use deep learning?" → Answer: Random Forest performed excellently, easier to interpret
2. "How do you know it's causal?" → Answer: PSM + controlling for major confounders
3. "What about other pollutants?" → Answer: Future work, PM2.5 is most harmful to children
4. "Why is fertility so important?" → Answer: Family size affects resource allocation, maternal health
5. "Can you predict for new countries?" → Answer: Yes, need same feature set


