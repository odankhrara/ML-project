"""
Visualization Module
Functions for creating plots and charts for PM2.5 and U5MR analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List
import config
import os


def plot_correlation_matrix(df: pd.DataFrame, 
                            columns: List[str],
                            title: str = "Correlation Matrix",
                            save_path: Optional[str] = None,
                            show: bool = False) -> None:
    """
    Plot correlation heatmap for specified columns.
    
    Args:
        df: DataFrame containing the columns
        columns: List of column names to include
        title: Plot title
        save_path: Path to save figure (if None, uses default)
        show: Whether to display plot
    """
    corr = df[columns].corr()
    
    plt.figure(figsize=config.FIGURE_SIZE_STANDARD)
    sns.heatmap(corr, annot=True, cmap=config.CORRELATION_CMAP, 
                fmt=".2f", center=0, cbar_kws={'label': 'Correlation'})
    plt.title(title)
    plt.tight_layout()
    
    if save_path is None:
        save_path = os.path.join(config.FIGURES_DIR, '01_correlation_matrix.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_scatter_with_regression(df: pd.DataFrame,
                                 x_col: str,
                                 y_col: str,
                                 title: str = None,
                                 xlabel: str = None,
                                 ylabel: str = None,
                                 save_path: Optional[str] = None,
                                 show: bool = False) -> None:
    """
    Create scatter plot with regression line.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        save_path: Path to save figure
        show: Whether to display plot
    """
    plt.figure(figsize=config.FIGURE_SIZE_STANDARD)
    sns.regplot(data=df, x=x_col, y=y_col,
                scatter_kws={"alpha": 0.4},
                line_kws={"color": "red"})
    
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path is None:
        save_path = os.path.join(config.FIGURES_DIR, f'scatter_{x_col}_vs_{y_col}.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_urban_vs_rural(df: pd.DataFrame,
                       save_path: Optional[str] = None,
                       show: bool = False) -> None:
    """
    Plot Urban vs Rural PM2.5 concentrations.
    
    Args:
        df: DataFrame with PM25_Rural_ugm3 and PM25_Urban_ugm3 columns
        save_path: Path to save figure
        show: Whether to display plot
    """
    if 'PM25_Rural_ugm3' not in df.columns or 'PM25_Urban_ugm3' not in df.columns:
        print("[WARNING] Rural/Urban PM2.5 columns not found, skipping plot")
        return
    
    plt.figure(figsize=config.FIGURE_SIZE_SQUARE)
    sns.scatterplot(data=df, x='PM25_Rural_ugm3', y='PM25_Urban_ugm3', alpha=0.5)
    
    max_val = max(df['PM25_Rural_ugm3'].max(), df['PM25_Urban_ugm3'].max())
    plt.plot([0, max_val], [0, max_val], 'r--', label='y=x')
    
    plt.xlabel('Rural PM2.5 (ug/m3)')
    plt.ylabel('Urban PM2.5 (ug/m3)')
    plt.title('Urban vs Rural PM2.5 Concentration')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path is None:
        save_path = os.path.join(config.FIGURES_DIR, '03_urban_vs_rural_pm25.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_top_countries(df: pd.DataFrame,
                      column: str,
                      country_col: str,
                      n: int = 10,
                      title: str = None,
                      ylabel: str = None,
                      ascending: bool = False,
                      save_path: Optional[str] = None,
                      show: bool = False) -> None:
    """
    Plot top N countries by a given metric.
    
    Args:
        df: DataFrame
        column: Column to aggregate and sort by
        country_col: Column containing country names
        n: Number of top countries to show
        title: Plot title
        ylabel: Y-axis label
        ascending: Sort order (False for descending)
        save_path: Path to save figure
        show: Whether to display plot
    """
    avg_values = (df.groupby(country_col)[column]
                  .mean()
                  .sort_values(ascending=ascending)
                  .head(n))
    
    plt.figure(figsize=config.FIGURE_SIZE_STANDARD)
    avg_values.plot(kind='bar', color='salmon')
    
    if title:
        plt.title(title)
    if ylabel:
        plt.ylabel(ylabel)
    
    plt.xlabel("Country")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path is None:
        save_path = os.path.join(config.FIGURES_DIR, f'top{n}_countries_{column}.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_time_series_dual_axis(df: pd.DataFrame,
                               country: str,
                               country_col: str,
                               y1_col: str,
                               y2_col: str,
                               y1_label: str,
                               y2_label: str,
                               title: str = None,
                               save_path: Optional[str] = None,
                               show: bool = False) -> None:
    """
    Plot time series with dual y-axes for a specific country.
    
    Args:
        df: DataFrame
        country: Country name to plot
        country_col: Column containing country names
        y1_col: First y-axis column
        y2_col: Second y-axis column
        y1_label: Label for first y-axis
        y2_label: Label for second y-axis
        title: Plot title
        save_path: Path to save figure
        show: Whether to display plot
    """
    sub = df[df[country_col] == country].sort_values('Year')
    
    if len(sub) == 0:
        print(f"[WARNING] No data for country: {country}")
        return
    
    fig, ax1 = plt.subplots(figsize=config.FIGURE_SIZE_STANDARD)
    
    # First axis
    ax1.plot(sub["Year"], sub[y1_col], "b-o", label=y1_label)
    ax1.set_xlabel("Year")
    ax1.set_ylabel(y1_label, color="b")
    ax1.tick_params(axis='y', labelcolor='b')
    
    # Second axis
    ax2 = ax1.twinx()
    ax2.plot(sub["Year"], sub[y2_col], "r--s", label=y2_label)
    ax2.set_ylabel(y2_label, color="r")
    ax2.tick_params(axis='y', labelcolor='r')
    
    if title:
        plt.title(title)
    else:
        plt.title(f"{country}: {y1_label} and {y2_label} Over Time")
    
    fig.tight_layout()
    
    if save_path is None:
        safe_country = country.replace(' ', '_').replace('/', '_')
        save_path = os.path.join(config.FIGURES_DIR, f'timeseries_{safe_country}.png')
    plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
    print(f"[SAVED] {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def create_exploratory_plots(merged_df: pd.DataFrame, 
                            show: bool = False) -> None:
    """
    Create all standard exploratory data analysis plots.
    
    Args:
        merged_df: Merged PM2.5 and U5MR DataFrame
        show: Whether to display plots
    """
    print("[PLOT] Creating exploratory visualizations")
    
    # Correlation matrix
    pm_cols = [c for c in config.PM25_FEATURES if c in merged_df.columns]
    if pm_cols and config.TARGET in merged_df.columns:
        plot_correlation_matrix(
            merged_df,
            pm_cols + [config.TARGET],
            title="Correlation Matrix: PM2.5 vs Under-5 Mortality",
            save_path=os.path.join(config.FIGURES_DIR, '01_correlation_matrix.png'),
            show=show
        )
    
    # PM2.5 Total vs U5MR scatter
    if 'PM25_Total_ugm3' in merged_df.columns and config.TARGET in merged_df.columns:
        plot_scatter_with_regression(
            merged_df,
            'PM25_Total_ugm3',
            config.TARGET,
            title="PM2.5 (Total) vs Under-5 Mortality Rate",
            xlabel="PM2.5 (ug/m3)",
            ylabel="Under-5 Mortality (per 1,000)",
            save_path=os.path.join(config.FIGURES_DIR, '02_pm25_vs_u5mr_scatter.png'),
            show=show
        )
    
    # Urban vs Rural PM2.5
    plot_urban_vs_rural(merged_df, show=show)
    
    # Top 10 countries by PM2.5
    if 'PM25_Total_ugm3' in merged_df.columns:
        country_col = 'Country_WHO' if 'Country_WHO' in merged_df.columns else 'Country_ISO3'
        plot_top_countries(
            merged_df,
            'PM25_Total_ugm3',
            country_col,
            n=10,
            title="Top 10 Countries by Average PM2.5 (Total)",
            ylabel="PM2.5 (ug/m3)",
            save_path=os.path.join(config.FIGURES_DIR, '04_top10_countries_pm25.png'),
            show=show
        )
    
    # Time series for sample country
    if 'PM25_Total_ugm3' in merged_df.columns and config.TARGET in merged_df.columns:
        country_col = 'Country_WHO' if 'Country_WHO' in merged_df.columns else 'Country_ISO3'
        sample_countries = merged_df[country_col].value_counts().head(5).index.tolist()
        
        if sample_countries:
            country = sample_countries[0]
            plot_time_series_dual_axis(
                merged_df,
                country,
                country_col,
                'PM25_Total_ugm3',
                config.TARGET,
                "PM2.5 Total",
                "U5MR (per 1,000)",
                save_path=os.path.join(config.FIGURES_DIR, f'05_timeseries_{country}.png'),
                show=show
            )
    
    print("[DONE] Exploratory plots complete")

