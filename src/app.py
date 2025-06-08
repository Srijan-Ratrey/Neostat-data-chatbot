import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import os
from core.chat_engine import ChatEngine

# Initialize session state
if 'chat_engine' not in st.session_state:
    st.session_state.chat_engine = ChatEngine()
if 'df' not in st.session_state:
    st.session_state.df = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Set page config
st.set_page_config(
    page_title="Data Chat",
    page_icon="💬",
    layout="wide"
)

# Title and description
st.title("💬 Data Chat")
st.markdown("""
Ask questions about your data in natural language. The chatbot will help you analyze and visualize your data!
""")

# File upload
uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        # Create a temporary file path
        temp_file_path = f"temp_{uploaded_file.name}"
        
        # Save the uploaded file
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
            
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(temp_file_path, encoding='utf-8')
        else:
            df = pd.read_excel(temp_file_path, engine='openpyxl')
            
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        # Store in session state
        st.session_state.df = df
        
        # Load data into chat engine
        st.session_state.chat_engine.load_data(df)
        
        # Display data summary
        st.subheader("📊 Data Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("File Type", uploaded_file.name.split('.')[-1].upper())
            
        # Display column information
        st.subheader("📋 Available Columns")
        for col in df.columns:
            col_type = st.session_state.chat_engine.context.column_types[col]
            st.markdown(f"- **{col}** ({col_type})")
            
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        st.info("Please make sure your file is a valid Excel or CSV file with proper formatting.")
        st.session_state.df = None

# Chat interface
if st.session_state.df is not None:
    st.subheader("💭 Chat with Your Data")
    
    # Display chat history
    for entry in st.session_state.query_history:
        with st.chat_message("user"):
            st.write(entry['query'])
        with st.chat_message("assistant"):
            if entry['result']['type'] == 'error':
                st.error(entry['result']['message'])
            else:
                st.success(entry['result']['message'])
                if entry['result']['type'] == 'statistical':
                    st.metric(
                        f"{entry['result']['function'].title()} of {entry['result']['column']}", 
                        f"{entry['result']['result']:.2f}"
                    )
                elif entry['result']['type'] == 'filter':
                    st.dataframe(entry['result']['filtered_data'])
                elif entry['result']['type'] == 'chart':
                    st.plotly_chart(entry['result']['chart'])
    
    # Query input
    query = st.chat_input("Ask a question about your data...")
    
    if query:
        # Add user message to chat
        with st.chat_message("user"):
            st.write(query)
            
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                start_time = time.time()
                result = st.session_state.chat_engine.process_query(query)
                processing_time = time.time() - start_time
                
                if result['type'] == 'error':
                    st.error(result['message'])
                else:
                    st.success(result['message'])
                    
                    if result['type'] == 'statistical':
                        st.metric(
                            f"{result['function'].title()} of {result['column']}", 
                            f"{result['result']:.2f}"
                        )
                    elif result['type'] == 'filter':
                        st.dataframe(result['filtered_data'])
                    elif result['type'] == 'chart':
                        st.plotly_chart(result['chart'])
                        
                    st.caption(f"Processed in {processing_time:.2f} seconds")
                    
                # Add to history
                st.session_state.query_history.append({
                    'query': query,
                    'result': result,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

# Example queries
st.subheader("💡 Example Queries")
st.markdown("""
Try asking questions like:
- What is the average price?
- Show me products above $100
- Create a pie chart of sales by category
- What is the highest price?
- Show me the distribution of prices
""") 