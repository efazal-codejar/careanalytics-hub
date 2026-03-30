import sqlite3
import os
import pandas as pd

print('Current directory:', os.getcwd())

# Create database
db_path = 'database/healthcare_dashboard.db'
print(f'Creating: {db_path}')

conn = sqlite3.connect(db_path)
print(f'Connected!')

# Create tables
conn.execute('''CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    age INTEGER,
    gender TEXT
)''')

# Load data
try:
    df = pd.read_csv('data/patients.csv')
    df.to_sql('patients', conn, if_exists='append', index=False)
    print(f'Loaded {len(df)} patients')
except Exception as e:
    print(f'Error loading: {e}')

conn.commit()
conn.close()

print('Done! Check database folder.')