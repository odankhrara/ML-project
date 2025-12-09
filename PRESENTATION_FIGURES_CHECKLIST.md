# Presentation Figures Checklist

## MUST-HAVE Figures for Presentation (Based on Rubric)

### 1. **Exploratory Analysis** (Rubric: "Visualization - exploratory analysis" - 2 pts)

✅ **SLIDE 4**: `01_correlation_matrix.png`
- **Purpose**: Heatmap showing correlations between all variables
- **What it shows**: PM2.5 correlates with U5MR (~0.5), but also with GDP, health expenditure
- **Talking point**: "This exploratory heatmap reveals that PM2.5 correlates with mortality, but confounders like GDP also correlate with both"

✅ **SLIDE 5**: `map_pm25.html` (screenshot) OR `map_bubble_pm25_u5mr.html`
- **Purpose**: Geographic visualization of PM2.5 levels globally
- **What it shows**: South Asia, Middle East, North Africa have highest PM2.5
- **Talking point**: "Clear geographic clustering suggests structural, socio-economic factors at play"

### 2. **Model Comparison** (Rubric: "Demo" - 5 pts)

✅ **SLIDE 9**: `confounder_impact.png` ⭐ **MOST IMPORTANT**
- **Purpose**: Direct comparison of PM2.5-only vs PM2.5+Confounders
- **What it shows**: R² jumps from 0.22 → 0.89 (+305%)
- **Talking point**: "This is THE key finding. Adding confounders transforms the model from useless to highly predictive"

✅ **SLIDE 13**: `feature_set_comparison.png`
- **Purpose**: Shows all 3 feature sets across all models
- **What it shows**: Random Forest consistently best, massive improvement with confounders
- **Talking point**: "Random Forest outperforms XGBoost and Gradient Boosting across all feature sets"

### 3. **Feature Importance** (Rubric: "Visualization" - 2 pts)

✅ **SLIDE 10**: `feature_importance_with_confounders.png`
- **Purpose**: Shows what features drive predictions
- **What it shows**: Fertility (71%), GDP (12%), Health (8%), PM2.5 (4-6%)
- **Talking point**: "Socio-economic factors dominate, but PM2.5 still has independent effect"

### 4. **Model Interpretability** (Rubric: "Code Walkthrough" - 5 pts)

✅ **SLIDE 12**: Use one of:
- `shap_waterfall_Champion_RandomForest_sample0.png`
- `shap_waterfall_Champion_RandomForest_sample1.png`
- `shap_waterfall_Champion_RandomForest_sample2.png`

- **Purpose**: Explain SHAP analysis and model interpretability
- **What it shows**: How each feature contributes to a specific prediction
- **Talking point**: "SHAP values show why the model predicted X for this specific country"

### 5. **Model Performance** (Rubric: "Demo" - 5 pts)

✅ **SLIDE 14** (or in Demo): `predictions_champion_model.png`
- **Purpose**: Predictions vs actual values
- **What it shows**: How well the model predicts on test set
- **Talking point**: "Points near the diagonal line indicate accurate predictions. Our model performs well across the full range"

---

## OPTIONAL/BONUS Figures

### For Deep Dive Discussion

⭕ **SLIDE 3 or APPENDIX**: `02_pm25_vs_u5mr_scatter.png`
- Scatter plot showing PM2.5 vs U5MR relationship
- Good for showing "there's a relationship, but it's messy"

⭕ **SLIDE 4**: `03_urban_vs_rural_pm25.png`
- Shows urban PM2.5 is generally higher than rural
- Good for context on PM2.5 exposure patterns

⭕ **SLIDE 5 ALTERNATIVE**: `04_top10_countries_pm25.png`
- Bar chart of countries with highest PM2.5
- Easier to digest than map for some audiences

⭕ **DEMO**: `map_pm25_animated.html`
- Animated map showing PM2.5 changes over time
- Great for live demo visual impact

---

## Figure Usage by Rubric Category

### 1. **Visualization (2 pts)**
- Primary: `01_correlation_matrix.png` (heatmap)
- Primary: `map_pm25.html` (geographic visualization)
- Bonus: `map_bubble_pm25_u5mr.html` (interactive bubble map)

### 2. **Demo (5 pts)**
- Live Streamlit dashboard showing:
  - Data exploration
  - Interactive maps
  - Model predictions
  - SHAP explanations
- Figures to show IN demo:
  - `confounder_impact.png`
  - `predictions_champion_model.png`
  - `feature_importance_with_confounders.png`

### 3. **Code Walkthrough (5 pts)**
- Show project structure (from SLIDE 17)
- Explain pipeline: data → features → models → evaluation
- Reference: `feature_set_comparison.png` to show systematic approach
- Reference: SHAP waterfall to show interpretability

### 4. **Presentation Skills (5 pts)**
- Use figures to tell a story:
  1. Problem (correlation matrix)
  2. Geography (map)
  3. Approach (feature sets)
  4. Key result (confounder impact) ⭐
  5. Interpretation (feature importance)
  6. Validation (predictions vs actual)

### 5. **Discussion/Q&A (5 pts)**
- Have ready:
  - `feature_importance_with_confounders.png` → "Why is fertility so important?"
  - `confounder_impact.png` → "How much better is your model?"
  - `map_pm25.html` → "Which regions should policymakers focus on?"

---

## Figures NOT Needed for Presentation

These are good for reports but not presentation:
- ❌ `model_comparison_pm25_only.png` - superseded by `confounder_impact.png`
- ❌ `feature_importance_RandomForest_pm25_only.png` - superseded by with_confounders version
- ❌ `predictions_RandomForest_pm25_only.png` - PM2.5-only model is bad, don't feature it
- ❌ `05_timeseries_Afghanistan.png` - Too specific, not generalizable
- ❌ `map_u5mr.html` - Mortality map is less interesting than PM2.5 map

---

## Recommended Slide-Figure Mapping

| Slide # | Slide Topic | Figure File | Purpose |
|---------|-------------|-------------|---------|
| 4 | EDA | `01_correlation_matrix.png` | Show correlations |
| 5 | Geographic | `map_pm25.html` screenshot | Show pollution hotspots |
| 9 | **KEY RESULT** | `confounder_impact.png` | Show +305% improvement |
| 10 | Feature Importance | `feature_importance_with_confounders.png` | What drives predictions |
| 12 | Interpretability | `shap_waterfall_sample0.png` | SHAP explanation |
| 13 | Model Comparison | `feature_set_comparison.png` | All models/features |
| 14 | Validation | `predictions_champion_model.png` | Model accuracy |
| 18 | Demo | Streamlit dashboard (live) | Interactive exploration |

---

## Creating PowerPoint/Google Slides

### Insert Figures:
1. Open your slide deck
2. For each slide, Insert → Image → From File
3. Resize to fill slide (leave room for title and caption)
4. Add brief caption below figure

### Screenshot HTML Maps:
For the interactive maps (`.html` files):
1. Open in browser (double-click file)
2. Take screenshot (Windows: Win+Shift+S)
3. Paste into slide

OR use the Streamlit dashboard during live demo instead!

### Figure Size Tips:
- Correlation matrix: Make large enough to read labels
- Confounder impact: Center prominently, this is your key result
- Feature importance: Ensure feature names are legible
- SHAP waterfall: May need to crop/zoom to focus on top features

---

## Print/Export Checklist

Before presenting, print these as backup:
- [ ] `confounder_impact.png`
- [ ] `feature_importance_with_confounders.png`
- [ ] `feature_set_comparison.png`
- [ ] Screenshot of Streamlit dashboard
- [ ] Summary table from `model_comparison_with_confounders.csv`

In case:
- Laptop won't connect to projector
- Internet fails (for HTML maps)
- Streamlit dashboard won't load

---

## Demo Preparation

### Before Presentation:
1. Start Streamlit dashboard:
   ```bash
   streamlit run streamlit_dashboard.py
   ```

2. Open in browser: `http://localhost:8501`

3. Prepare these views:
   - **Homepage** → Quick overview
   - **Data Explorer** → Filter to high PM2.5 countries
   - **Geographic Maps** → PM2.5 world map 2022
   - **Machine Learning** → Model comparison chart
   - **Causal Inference** → PSM results

4. Bookmark/tab each page for quick switching

### During Demo (5 min):
- **1 min**: Data Explorer - show filtering
- **1 min**: Geographic Map - show hotspots
- **2 min**: Machine Learning - show model comparison
- **1 min**: Feature Importance - explain top features

### Demo Script:
"Let me show you our interactive dashboard. [Click Data Explorer]
 Here I can filter to high-pollution countries... [select >35]
 We see India, Pakistan, Bangladesh. [Click Maps]
 This geographic view shows South Asia as a hotspot. [Click ML]
 Here's our model comparison - you can see the dramatic improvement
 with confounders. [Click Feature Importance]
 And this shows fertility rate is the dominant factor."

---

## Final Presentation Flow (with Figures)

```
OPENING (5 min)
├─ Slide 1-3: Problem & Data
└─ Slide 4-5: EDA with HEATMAP + MAP

METHODS & RESULTS (7 min)
├─ Slide 6-8: Approach
├─ Slide 9: 🌟 KEY RESULT with CONFOUNDER_IMPACT.PNG
├─ Slide 10: FEATURE_IMPORTANCE.PNG
├─ Slide 11: Causality (text only)
├─ Slide 12: SHAP waterfall
├─ Slide 13: FEATURE_SET_COMPARISON.PNG
└─ Slide 14: PREDICTIONS vs ACTUAL.PNG

TECHNICAL (5 min)
├─ Slide 15-17: Lessons, Project Mgmt, Code
└─ Slide 18: 🎬 LIVE DEMO (Streamlit)

CONCLUSION (3 min)
├─ Slide 19-20: Findings & Policy
├─ Slide 21-25: Future, Challenges, Testing, Reproducibility, Conclusion
└─ Slide 26: Q&A
```

---

## Presentation Success Criteria (Rubric)

To maximize points:

✅ **Visualization (2 pts)**
   - Show correlation heatmap ✓
   - Show geographic map ✓
   - Show feature importance ✓

✅ **Demo (5 pts)**
   - Live Streamlit dashboard ✓
   - Show data exploration ✓
   - Show model predictions ✓
   - Show interactive features ✓

✅ **Code Walkthrough (5 pts)**
   - Explain modular structure ✓
   - Show src/ directory ✓
   - Reference tests/ directory ✓
   - Show config.py ✓

✅ **Presentation Skills (5 pts)**
   - Clear narrative arc ✓
   - Engaging visuals ✓
   - Time management (15-20 min) ✓

✅ **Discussion/Q&A (5 pts)**
   - Prepared answers ✓
   - Can explain technical choices ✓
   - Can discuss limitations ✓

✅ **Version Control (3 pts)**
   - GitHub repo with code ✓
   - README with instructions ✓
   - Commit history ✓

✅ **Lessons Learned (5 pts)**
   - Dedicated slide (15) ✓
   - Technical + domain insights ✓

✅ **Slides (5 pts)**
   - Professional appearance ✓
   - Clear figures ✓
   - Proper citations ✓

✅ **Saving Model (3 pts)**
   - Model saved in models/ directory ✓
   - Can load and demo quickly ✓

✅ **Creative Presentation (2 pts)**
   - Interactive dashboard ✓
   - Animated maps ✓
   - SHAP visualizations ✓

---

## Quick Reference: Key Numbers to Memorize

For Q&A, memorize these:
- **Dataset**: 1,950 observations, 195 countries, 2010-2022
- **R² improvement**: 0.22 → 0.89 (+305%)
- **MAE**: 6.2 deaths per 1,000 live births
- **Top feature**: Fertility rate (71.1% importance)
- **Best model**: Random Forest with 7 features
- **Training strategy**: Time-aware split (≤2015 train, >2015 test)
- **Cross-validation**: 5-fold, score = 0.887
- **Feature sets**: 3 (PM2.5-only), 7 (+ confounders), 12 (+ interactions)
- **Models tested**: 6 (Ridge, Lasso, ElasticNet, RF, XGBoost, GradientBoosting)

---

## Final Checklist Before Presenting

Day Before:
- [ ] Slides created with all figures
- [ ] Streamlit dashboard tested
- [ ] GitHub repo is public
- [ ] Practiced presentation timing (15-20 min)
- [ ] Reviewed Q&A preparation
- [ ] Laptop charged

1 Hour Before:
- [ ] Start Streamlit dashboard
- [ ] Test projector connection
- [ ] Have backup slides as PDF
- [ ] Have printed figures (just in case)
- [ ] GitHub URL ready to share

During Presentation:
- [ ] Spend 2+ min on Slide 9 (key result)
- [ ] Emphasize +305% improvement
- [ ] Show live demo (5 min)
- [ ] Invite questions throughout
- [ ] Stay within time limit

Good luck! You have excellent results and a great story to tell. 🎉


