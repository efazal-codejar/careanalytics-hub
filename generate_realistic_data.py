import sqlite3
import random
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('database/healthcare_dashboard.db')
cursor = conn.cursor()

print("Completely regenerating gaps with realistic data...")
print("="*60)

# Get patients
cursor.execute("SELECT patient_id FROM patients LIMIT 5000")
patient_ids = [row[0] for row in cursor.fetchall()]
print(f"✓ Found {len(patient_ids)} patients")

# Step 1: DROP and RECREATE table (complete reset)
print("\nStep 1: Dropping and recreating gaps_in_care table...")
try:
    cursor.execute("DROP TABLE gaps_in_care")
    print("✓ Old table dropped")
except:
    print("✓ Table didn't exist, that's okay")

# Recreate table
cursor.execute('''
CREATE TABLE gaps_in_care (
    gap_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    screening_type TEXT,
    is_gap BOOLEAN,
    days_overdue INTEGER,
    priority TEXT,
    last_completed_date TEXT,
    target_completion_date TEXT,
    gap_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
print("✓ New table created")

# Step 2: Generate realistic gaps
print("\nStep 2: Generating realistic gaps...")

screening_types = [
    'Diabetes Screening',
    'Blood Pressure Check',
    'Cholesterol Test',
    'Cancer Screening',
    'Preventive Care Visit',
    'Immunizations'
]

gaps = []
gap_counter = 0

# Create 1,200 gaps (realistic number for 5,000 patients)
for i in range(1200):
    patient_id = random.choice(patient_ids)
    screening_type = random.choice(screening_types)
    priority = random.choices(['High', 'Medium', 'Low'], weights=[0.25, 0.35, 0.40])[0]
    
    # Realistic open/closed distribution based on priority
    if priority == 'High':
        is_open = random.random() > 0.40  # 40% closed, 60% open
    elif priority == 'Medium':
        is_open = random.random() > 0.65  # 65% closed, 35% open
    else:
        is_open = random.random() > 0.85  # 85% closed, 15% open
    
    days_overdue = random.randint(10, 200) if is_open else random.randint(5, 30)
    gap_type = 'open' if is_open else 'closed'
    
    gap_id = f"GAP{i:07d}"
    last_completed = (datetime.now() - timedelta(days=days_overdue)).strftime('%Y-%m-%d')
    target_completion = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    
    gaps.append((
        gap_id,
        patient_id,
        screening_type,
        1,
        days_overdue,
        priority,
        last_completed,
        target_completion,
        gap_type
    ))

# Step 3: Insert all gaps
print(f"Inserting {len(gaps)} new gaps...")
for gap in gaps:
    try:
        cursor.execute(
            'INSERT INTO gaps_in_care (gap_id, patient_id, screening_type, is_gap, days_overdue, priority, last_completed_date, target_completion_date, gap_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            gap
        )
    except Exception as e:
        print(f"Error inserting gap: {e}")

conn.commit()
print(f"✓ Inserted {len(gaps)} gaps")

# Step 4: Verify data
print("\nStep 4: Verifying data...")

cursor.execute("SELECT COUNT(*) FROM gaps_in_care")
total = cursor.fetchone()[0]
print(f"✓ Total gaps in table: {total}")

cursor.execute("SELECT COUNT(*) FROM gaps_in_care WHERE gap_type = 'open'")
open_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM gaps_in_care WHERE gap_type = 'closed'")
closed_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM gaps_in_care WHERE gap_type IS NULL")
null_count = cursor.fetchone()[0]

print(f"✓ Open gaps: {open_count}")
print(f"✓ Closed gaps: {closed_count}")
print(f"✓ NULL gap_type: {null_count}")

# Final summary
print("\n" + "="*60)
print("✅ GAPS COMPLETELY REGENERATED")
print("="*60)

print(f"\nSummary:")
print(f"  Total Gaps: {total:,}")
print(f"  Open Gaps: {open_count:,} ({open_count/total*100:.1f}%)")
print(f"  Closed Gaps: {closed_count:,} ({closed_count/total*100:.1f}%)")
print(f"  Closure Rate: {closed_count/total*100:.1f}%")

print(f"\nBy Priority:")
cursor.execute("SELECT priority, COUNT(*) FROM gaps_in_care GROUP BY priority ORDER BY priority")
for priority, count in cursor.fetchall():
    print(f"  {priority}: {count:,}")

print(f"\nBy Screening Type:")
cursor.execute("SELECT screening_type, COUNT(*) FROM gaps_in_care GROUP BY screening_type ORDER BY COUNT(*) DESC")
for screening, count in cursor.fetchall():
    print(f"  {screening}: {count:,}")

print("\n" + "="*60)
print("✓ Data regeneration complete!")
print("✓ Dashboard is ready to restart")
print("="*60)

conn.close()