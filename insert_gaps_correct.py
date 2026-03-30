import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('database/healthcare_dashboard.db')
cursor = conn.cursor()

# Get patients
cursor.execute("SELECT patient_id FROM patients LIMIT 2000")
patients = [row[0] for row in cursor.fetchall()]

print(f"Creating gaps for {len(patients)} patients...")

# Clear table
cursor.execute("DELETE FROM gaps_in_care")
conn.commit()

# Insert gaps with CORRECT columns
gap_counter = 0
gaps_list = []

for patient_id in patients:
    for i in range(random.randint(1, 4)):
        gap_counter += 1
        gaps_list.append((
            f"GAP{gap_counter:07d}",
            patient_id,
            random.choice(['Diabetes Screening', 'BP Check', 'Cholesterol', 'Cancer Screening', 'Preventive Care']),
            random.choice([True, True, False]),  # mostly True
            random.randint(0, 200),
            random.choice(['High', 'Medium', 'Low', 'Low']),
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d')
        ))

print(f"Inserting {len(gaps_list)} gaps...")

for gap in gaps_list:
    try:
        cursor.execute(
            '''INSERT INTO gaps_in_care 
               (gap_id, patient_id, screening_type, is_gap, days_overdue, priority, last_completed_date, target_completion_date) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            gap
        )
    except Exception as e:
        print(f"Error: {e}")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM gaps_in_care")
count = cursor.fetchone()[0]
print(f"✅ Successfully inserted {count} gaps")

# Show summary
cursor.execute("SELECT priority, COUNT(*) FROM gaps_in_care GROUP BY priority")
for priority, cnt in cursor.fetchall():
    print(f"   {priority}: {cnt}")

conn.close()
