import sqlite3

conn = sqlite3.connect('database/healthcare_dashboard.db')
cursor = conn.cursor()

# Check gaps_in_care table structure
print("Gaps in care table structure:")
cursor.execute("PRAGMA table_info(gaps_in_care)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
