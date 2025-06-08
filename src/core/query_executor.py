import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from .query_understanding import QueryIntent, QueryType
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

class QueryExecutor:
    def __init__(self):
        self.aggregation_functions = {
            'mean': np.mean,
            'sum': np.sum,
            'count': len,
            'min': np.min,
            'max': np.max,
            'median': np.median
        }
        
    def execute_query(self, df: pd.DataFrame, intent: QueryIntent) -> Dict:
        """
        Execute the query based on the understood intent
        """
        try:
            if intent.type == QueryType.STATISTICAL:
                return self._execute_statistical_query(df, intent)
            elif intent.type == QueryType.FILTER:
                return self._execute_filter_query(df, intent)
            elif intent.type == QueryType.COMPARISON:
                return self._execute_comparison_query(df, intent)
            elif intent.type == QueryType.VISUALIZATION:
                return self._execute_visualization_query(df, intent)
            else:
                return {
                    'error': 'Unknown query type',
                    'message': 'Could not understand the type of query'
                }
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error executing query'
            }
    
    def _execute_statistical_query(self, df: pd.DataFrame, intent: QueryIntent) -> Dict:
        """Execute statistical query"""
        if not intent.columns:
            return {
                'error': 'No columns specified',
                'message': 'Please specify which column to analyze'
            }
            
        if not intent.aggregation:
            # Default to max if no aggregation specified
            intent.aggregation = 'max'
            
        column = intent.columns[0]
        if column not in df.columns:
            return {
                'error': 'Column not found',
                'message': f'Column {column} does not exist in the data'
            }
            
        # Apply aggregation
        result = self.aggregation_functions[intent.aggregation](df[column])
        
        return {
            'type': 'statistical',
            'column': column,
            'aggregation': intent.aggregation,
            'result': result,
            'message': f'The {intent.aggregation} of {column} is {result:.2f}'
        }
    
    def _execute_filter_query(self, df: pd.DataFrame, intent: QueryIntent) -> Dict:
        """Execute filter query"""
        if not intent.columns or not intent.conditions:
            return {
                'error': 'Invalid filter',
                'message': 'Please specify both column and condition'
            }
            
        # Apply filters
        filtered_df = df.copy()
        for condition in intent.conditions:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']
            
            if column not in df.columns:
                return {
                    'error': 'Column not found',
                    'message': f'Column {column} does not exist in the data'
                }
                
            # Apply filter
            if operator == '>':
                filtered_df = filtered_df[filtered_df[column] > value]
            elif operator == '<':
                filtered_df = filtered_df[filtered_df[column] < value]
            elif operator == '==':
                filtered_df = filtered_df[filtered_df[column] == value]
            elif operator == 'between':
                if isinstance(value, tuple) and len(value) == 2:
                    filtered_df = filtered_df[
                        (filtered_df[column] >= value[0]) & 
                        (filtered_df[column] <= value[1])
                    ]
        
        return {
            'type': 'filter',
            'filtered_data': filtered_df,
            'message': f'Found {len(filtered_df)} rows matching the criteria'
        }
    
    def _execute_comparison_query(self, df: pd.DataFrame, intent: QueryIntent) -> Dict:
        """Execute comparison query"""
        if not intent.columns:
            return {
                'error': 'No columns specified',
                'message': 'Please specify which columns to compare'
            }
            
        if len(intent.columns) < 2:
            return {
                'error': 'Insufficient columns',
                'message': 'Please specify at least two columns to compare'
            }
            
        # Group by if specified
        if intent.group_by:
            grouped_df = df.groupby(intent.group_by)[intent.columns].agg('mean')
            return {
                'type': 'comparison',
                'comparison_data': grouped_df,
                'message': f'Comparison of {", ".join(intent.columns)} grouped by {", ".join(intent.group_by)}'
            }
        else:
            # Simple comparison
            comparison_df = df[intent.columns].describe()
            return {
                'type': 'comparison',
                'comparison_data': comparison_df,
                'message': f'Comparison of {", ".join(intent.columns)}'
            }
    
    def _execute_visualization_query(self, df: pd.DataFrame, intent: QueryIntent) -> Dict:
        """Execute visualization query"""
        if not intent.columns:
            return {
                'error': 'No columns specified',
                'message': 'Please specify which columns to visualize'
            }
            
        if not intent.visualization_type:
            # Default to bar chart
            intent.visualization_type = 'bar'
            
        # Create visualization based on type
        if intent.visualization_type == 'bar':
            fig = px.bar(df, x=intent.columns[0], y=intent.columns[1] if len(intent.columns) > 1 else None)
        elif intent.visualization_type == 'line':
            fig = px.line(df, x=intent.columns[0], y=intent.columns[1] if len(intent.columns) > 1 else None)
        elif intent.visualization_type == 'pie':
            fig = px.pie(df, names=intent.columns[0], values=intent.columns[1] if len(intent.columns) > 1 else None)
        elif intent.visualization_type == 'scatter':
            if len(intent.columns) < 2:
                return {
                    'error': 'Insufficient columns',
                    'message': 'Scatter plot requires at least two columns'
                }
            fig = px.scatter(df, x=intent.columns[0], y=intent.columns[1])
        elif intent.visualization_type == 'histogram':
            fig = px.histogram(df, x=intent.columns[0])
        else:
            return {
                'error': 'Invalid visualization type',
                'message': f'Visualization type {intent.visualization_type} not supported'
            }
            
        return {
            'type': 'visualization',
            'visualization': fig,
            'message': f'Created {intent.visualization_type} chart for {", ".join(intent.columns)}'
        } 