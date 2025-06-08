import spacy
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass
from enum import Enum

class QueryType(Enum):
    STATISTICAL = "statistical"
    FILTER = "filter"
    COMPARISON = "comparison"
    VISUALIZATION = "visualization"
    UNKNOWN = "unknown"

@dataclass
class QueryIntent:
    type: QueryType
    columns: List[str]
    conditions: List[Dict]
    aggregation: Optional[str] = None
    visualization_type: Optional[str] = None
    group_by: Optional[List[str]] = None
    order_by: Optional[Dict] = None
    limit: Optional[int] = None

class QueryUnderstanding:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
            
        # Initialize query patterns
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize patterns for different types of queries"""
        # Statistical patterns
        self.statistical_patterns = {
            'average': {
                'terms': ['average', 'mean', 'avg'],
                'function': 'mean'
            },
            'sum': {
                'terms': ['sum', 'total', 'sum of'],
                'function': 'sum'
            },
            'count': {
                'terms': ['count', 'number of', 'how many'],
                'function': 'count'
            },
            'min': {
                'terms': ['minimum', 'lowest', 'smallest', 'least'],
                'function': 'min'
            },
            'max': {
                'terms': ['maximum', 'highest', 'largest', 'most'],
                'function': 'max'
            },
            'median': {
                'terms': ['median', 'middle'],
                'function': 'median'
            }
        }
        
        # Filter patterns
        self.filter_patterns = {
            'comparison': {
                'terms': ['greater than', 'more than', 'above', 'less than', 'below', 'equal to', 'equals'],
                'operators': {
                    'greater than': '>',
                    'more than': '>',
                    'above': '>',
                    'less than': '<',
                    'below': '<',
                    'equal to': '==',
                    'equals': '=='
                }
            },
            'range': {
                'terms': ['between', 'from', 'to'],
                'operator': 'between'
            }
        }
        
        # Visualization patterns
        self.visualization_patterns = {
            'bar': {
                'terms': ['bar', 'bar chart', 'bars'],
                'type': 'bar'
            },
            'line': {
                'terms': ['line', 'line chart', 'trend'],
                'type': 'line'
            },
            'pie': {
                'terms': ['pie', 'pie chart', 'distribution'],
                'type': 'pie'
            },
            'scatter': {
                'terms': ['scatter', 'scatter plot', 'correlation'],
                'type': 'scatter'
            },
            'histogram': {
                'terms': ['histogram', 'distribution'],
                'type': 'histogram'
            }
        }
        
        # Comparison patterns
        self.comparison_patterns = {
            'compare': {
                'terms': ['compare', 'comparison', 'versus', 'vs', 'against'],
                'type': 'comparison'
            },
            'group': {
                'terms': ['by', 'group by', 'grouped by'],
                'type': 'group'
            }
        }
    
    def understand_query(self, query: str, schema: Dict) -> QueryIntent:
        """
        Understand the natural language query and return structured intent
        """
        # Preprocess query
        query = query.lower().strip()
        doc = self.nlp(query)
        
        # Identify query type
        query_type = self._identify_query_type(query)
        
        # Extract columns
        columns = self._extract_columns(query, schema)
        
        # Initialize query intent
        intent = QueryIntent(
            type=query_type,
            columns=columns,
            conditions=[],
            aggregation=None,
            visualization_type=None,
            group_by=None,
            order_by=None,
            limit=None
        )
        
        # Process based on query type
        if query_type == QueryType.STATISTICAL:
            self._process_statistical_query(query, intent)
        elif query_type == QueryType.FILTER:
            self._process_filter_query(query, intent)
        elif query_type == QueryType.COMPARISON:
            self._process_comparison_query(query, intent)
        elif query_type == QueryType.VISUALIZATION:
            self._process_visualization_query(query, intent)
        
        return intent
    
    def _identify_query_type(self, query: str) -> QueryType:
        """Identify the type of query"""
        # Check for statistical terms
        if any(term in query for pattern in self.statistical_patterns.values() 
               for term in pattern['terms']):
            return QueryType.STATISTICAL
            
        # Check for visualization terms
        if any(term in query for pattern in self.visualization_patterns.values() 
               for term in pattern['terms']):
            return QueryType.VISUALIZATION
            
        # Check for comparison terms
        if any(term in query for pattern in self.comparison_patterns.values() 
               for term in pattern['terms']):
            return QueryType.COMPARISON
            
        # Check for filter terms
        if any(term in query for pattern in self.filter_patterns.values() 
               for term in pattern['terms']):
            return QueryType.FILTER
            
        return QueryType.UNKNOWN
    
    def _extract_columns(self, query: str, schema: Dict) -> List[str]:
        """Extract relevant columns from the query"""
        columns = []
        query_words = set(query.lower().split())
        
        for col in schema.keys():
            # Check for exact match
            if col.lower() in query_words:
                columns.append(col)
                continue
                
            # Check for semantic similarity
            col_doc = self.nlp(col.lower())
            query_doc = self.nlp(query.lower())
            if col_doc.similarity(query_doc) > 0.7:
                columns.append(col)
                
        return columns
    
    def _process_statistical_query(self, query: str, intent: QueryIntent):
        """Process statistical query"""
        # Extract aggregation function
        for pattern in self.statistical_patterns.values():
            if any(term in query for term in pattern['terms']):
                intent.aggregation = pattern['function']
                break
    
    def _process_filter_query(self, query: str, intent: QueryIntent):
        """Process filter query"""
        # Extract conditions
        for pattern in self.filter_patterns.values():
            if any(term in query for term in pattern['terms']):
                for term, operator in pattern['operators'].items():
                    if term in query:
                        # Extract value
                        parts = query.split(term)
                        if len(parts) > 1 and intent.columns:
                            value = self._extract_value(parts[1])
                            intent.conditions.append({
                                'column': intent.columns[0],
                                'operator': operator,
                                'value': value
                            })
    
    def _process_comparison_query(self, query: str, intent: QueryIntent):
        """Process comparison query"""
        # Extract group by
        for pattern in self.comparison_patterns.values():
            if any(term in query for term in pattern['terms']):
                if pattern['type'] == 'group':
                    # Extract group by columns
                    parts = query.split(term)
                    if len(parts) > 1:
                        group_cols = self._extract_columns(parts[1], {})
                        intent.group_by = group_cols
    
    def _process_visualization_query(self, query: str, intent: QueryIntent):
        """Process visualization query"""
        # Extract visualization type
        for pattern in self.visualization_patterns.values():
            if any(term in query for term in pattern['terms']):
                intent.visualization_type = pattern['type']
                break
    
    def _extract_value(self, text: str) -> any:
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
                
        # Return as string
        return text.strip() 