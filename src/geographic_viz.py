"""
Geographic Visualization Module
Create interactive maps and geographic heatmaps
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from typing import Optional
import config


def create_choropleth_map(df: pd.DataFrame,
                         value_column: str,
                         title: str,
                         color_scale: str = 'Reds',
                         save_path: Optional[str] = None) -> go.Figure:
    """
    Create interactive choropleth map using Plotly.
    
    Args:
        df: DataFrame with Country_ISO3 and value column
        value_column: Column name for map colors
        title: Map title
        color_scale: Plotly color scale
        save_path: Path to save HTML file
        
    Returns:
        Plotly figure object
    """
    # Aggregate by country (mean across years)
    df_agg = df.groupby('Country_ISO3')[value_column].mean().reset_index()
    
    fig = px.choropleth(
        df_agg,
        locations='Country_ISO3',
        color=value_column,
        hover_name='Country_ISO3',
        color_continuous_scale=color_scale,
        title=title,
        labels={value_column: value_column.replace('_', ' ')}
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=600,
        width=1000
    )
    
    if save_path:
        fig.write_html(save_path)
        print(f"[SAVED] {save_path}")
    
    return fig


def create_bubble_map(df: pd.DataFrame,
                     x_column: str,
                     y_column: str,
                     size_column: str,
                     title: str,
                     save_path: Optional[str] = None) -> go.Figure:
    """
    Create bubble map showing relationships between variables.
    
    Args:
        df: DataFrame with geographic data
        x_column: X-axis variable
        y_column: Y-axis variable
        size_column: Variable for bubble size
        title: Plot title
        save_path: Path to save HTML file
        
    Returns:
        Plotly figure object
    """
    # Get latest year data
    df_latest = df[df['Year'] == df['Year'].max()].copy()
    
    fig = px.scatter_geo(
        df_latest,
        locations='Country_ISO3',
        color=y_column,
        size=size_column,
        hover_name='Country_ISO3' if 'Country_ISO3' in df_latest.columns else None,
        hover_data=[x_column, y_column, size_column],
        projection='natural earth',
        title=title,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=600, width=1000)
    
    if save_path:
        fig.write_html(save_path)
        print(f"[SAVED] {save_path}")
    
    return fig


def create_animated_choropleth(df: pd.DataFrame,
                               value_column: str,
                               title: str,
                               color_scale: str = 'Reds',
                               save_path: Optional[str] = None) -> go.Figure:
    """
    Create animated choropleth map over time.
    
    Args:
        df: DataFrame with Country_ISO3, Year, and value column
        value_column: Column name for map colors
        title: Map title
        color_scale: Plotly color scale
        save_path: Path to save HTML file
        
    Returns:
        Plotly figure object
    """
    fig = px.choropleth(
        df,
        locations='Country_ISO3',
        color=value_column,
        hover_name='Country_ISO3',
        animation_frame='Year',
        color_continuous_scale=color_scale,
        title=title,
        labels={value_column: value_column.replace('_', ' ')},
        range_color=[df[value_column].quantile(0.05), 
                    df[value_column].quantile(0.95)]
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=600,
        width=1000
    )
    
    if save_path:
        fig.write_html(save_path)
        print(f"[SAVED] {save_path}")
    
    return fig


def create_regional_comparison(df: pd.DataFrame,
                               value_column: str,
                               title: str,
                               save_path: Optional[str] = None) -> go.Figure:
    """
    Create regional comparison bar chart.
    
    Args:
        df: DataFrame with regional data
        value_column: Column to compare
        title: Plot title
        save_path: Path to save HTML file
        
    Returns:
        Plotly figure object
    """
    # Map ISO3 codes to regions (simplified mapping)
    region_mapping = {
        'AFG': 'South Asia', 'BGD': 'South Asia', 'BTN': 'South Asia', 
        'IND': 'South Asia', 'PAK': 'South Asia', 'NPL': 'South Asia',
        'CHN': 'East Asia', 'JPN': 'East Asia', 'KOR': 'East Asia',
        'USA': 'North America', 'CAN': 'North America', 'MEX': 'North America',
        'BRA': 'South America', 'ARG': 'South America', 'CHL': 'South America',
        'GBR': 'Europe', 'FRA': 'Europe', 'DEU': 'Europe', 'ITA': 'Europe',
        'NGA': 'Africa', 'ETH': 'Africa', 'EGY': 'Africa', 'ZAF': 'Africa'
    }
    
    df['Region'] = df['Country_ISO3'].map(region_mapping).fillna('Other')
    
    # Group by region
    regional_data = df.groupby('Region')[value_column].mean().reset_index()
    regional_data = regional_data.sort_values(value_column, ascending=False)
    
    fig = px.bar(
        regional_data,
        x='Region',
        y=value_column,
        title=title,
        labels={value_column: value_column.replace('_', ' ')},
        color=value_column,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(height=500, width=800, xaxis_tickangle=-45)
    
    if save_path:
        fig.write_html(save_path)
        print(f"[SAVED] {save_path}")
    
    return fig


def generate_all_geographic_visualizations(df: pd.DataFrame, verbose: bool = True):
    """
    Generate all geographic visualizations.
    
    Args:
        df: Merged dataset with PM2.5 and U5MR
        verbose: Print progress
    """
    if verbose:
        print("\n[GEO] Creating geographic visualizations")
    
    figures_dir = config.FIGURES_DIR
    
    # 1. PM2.5 Choropleth
    if 'PM25_Total_ugm3' in df.columns:
        create_choropleth_map(
            df, 'PM25_Total_ugm3',
            'Global PM2.5 Levels (Average)',
            color_scale='Reds',
            save_path=os.path.join(figures_dir, 'map_pm25.html')
        )
    
    # 2. U5MR Choropleth
    if 'U5MR_per_1000' in df.columns:
        create_choropleth_map(
            df, 'U5MR_per_1000',
            'Global Under-5 Mortality Rate (Average)',
            color_scale='OrRd',
            save_path=os.path.join(figures_dir, 'map_u5mr.html')
        )
    
    # 3. Animated PM2.5 over time
    if 'PM25_Total_ugm3' in df.columns and 'Year' in df.columns:
        df_clean = df.dropna(subset=['Country_ISO3', 'Year', 'PM25_Total_ugm3'])
        if len(df_clean) > 0:
            create_animated_choropleth(
                df_clean, 'PM25_Total_ugm3',
                'PM2.5 Levels Over Time',
                color_scale='Reds',
                save_path=os.path.join(figures_dir, 'map_pm25_animated.html')
            )
    
    # 4. Bubble map: PM2.5 vs U5MR
    if 'PM25_Total_ugm3' in df.columns and 'U5MR_per_1000' in df.columns:
        create_bubble_map(
            df, 'PM25_Total_ugm3', 'U5MR_per_1000', 'U5MR_per_1000',
            'PM2.5 vs Under-5 Mortality (Latest Year)',
            save_path=os.path.join(figures_dir, 'map_bubble_pm25_u5mr.html')
        )
    
    # 5. Regional comparison
    if 'PM25_Total_ugm3' in df.columns:
        create_regional_comparison(
            df, 'PM25_Total_ugm3',
            'PM2.5 Levels by Region',
            save_path=os.path.join(figures_dir, 'map_regional_pm25.html')
        )
    
    if verbose:
        print("[DONE] Geographic visualizations complete")
        print(f"  Created 5 interactive HTML maps in {figures_dir}")

