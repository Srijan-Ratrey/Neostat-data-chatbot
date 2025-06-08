# Excel Insights Chatbot

A web-based chatbot that helps users get insights from Excel files through natural language conversations.

## Features

- Excel file upload and processing
- Natural language query processing
- Data analysis and visualization
- Interactive chat interface
- Support for various types of queries:
  - Statistical summaries
  - Filtered queries
  - Comparisons and groupings
  - Visual insights

## Project Structure

```
├── src/
│   ├── utils/         # Utility functions
│   ├── components/    # UI components
│   ├── models/        # Data processing models
├── tests/            # Test files
├── data/             # Sample data
├── requirements.txt  # Project dependencies
└── README.md        # Project documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run src/app.py
```

## Usage

1. Upload an Excel file (.xlsx format)
2. Ask questions in natural language
3. View results in text, table, or chart format

## Development Guidelines

- No hardcoding of column names or schemas
- Schema-agnostic design
- Clear error handling and user feedback
- Modular and maintainable code structure

## Testing

Run tests using pytest:
```bash
pytest tests/
``` 