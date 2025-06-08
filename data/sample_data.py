import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
n_records = 100

data = {
    'employee_id': range(1, n_records + 1),
    'name': [f'Employee_{i}' for i in range(1, n_records + 1)],
    'age': np.random.randint(22, 60, n_records),
    'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing', 'Sales'], n_records),
    'salary': np.random.randint(30000, 120000, n_records),
    'experience': np.random.randint(0, 20, n_records),
    'performance_score': np.random.uniform(1, 5, n_records).round(2),
    'attendance': np.random.randint(80, 101, n_records)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('data/sample_data.xlsx', index=False)
print("Sample data created successfully!") 