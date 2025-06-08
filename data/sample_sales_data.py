import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate sample data
n_records = 100

# Generate dates for the last 100 days
end_date = datetime.now()
dates = [end_date - timedelta(days=x) for x in range(n_records)]

# Generate sample data
data = {
    'date': dates,
    'product_category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books', 'Home'], n_records),
    'sales_amount': np.random.uniform(100, 1000, n_records).round(2),
    'quantity_sold': np.random.randint(1, 10, n_records),
    'customer_segment': np.random.choice(['Retail', 'Wholesale', 'Online'], n_records),
    'region': np.random.choice(['North', 'South', 'East', 'West'], n_records)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('data/sample_sales.xlsx', index=False)
print("Sample sales data created successfully!") 