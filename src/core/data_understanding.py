import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

class DataUnderstanding:
    def __init__(self):
        self.df = None
        self.schema = {}
        self.column_relationships = {}
        self.data_quality_metrics = {}
        
    def analyze_data(self, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive data analysis to understand the structure and content
        """
        self.df = df
        self._infer_schema()
        self._analyze_relationships()
        self._calculate_quality_metrics()
        return self._get_analysis_summary()
    
    def _infer_schema(self):
        """Infer detailed schema information for each column"""
        for col in self.df.columns:
            col_info = {
                'type': self._infer_column_type(col),
                'unique_values': self.df[col].nunique(),
                'null_count': self.df[col].isnull().sum(),
                'null_percentage': (self.df[col].isnull().sum() / len(self.df)) * 100,
                'sample_values': self._get_sample_values(col),
                'statistics': self._calculate_column_statistics(col)
            }
            self.schema[col] = col_info
    
    def _infer_column_type(self, column: str) -> str:
        """Infer the semantic type of a column"""
        # Get non-null sample
        sample = self.df[column].dropna().head(100)
        if len(sample) == 0:
            return 'unknown'
            
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(sample):
            return 'datetime'
            
        # Check for numeric
        if pd.api.types.is_numeric_dtype(sample):
            # Check if it's a binary/categorical numeric
            if sample.nunique() <= 2:
                return 'binary'
            elif sample.nunique() < len(sample) * 0.5:
                return 'categorical_numeric'
            return 'numeric'
            
        # Check for categorical
        if sample.nunique() < len(sample) * 0.5:
            return 'categorical'
            
        # Check for text
        if pd.api.types.is_string_dtype(sample):
            # Check if it's a date string
            if self._is_date_string(sample):
                return 'date_string'
            return 'text'
            
        return 'unknown'
    
    def _is_date_string(self, sample: pd.Series) -> bool:
        """Check if a string column contains dates"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{2}\.\d{2}\.\d{4}'
        ]
        
        sample_str = sample.astype(str)
        for pattern in date_patterns:
            if sample_str.str.match(pattern).mean() > 0.5:
                return True
        return False
    
    def _get_sample_values(self, column: str, n: int = 5) -> List:
        """Get sample values from a column"""
        return self.df[column].dropna().head(n).tolist()
    
    def _calculate_column_statistics(self, column: str) -> Dict:
        """Calculate detailed statistics for a column"""
        stats = {}
        col_type = self.schema[column]['type']
        
        if col_type in ['numeric', 'categorical_numeric']:
            stats.update({
                'mean': self.df[column].mean(),
                'median': self.df[column].median(),
                'std': self.df[column].std(),
                'min': self.df[column].min(),
                'max': self.df[column].max(),
                'q1': self.df[column].quantile(0.25),
                'q3': self.df[column].quantile(0.75)
            })
        elif col_type == 'categorical':
            stats['value_counts'] = self.df[column].value_counts().head(10).to_dict()
            stats['most_common'] = self.df[column].mode().iloc[0]
            stats['least_common'] = self.df[column].value_counts().index[-1]
            
        return stats
    
    def _analyze_relationships(self):
        """Analyze relationships between columns"""
        numeric_cols = [col for col, info in self.schema.items() 
                       if info['type'] in ['numeric', 'categorical_numeric']]
        
        if len(numeric_cols) >= 2:
            corr_matrix = self.df[numeric_cols].corr()
            for col1 in numeric_cols:
                for col2 in numeric_cols:
                    if col1 != col2:
                        key = f"{col1}_{col2}"
                        self.column_relationships[key] = {
                            'correlation': corr_matrix.loc[col1, col2],
                            'type': 'numeric_correlation'
                        }
    
    def _calculate_quality_metrics(self):
        """Calculate data quality metrics"""
        self.data_quality_metrics = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'null_percentage': (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100,
            'duplicate_rows': self.df.duplicated().sum(),
            'column_types': {col: info['type'] for col, info in self.schema.items()}
        }
    
    def _get_analysis_summary(self) -> Dict:
        """Get a summary of the data analysis"""
        return {
            'schema': self.schema,
            'relationships': self.column_relationships,
            'quality_metrics': self.data_quality_metrics
        }
    
    def get_column_suggestions(self) -> Dict[str, List[str]]:
        """Get suggestions for columns based on their types"""
        suggestions = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'text': [],
            'binary': []
        }
        
        for col, info in self.schema.items():
            col_type = info['type']
            if col_type in suggestions:
                suggestions[col_type].append(col)
            elif col_type == 'categorical_numeric':
                suggestions['numeric'].append(col)
                
        return suggestions
    
    def get_visualization_suggestions(self) -> List[Dict]:
        """Get suggestions for visualizations based on data analysis"""
        suggestions = []
        
        # Time series suggestions
        datetime_cols = [col for col, info in self.schema.items() 
                        if info['type'] in ['datetime', 'date_string']]
        if datetime_cols:
            numeric_cols = [col for col, info in self.schema.items() 
                           if info['type'] in ['numeric', 'categorical_numeric']]
            for num_col in numeric_cols:
                suggestions.append({
                    'type': 'line',
                    'title': f"{num_col} Over Time",
                    'x': datetime_cols[0],
                    'y': num_col
                })
        
        # Distribution suggestions
        numeric_cols = [col for col, info in self.schema.items() 
                       if info['type'] in ['numeric', 'categorical_numeric']]
        for num_col in numeric_cols:
            suggestions.append({
                'type': 'histogram',
                'title': f"Distribution of {num_col}",
                'x': num_col
            })
        
        # Categorical suggestions
        categorical_cols = [col for col, info in self.schema.items() 
                           if info['type'] == 'categorical']
        if categorical_cols and numeric_cols:
            for cat_col in categorical_cols:
                for num_col in numeric_cols:
                    suggestions.append({
                        'type': 'bar',
                        'title': f"{num_col} by {cat_col}",
                        'x': cat_col,
                        'y': num_col
                    })
        
        return suggestions 