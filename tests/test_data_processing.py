"""Unit tests for data_processing module"""

import pytest
import pandas as pd
import numpy as np
from src import data_processing


class TestColumnPicking:
    """Test column detection functions"""
    
    def test_pick_column_finds_first_match(self):
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        result = data_processing.pick_column(['B', 'A', 'C'], df)
        assert result == 'B'
    
    def test_pick_column_returns_none_when_not_found(self):
        df = pd.DataFrame({'A': [1, 2]})
        result = data_processing.pick_column(['X', 'Y', 'Z'], df)
        assert result is None


class TestResidenceCategorization:
    """Test residence type categorization"""
    
    def test_categorize_urban(self):
        assert data_processing.categorize_residence('Urban') == 'Urban'
        assert data_processing.categorize_residence('urban area') == 'Urban'
    
    def test_categorize_rural(self):
        assert data_processing.categorize_residence('Rural') == 'Rural'
        assert data_processing.categorize_residence('rural region') == 'Rural'
    
    def test_categorize_total(self):
        assert data_processing.categorize_residence('Total') == 'Total'
        assert data_processing.categorize_residence('National') == 'Total'
        assert data_processing.categorize_residence('Both sexes') == 'Total'
    
    def test_categorize_unknown(self):
        assert data_processing.categorize_residence('Unknown') is None
        assert data_processing.categorize_residence('') is None


class TestISO3Codes:
    """Test ISO3 code addition"""
    
    def test_add_iso3_codes_preserves_existing(self):
        df = pd.DataFrame({
            'Country': ['USA', 'France'],
            'SpatialDimValueCode': ['USA', 'FRA']
        })
        result = data_processing.add_iso3_codes(df, verbose=False)
        assert result['Country_ISO3'].tolist() == ['USA', 'FRA']
    
    def test_add_iso3_codes_creates_column(self):
        df = pd.DataFrame({'Country': ['Afghanistan', 'Albania']})
        result = data_processing.add_iso3_codes(df, verbose=False)
        assert 'Country_ISO3' in result.columns


class TestDataMerging:
    """Test data merging functions"""
    
    def test_merge_pm25_u5mr_inner_join(self):
        who_df = pd.DataFrame({
            'Country_ISO3': ['USA', 'FRA'],
            'Year': [2015, 2015],
            'PM25_Total_ugm3': [10.5, 12.3]
        })
        u5mr_df = pd.DataFrame({
            'Country_ISO3': ['USA', 'DEU'],
            'Year': [2015, 2015],
            'U5MR_per_1000': [6.5, 3.8],
            'Country': ['United States', 'Germany']
        })
        
        result = data_processing.merge_pm25_u5mr(who_df, u5mr_df, verbose=False)
        
        # Should only keep USA (inner join)
        assert len(result) == 1
        assert result['Country_ISO3'].iloc[0] == 'USA'
        assert 'PM25_Total_ugm3' in result.columns
        assert 'U5MR_per_1000' in result.columns

