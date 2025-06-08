import pytest
import pandas as pd
from src.utils.query_parser import QueryParser

@pytest.fixture
def sample_df():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'HR'],
        'experience': [2, 5, 8, 12, 15]
    })

@pytest.fixture
def parser():
    """Create a QueryParser instance."""
    return QueryParser()

def test_statistical_query(parser, sample_df):
    """Test parsing of statistical queries."""
    query = "What is the average salary?"
    result = parser.parse_query(query, sample_df)
    
    assert result['query_type'] == 'statistical'
    assert 'salary' in result['columns']
    assert result['aggregation'] == 'mean'

def test_filter_query(parser, sample_df):
    """Test parsing of filter queries."""
    query = "Show employees where age is greater than 30"
    result = parser.parse_query(query, sample_df)
    
    assert result['query_type'] == 'filter'
    assert 'age' in result['columns']
    assert len(result['conditions']) > 0
    assert result['conditions'][0]['operator'] == '>'
    assert result['conditions'][0]['value'] == 30

def test_comparison_query(parser, sample_df):
    """Test parsing of comparison queries."""
    query = "Compare salary by department"
    result = parser.parse_query(query, sample_df)
    
    assert result['query_type'] == 'comparison'
    assert 'salary' in result['columns']
    assert 'department' in result['columns']

def test_visualization_query(parser, sample_df):
    """Test parsing of visualization queries."""
    query = "Show a bar chart of salary by department"
    result = parser.parse_query(query, sample_df)
    
    assert result['query_type'] == 'visualization'
    assert result['visualization_type'] == 'bar'
    assert 'salary' in result['columns']
    assert 'department' in result['columns']

def test_query_validation(parser, sample_df):
    """Test query validation."""
    # Valid query
    valid_query = "What is the average salary?"
    valid_result = parser.parse_query(valid_query, sample_df)
    is_valid, message = parser.validate_query(valid_result, sample_df)
    assert is_valid
    assert message == "Query is valid"
    
    # Invalid query (no columns)
    invalid_query = "What is the average?"
    invalid_result = parser.parse_query(invalid_query, sample_df)
    is_valid, message = parser.validate_query(invalid_result, sample_df)
    assert not is_valid
    assert "No valid columns found" in message

def test_extract_operators(parser):
    """Test operator extraction."""
    query = "Show employees with salary greater than 50000 and less than 100000"
    operators = parser._extract_operators(query)
    assert '>' in operators
    assert '<' in operators

def test_extract_numeric_values(parser):
    """Test numeric value extraction."""
    query = "Show employees with salary between 50000 and 100000"
    values = parser._extract_numeric_values(query)
    assert 50000 in values
    assert 100000 in values 