import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('database/healthcare_dashboard.db')
cursor = conn.cursor()

print("Fixing gaps_in_care table...")

# Check if gap_type column exists
cursor.execute("PRAGMA table_info(gaps_in_care)")
columns = [col[1] for col in cursor.fetchall()]

if 'gap_type' not in columns:
    print("Adding gap_type column...")
    try:
        cursor.execute("ALTER TABLE gaps_in_care ADD COLUMN gap_type TEXT DEFAULT 'open'")
        conn.commit()
        print("✓ Column added")
    except Exception as e:
        print(f"Error: {e}")

# Update existing gaps with gap_type
print("Updating gaps with gap_type...")
cursor.execute("UPDATE gaps_in_care SET gap_type = ? WHERE gap_type IS NULL", ('open',))
cursor.execute("UPDATE gaps_in_care SET gap_type = ? WHERE is_gap = ?", ('closed', 0))
cursor.execute("UPDATE gaps_in_care SET gap_type = ? WHERE is_gap = ?", ('open', 1))
conn.commit()

# Verify
cursor.execute("SELECT gap_type, COUNT(*) FROM gaps_in_care GROUP BY gap_type")
print("\nGap type distribution:")
for gap_type, count in cursor.fetchall():
    print(f"  {gap_type}: {count}")

conn.close()
print("\n✅ Gaps fixed!")
