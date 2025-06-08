import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import re
from dataclasses import dataclass
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

@dataclass
class QueryContext:
    """Context for the current query"""
    df: pd.DataFrame
    columns: List[str]
    column_types: Dict[str, str]
    last_query: Optional[str] = None
    last_result: Optional[Any] = None

class ChatEngine:
    def __init__(self):
        # Initialize common patterns
        self.patterns = {
            'stats': {
                'mean': r'(average|mean|avg)',
                'sum': r'(sum|total)',
                'count': r'(count|number of|how many)',
                'min': r'(minimum|lowest|smallest)',
                'max': r'(maximum|highest|largest)',
                'median': r'(median|middle)'
            },
            'filters': {
                'gt': r'(greater than|more than|above)',
                'lt': r'(less than|below)',
                'eq': r'(equal to|equals|is)',
                'between': r'(between|from|to)'
            },
            'charts': {
                'bar': r'(bar|bar chart)',
                'line': r'(line|line chart|trend)',
                'pie': r'(pie|pie chart|distribution)',
                'scatter': r'(scatter|scatter plot)',
                'histogram': r'(histogram|distribution)'
            }
        }
        
        # Initialize context
        self.context = None
        
    def load_data(self, df: pd.DataFrame) -> None:
        """Load and analyze data"""
        self.context = QueryContext(
            df=df,
            columns=df.columns.tolist(),
            column_types=self._infer_column_types(df)
        )
        
    def _infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer column types"""
        types = {}
        for col in df.columns:
            # Check for datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                types[col] = 'datetime'
            # Check for numeric
            elif pd.api.types.is_numeric_dtype(df[col]):
                if df[col].nunique() <= 2:
                    types[col] = 'binary'
                elif df[col].nunique() < len(df) * 0.5:
                    types[col] = 'categorical_numeric'
                else:
                    types[col] = 'numeric'
            # Check for categorical
            elif df[col].nunique() < len(df) * 0.5:
                types[col] = 'categorical'
            # Default to text
            else:
                types[col] = 'text'
        return types
        
    def process_query(self, query: str) -> Dict:
        """Process a natural language query"""
        if not self.context:
            return {
                'type': 'error',
                'message': 'No data loaded. Please upload a file first.'
            }
            
        try:
            # Normalize query
            query = query.lower().strip()
            
            # Extract columns mentioned in query
            columns = self._extract_columns(query)
            
            # Determine query type and process
            if self._is_statistical_query(query):
                return self._handle_statistical_query(query, columns)
            elif self._is_filter_query(query):
                return self._handle_filter_query(query, columns)
            elif self._is_chart_query(query):
                return self._handle_chart_query(query, columns)
            else:
                return {
                    'type': 'error',
                    'message': 'Could not understand query type. Please try rephrasing your question.'
                }
                
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Error processing query: {str(e)}'
            }
            
    def _extract_columns(self, query: str) -> List[str]:
        """Extract column names from query"""
        columns = []
        for col in self.context.columns:
            if col.lower() in query:
                columns.append(col)
        return columns
        
    def _is_statistical_query(self, query: str) -> bool:
        """Check if query is statistical"""
        return any(re.search(pattern, query) 
                  for patterns in self.patterns['stats'].values() 
                  for pattern in [patterns])
                  
    def _is_filter_query(self, query: str) -> bool:
        """Check if query is a filter"""
        return any(re.search(pattern, query) 
                  for patterns in self.patterns['filters'].values() 
                  for pattern in [patterns])
                  
    def _is_chart_query(self, query: str) -> bool:
        """Check if query is for a chart"""
        return any(re.search(pattern, query) 
                  for patterns in self.patterns['charts'].values() 
                  for pattern in [patterns])
                  
    def _handle_statistical_query(self, query: str, columns: List[str]) -> Dict:
        """Handle statistical queries"""
        if not columns:
            return {
                'type': 'error',
                'message': 'No columns specified in the query. Please mention a column name.'
            }
            
        # Determine aggregation function
        agg_func = None
        for func, pattern in self.patterns['stats'].items():
            if re.search(pattern, query):
                agg_func = func
                break
                
        if not agg_func:
            agg_func = 'max'  # Default to max
            
        # Apply aggregation
        column = columns[0]
        if column not in self.context.df.columns:
            return {
                'type': 'error',
                'message': f'Column "{column}" not found in the data.'
            }
            
        result = getattr(self.context.df[column], agg_func)()
        
        return {
            'type': 'statistical',
            'column': column,
            'function': agg_func,
            'result': result,
            'message': f'The {agg_func} of {column} is {result:.2f}'
        }
        
    def _handle_filter_query(self, query: str, columns: List[str]) -> Dict:
        """Handle filter queries"""
        if not columns:
            return {
                'type': 'error',
                'message': 'No columns specified in the query. Please mention a column name.'
            }
            
        # Extract condition
        condition = None
        for op, pattern in self.patterns['filters'].items():
            if re.search(pattern, query):
                condition = op
                break
                
        if not condition:
            return {
                'type': 'error',
                'message': 'No valid condition found. Please specify a condition (e.g., "greater than", "less than").'
            }
            
        # Extract value
        value = self._extract_value(query)
        if value is None:
            return {
                'type': 'error',
                'message': 'No valid value found. Please specify a value to compare against.'
            }
            
        # Apply filter
        column = columns[0]
        if column not in self.context.df.columns:
            return {
                'type': 'error',
                'message': f'Column "{column}" not found in the data.'
            }
            
        if condition == 'gt':
            filtered_df = self.context.df[self.context.df[column] > value]
        elif condition == 'lt':
            filtered_df = self.context.df[self.context.df[column] < value]
        elif condition == 'eq':
            filtered_df = self.context.df[self.context.df[column] == value]
        else:
            return {
                'type': 'error',
                'message': 'Unsupported condition. Please use "greater than", "less than", or "equal to".'
            }
            
        return {
            'type': 'filter',
            'filtered_data': filtered_df,
            'message': f'Found {len(filtered_df)} rows matching the criteria'
        }
        
    def _handle_chart_query(self, query: str, columns: List[str]) -> Dict:
        """Handle chart queries"""
        if not columns:
            return {
                'type': 'error',
                'message': 'No columns specified in the query. Please mention a column name.'
            }
            
        # Determine chart type
        chart_type = None
        for ctype, pattern in self.patterns['charts'].items():
            if re.search(pattern, query):
                chart_type = ctype
                break
                
        if not chart_type:
            chart_type = 'bar'  # Default to bar chart
            
        # Create chart
        column = columns[0]
        if column not in self.context.df.columns:
            return {
                'type': 'error',
                'message': f'Column "{column}" not found in the data.'
            }
            
        try:
            if chart_type == 'bar':
                fig = px.bar(self.context.df, x=column)
            elif chart_type == 'line':
                fig = px.line(self.context.df, x=column)
            elif chart_type == 'pie':
                fig = px.pie(self.context.df, names=column)
            elif chart_type == 'scatter':
                if len(columns) < 2:
                    return {
                        'type': 'error',
                        'message': 'Scatter plot requires two columns. Please specify both x and y columns.'
                    }
                fig = px.scatter(self.context.df, x=columns[0], y=columns[1])
            elif chart_type == 'histogram':
                fig = px.histogram(self.context.df, x=column)
            else:
                return {
                    'type': 'error',
                    'message': 'Unsupported chart type. Please try bar, line, pie, scatter, or histogram.'
                }
                
            return {
                'type': 'chart',
                'chart': fig,
                'message': f'Created {chart_type} chart for {column}'
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Error creating chart: {str(e)}'
            }
        
    def _extract_value(self, text: str) -> Optional[Union[float, str]]:
        """Extract value from text"""
        # Try to extract number
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            return float(numbers[0])
            
        # Try to extract date
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}'
        ]
        for pattern in date_patterns:
            dates = re.findall(pattern, text)
            if dates:
                return dates[0]
                
        return None 