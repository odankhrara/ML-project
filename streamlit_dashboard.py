"""
Interactive Streamlit Dashboard
Air Pollution & Under-5 Mortality Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from src import data_processing, visualization, ml_pipeline, geographic_viz

# Page configuration
st.set_page_config(
    page_title="Air Pollution & Child Mortality Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load processed data"""
    try:
        data = data_processing.load_processed_data(verbose=False)
        return data
    except:
        return None


@st.cache_data
def load_extended_data():
    """Load extended dataset with features"""
    extended_path = os.path.join(config.PROCESSED_DATA_DIR, 'merged_extended.csv')
    if os.path.exists(extended_path):
        return pd.read_csv(extended_path)
    return None


def main():
    # Title and description
    st.title("🌍 Air Pollution & Under-5 Mortality Analysis")
    st.markdown("""
    **Interactive Dashboard** exploring the relationship between PM2.5 air pollution 
    and child mortality rates across 195 countries (2010-2018).
    """)
    
    # Load data
    with st.spinner('Loading data...'):
        data = load_data()
        extended_data = load_extended_data()
    
    if data is None:
        st.error("❌ Could not load data. Please run main_complete.py first.")
        return
    
    merged_df = data['merged']
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Data Explorer", "Geographic Maps", "Statistical Analysis", 
         "Machine Learning", "Causal Inference", "About"]
    )
    
    # ========================================================================
    # PAGE 1: OVERVIEW
    # ========================================================================
    
    if page == "Overview":
        st.header("📈 Key Findings at a Glance")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Countries Analyzed",
                f"{merged_df['Country_ISO3'].nunique()}",
                help="Total number of countries in dataset"
            )
        
        with col2:
            st.metric(
                "Observations",
                f"{len(merged_df):,}",
                help="Total country-year observations"
            )
        
        with col3:
            avg_pm25 = merged_df['PM25_Total_ugm3'].mean() if 'PM25_Total_ugm3' in merged_df.columns else 0
            st.metric(
                "Avg PM2.5",
                f"{avg_pm25:.1f} µg/m³",
                help="Average PM2.5 concentration"
            )
        
        with col4:
            avg_u5mr = merged_df['U5MR_per_1000'].mean() if 'U5MR_per_1000' in merged_df.columns else 0
            st.metric(
                "Avg U5MR",
                f"{avg_u5mr:.1f}",
                help="Average under-5 mortality rate (per 1,000)"
            )
        
        st.markdown("---")
        
        # Key findings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔬 Statistical Findings")
            st.markdown("""
            - **Correlation**: r = 0.33 (p < 0.001) ***
            - **Effect Size**: +1 µg/m³ PM2.5 → +0.85 U5MR
            - **Variance Explained**: 10.9% (linear model)
            - **Urban vs Rural**: Urban PM2.5 14% higher
            """)
            
            # Load regression summary
            reg_file = os.path.join(config.TABLES_DIR, 'regression_summary.txt')
            if os.path.exists(reg_file):
                with st.expander("📄 View Full Regression Output"):
                    with open(reg_file, 'r') as f:
                        st.text(f.read())
        
        with col2:
            st.subheader("🤖 Machine Learning Results")
            
            # Load model results
            model_results_path = os.path.join(config.TABLES_DIR, 'model_results_pm25_only.csv')
            if os.path.exists(model_results_path):
                model_results = pd.read_csv(model_results_path)
                best_model = model_results.iloc[0]
                
                st.markdown(f"""
                - **Best Model**: {best_model['Model']}
                - **R² Score**: {best_model['R2']:.3f}
                - **MAE**: {best_model['MAE']:.2f}
                - **RMSE**: {best_model['RMSE']:.2f}
                """)
                
                with st.expander("📊 View All Model Comparison"):
                    st.dataframe(model_results[['Model', 'R2', 'MAE', 'RMSE', 'MedAE']])
        
        # Correlation heatmap
        st.subheader("🔥 Correlation Heatmap")
        pm_cols = [c for c in ['PM25_Total_ugm3', 'PM25_Urban_ugm3', 'PM25_Rural_ugm3'] 
                   if c in merged_df.columns]
        if pm_cols and 'U5MR_per_1000' in merged_df.columns:
            corr_cols = pm_cols + ['U5MR_per_1000']
            corr_matrix = merged_df[corr_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                aspect='auto',
                color_continuous_scale='RdBu_r',
                zmin=-1, zmax=1,
                title='Correlation Matrix: PM2.5 vs U5MR'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # PAGE 2: DATA EXPLORER
    # ========================================================================
    
    elif page == "Data Explorer":
        st.header("🔍 Interactive Data Explorer")
        
        # Filters
        st.sidebar.subheader("Filters")
        
        if 'Year' in merged_df.columns:
            years = sorted(merged_df['Year'].unique())
            selected_years = st.sidebar.multiselect(
                "Select Years",
                years,
                default=years
            )
            filtered_df = merged_df[merged_df['Year'].isin(selected_years)]
        else:
            filtered_df = merged_df
        
        # Show data
        st.subheader("📋 Dataset Preview")
        st.dataframe(filtered_df.head(100), use_container_width=True)
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
        st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)
        
        # Download data
        st.subheader("💾 Download Data")
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv"
        )
        
        # Scatter plot explorer
        st.subheader("📈 Custom Scatter Plot")
        col1, col2 = st.columns(2)
        
        numeric_cols_for_plot = [c for c in numeric_cols if c in filtered_df.columns]
        
        with col1:
            x_col = st.selectbox("X-axis", numeric_cols_for_plot, 
                                index=numeric_cols_for_plot.index('PM25_Total_ugm3') 
                                if 'PM25_Total_ugm3' in numeric_cols_for_plot else 0)
        
        with col2:
            y_col = st.selectbox("Y-axis", numeric_cols_for_plot,
                                index=numeric_cols_for_plot.index('U5MR_per_1000')
                                if 'U5MR_per_1000' in numeric_cols_for_plot else 1)
        
        fig = px.scatter(
            filtered_df,
            x=x_col,
            y=y_col,
            color='Year' if 'Year' in filtered_df.columns else None,
            hover_name='Country_ISO3' if 'Country_ISO3' in filtered_df.columns else None,
            trendline='ols',
            title=f'{x_col} vs {y_col}'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # PAGE 3: GEOGRAPHIC MAPS
    # ========================================================================
    
    elif page == "Geographic Maps":
        st.header("🗺️ Interactive Geographic Visualizations")
        
        map_type = st.selectbox(
            "Select Map Type",
            ["PM2.5 Choropleth", "U5MR Choropleth", "Animated PM2.5", "Bubble Map"]
        )
        
        if map_type == "PM2.5 Choropleth":
            st.subheader("Global PM2.5 Levels")
            if 'PM25_Total_ugm3' in merged_df.columns:
                fig = geographic_viz.create_choropleth_map(
                    merged_df, 'PM25_Total_ugm3',
                    'Average PM2.5 Concentration by Country',
                    color_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif map_type == "U5MR Choropleth":
            st.subheader("Global Under-5 Mortality Rates")
            if 'U5MR_per_1000' in merged_df.columns:
                fig = geographic_viz.create_choropleth_map(
                    merged_df, 'U5MR_per_1000',
                    'Average U5MR by Country',
                    color_scale='OrRd'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif map_type == "Animated PM2.5":
            st.subheader("PM2.5 Levels Over Time")
            if 'PM25_Total_ugm3' in merged_df.columns and 'Year' in merged_df.columns:
                df_clean = merged_df.dropna(subset=['Country_ISO3', 'Year', 'PM25_Total_ugm3'])
                fig = geographic_viz.create_animated_choropleth(
                    df_clean, 'PM25_Total_ugm3',
                    'PM2.5 Levels Over Time',
                    color_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif map_type == "Bubble Map":
            st.subheader("PM2.5 vs U5MR (Bubble Map)")
            if 'PM25_Total_ugm3' in merged_df.columns and 'U5MR_per_1000' in merged_df.columns:
                fig = geographic_viz.create_bubble_map(
                    merged_df, 'PM25_Total_ugm3', 'U5MR_per_1000', 'U5MR_per_1000',
                    'PM2.5 vs Under-5 Mortality'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # PAGE 4: STATISTICAL ANALYSIS
    # ========================================================================
    
    elif page == "Statistical Analysis":
        st.header("📊 Statistical Analysis")
        
        # Correlation analysis
        st.subheader("🔗 Correlation Analysis")
        pm_cols = [c for c in ['PM25_Total_ugm3', 'PM25_Urban_ugm3', 'PM25_Rural_ugm3'] 
                   if c in merged_df.columns]
        
        if pm_cols and 'U5MR_per_1000' in merged_df.columns:
            for pm_col in pm_cols:
                corr = merged_df[[pm_col, 'U5MR_per_1000']].corr().iloc[0, 1]
                st.metric(
                    f"Correlation: {pm_col} ↔ U5MR",
                    f"r = {corr:.3f}",
                    help="Pearson correlation coefficient"
                )
        
        # Distribution plots
        st.subheader("📈 Variable Distributions")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'PM25_Total_ugm3' in merged_df.columns:
                fig = px.histogram(
                    merged_df,
                    x='PM25_Total_ugm3',
                    nbins=50,
                    title='Distribution of PM2.5',
                    labels={'PM25_Total_ugm3': 'PM2.5 (µg/m³)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'U5MR_per_1000' in merged_df.columns:
                fig = px.histogram(
                    merged_df,
                    x='U5MR_per_1000',
                    nbins=50,
                    title='Distribution of U5MR',
                    labels={'U5MR_per_1000': 'U5MR (per 1,000)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Regression plot
        st.subheader("📉 Regression Analysis")
        if 'PM25_Total_ugm3' in merged_df.columns and 'U5MR_per_1000' in merged_df.columns:
            fig = px.scatter(
                merged_df,
                x='PM25_Total_ugm3',
                y='U5MR_per_1000',
                trendline='ols',
                title='PM2.5 vs Under-5 Mortality (with OLS regression line)',
                labels={
                    'PM25_Total_ugm3': 'PM2.5 (µg/m³)',
                    'U5MR_per_1000': 'U5MR (per 1,000)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show regression coefficients
            from scipy import stats
            X = merged_df['PM25_Total_ugm3'].dropna()
            y = merged_df.loc[X.index, 'U5MR_per_1000']
            slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
            
            st.markdown(f"""
            **Regression Equation:** U5MR = {intercept:.2f} + {slope:.4f} × PM2.5
            
            - **Slope**: {slope:.4f} (SE: {std_err:.4f})
            - **Intercept**: {intercept:.2f}
            - **R-squared**: {r_value**2:.4f}
            - **P-value**: {p_value:.2e}
            """)
    
    # ========================================================================
    # PAGE 5: MACHINE LEARNING
    # ========================================================================
    
    elif page == "Machine Learning":
        st.header("🤖 Machine Learning Models")
        
        # Load model results
        model_results_path = os.path.join(config.TABLES_DIR, 'model_results_pm25_only.csv')
        if os.path.exists(model_results_path):
            model_results = pd.read_csv(model_results_path)
            
            st.subheader("📊 Model Performance Comparison")
            
            # Bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(name='R²', x=model_results['Model'], y=model_results['R2']))
            fig.add_trace(go.Bar(name='MAE', x=model_results['Model'], 
                                y=model_results['MAE']/100))  # Scale for visibility
            fig.update_layout(title='Model Performance Metrics', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed results table
            st.subheader("📋 Detailed Results")
            st.dataframe(model_results, use_container_width=True)
            
            # Feature importance (if available)
            st.subheader("⭐ Feature Importance")
            best_model_name = model_results.iloc[0]['Model']
            feat_imp_path = os.path.join(config.FIGURES_DIR, 
                                        f'feature_importance_{best_model_name}_pm25_only.png')
            if os.path.exists(feat_imp_path):
                st.image(feat_imp_path, caption=f'{best_model_name} Feature Importance')
            
            # Predictions vs actual
            st.subheader("🎯 Predictions vs Actual Values")
            pred_path = os.path.join(config.FIGURES_DIR, 
                                    f'predictions_{best_model_name}_pm25_only.png')
            if os.path.exists(pred_path):
                st.image(pred_path, caption=f'{best_model_name} Predictions')
        else:
            st.warning("⚠️ Model results not found. Please run main_complete.py first.")
    
    # ========================================================================
    # PAGE 6: CAUSAL INFERENCE
    # ========================================================================
    
    elif page == "Causal Inference":
        st.header("🔬 Causal Inference Analysis")
        
        st.markdown("""
        This section explores **causal relationships** between air pollution and child mortality
        using advanced statistical methods.
        """)
        
        st.subheader("📚 Methods Available")
        st.markdown("""
        1. **Propensity Score Matching (PSM)**: Matches treated and control units with similar characteristics
        2. **Difference-in-Differences (DiD)**: Compares changes over time between groups
        3. **Instrumental Variables (IV)**: Uses exogenous variables to estimate causal effects
        """)
        
        # Check if extended data is available
        if extended_data is not None and 'gdp_pc' in extended_data.columns:
            st.subheader("⚙️ Run Causal Analysis")
            
            if st.button("Run Propensity Score Matching"):
                with st.spinner("Running PSM analysis..."):
                    from src import causal_inference
                    
                    # Create treatment variable
                    extended_data['high_pollution'] = (
                        extended_data['PM25_Total_ugm3'] > 
                        extended_data['PM25_Total_ugm3'].median()
                    ).astype(int)
                    
                    confounders = ['gdp_pc', 'urban_pct']
                    results = causal_inference.propensity_score_matching(
                        extended_data, 'high_pollution', 'U5MR_per_1000',
                        confounders, verbose=False
                    )
                    
                    if results:
                        st.success("✅ PSM Analysis Complete!")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Matched Pairs", results['n_matched'])
                        with col2:
                            st.metric("Average Treatment Effect", f"{results['ate']:.2f}")
                        with col3:
                            st.metric("Matching Rate", f"{results['matching_rate']*100:.1f}%")
        else:
            st.info("ℹ️ Extended dataset with confounders needed. Run main_complete.py to download.")
    
    # ========================================================================
    # PAGE 7: ABOUT
    # ========================================================================
    
    elif page == "About":
        st.header("ℹ️ About This Project")
        
        st.markdown("""
        ## Air Pollution & Under-5 Mortality Analysis
        
        This interactive dashboard presents a comprehensive analysis of the relationship 
        between PM2.5 air pollution and under-5 mortality rates across 195 countries.
        
        ### 📊 Data Sources
        - **WHO**: PM2.5 air pollution data (2010-2019)
        - **UNICEF**: Under-5 mortality rates (1990-2023)
        - **World Bank**: GDP, health expenditure, urbanization, fertility
        
        ### 🔬 Methods
        - **Statistical Analysis**: Correlation, regression, hypothesis testing
        - **Machine Learning**: Ridge, Lasso, Random Forest, XGBoost, etc.
        - **Causal Inference**: PSM, DiD, IV methods
        - **Geographic Visualization**: Interactive choropleth maps
        
        ### 🎯 Key Findings
        - PM2.5 explains 10.9% of U5MR variance (linear model)
        - Random Forest achieves R² = 0.437 (43.7% explained)
        - Each 1 µg/m³ increase in PM2.5 → +0.85 U5MR
        - Urban areas have 14% higher PM2.5 than rural areas
        
        ### 👨‍💻 Technical Stack
        - **Language**: Python 3.10+
        - **ML**: scikit-learn, XGBoost
        - **Visualization**: Plotly, Matplotlib, Seaborn
        - **Dashboard**: Streamlit
        - **Stats**: statsmodels, scipy
        
        ### 📁 Project Structure
        ```
        Project/
        ├── config.py                    # Configuration
        ├── streamlit_dashboard.py       # This dashboard
        ├── src/                         # Source modules
        ├── data/                        # Data files
        ├── reports/                     # Outputs
        └── models/                      # Trained models
        ```
        
        ### 📚 Documentation
        - **README.md**: Complete project documentation
        - **PROJECT_REPORT.md**: Academic-style report
        - **QUICK_START.md**: Quick setup guide
        
        ---
        
        **Last Updated**: December 8, 2025  
        **Version**: 2.0 (With Dashboard)
        """)


if __name__ == "__main__":
    main()

