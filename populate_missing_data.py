import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('database/healthcare_dashboard.db')
cursor = conn.cursor()

print("Populating missing data...")

# Get existing data
patients_df = pd.read_sql("SELECT * FROM patients", conn)
providers_df = pd.read_sql("SELECT * FROM providers", conn)

patient_ids = patients_df['patient_id'].tolist()
provider_ids = providers_df['provider_id'].tolist()

print(f"Found {len(patient_ids)} patients and {len(provider_ids)} providers")

# Clear existing data in empty tables
print("\nClearing old data...")
try:
    cursor.execute("DELETE FROM gaps_in_care")
    cursor.execute("DELETE FROM encounters")
    cursor.execute("DELETE FROM provider_performance")
    cursor.execute("DELETE FROM clinical_quality")
    conn.commit()
except:
    pass

# 1. Insert gaps_in_care data
print("Inserting gaps_in_care...")
gaps_data = []
gap_id_counter = 0

for patient_idx, patient_id in enumerate(patient_ids[:2000]):
    num_gaps = random.randint(1, 4)
    for j in range(num_gaps):
        gap_id_counter += 1
        gaps_data.append((
            f"GAP{gap_id_counter:06d}",
            patient_id,
            random.choice(['Diabetes Screening', 'Blood Pressure Check', 'Cholesterol Screening', 'Cancer Screening', 'Preventive Care']),
            random.choice([True, False, True, True]),  # More True values
            random.randint(0, 365) if random.choice([True, False]) else 0,
            random.choice(['High', 'Medium', 'Low', 'Low']),  # More Low values
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d'),
            random.choice(['open', 'closed', 'open', 'open'])  # More open values
        ))

for gap in gaps_data:
    try:
        cursor.execute(
            'INSERT INTO gaps_in_care (gap_id, patient_id, screening_type, is_gap, days_overdue, priority, last_completed_date, target_completion_date, gap_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            gap
        )
    except Exception as e:
        pass

conn.commit()
print(f"✓ Inserted {len(gaps_data)} gaps_in_care records")

# 2. Insert encounters data
print("Inserting encounters...")
encounters_data = []
enc_id_counter = 0

for patient_idx, patient_id in enumerate(patient_ids[:3000]):
    num_encounters = random.randint(1, 6)
    for j in range(num_encounters):
        enc_id_counter += 1
        encounters_data.append((
            f"ENC{enc_id_counter:06d}",
            patient_id,
            random.choice(provider_ids),
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            random.choice(['Office Visit', 'Telehealth', 'ER', 'Inpatient', 'Office Visit', 'Office Visit']),
            random.choice(['E11.9', 'I10', 'J45.9', 'I50.9', 'J44.9']),
            random.choice(['Diabetes', 'Hypertension', 'Asthma', 'Heart Failure', 'COPD']),
            random.randint(0, 3),
            random.randint(1, 8),
            random.randint(10, 90)
        ))

for enc in encounters_data:
    try:
        cursor.execute(
            'INSERT INTO encounters (encounter_id, patient_id, provider_id, encounter_date, encounter_type, icd10_code, diagnosis, procedures, medications_prescribed, visit_duration_minutes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            enc
        )
    except Exception as e:
        pass

conn.commit()
print(f"✓ Inserted {len(encounters_data)} encounters records")

# 3. Insert provider_performance data
print("Inserting provider_performance...")
perf_data = []

for i, provider_id in enumerate(provider_ids):
    perf_data.append((
        f"PERF{i:05d}",
        str(provider_id),  # Convert to string
        f"Dr. Provider {i}",
        random.randint(50, 250),
        random.randint(100, 600),
        round(random.uniform(3.5, 5.0), 2),
        round(random.uniform(20, 60), 1),
        round(random.uniform(0.05, 0.25), 3),
        round(random.uniform(0.1, 0.4), 3),
        round(random.uniform(0.5, 2.5), 2),
        round(random.uniform(0.6, 0.95), 2),
        round(random.uniform(0.7, 0.98), 3),
        round(random.uniform(60, 95), 1),
        '2024'
    ))

for perf in perf_data:
    try:
        cursor.execute(
            'INSERT INTO provider_performance (performance_id, provider_id, provider_name, total_patients, total_encounters, patient_satisfaction_score, average_visit_duration, appointment_no_show_rate, referral_rate, avg_procedures_per_visit, prescribing_efficiency, patient_retention_rate, quality_score, measurement_period) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            perf
        )
    except Exception as e:
        print(f"Provider performance error: {e}")

conn.commit()
print(f"✓ Inserted {len(perf_data)} provider_performance records")

# 4. Insert clinical_quality data
print("Inserting clinical_quality...")
quality_data = []

for i, patient_id in enumerate(patient_ids[:2000]):
    has_readmission = random.choice([True, False, False, False])  # 25% chance
    quality_data.append((
        f"QUAL{i:06d}",
        patient_id,
        has_readmission,
        random.randint(1, 30) if has_readmission else None,
        random.choice([True, False, False, False]),  # 25% chance
        round(random.uniform(0.5, 1.0), 2),
        round(random.uniform(60, 100), 1),
        random.randint(0, 2),
        round(random.uniform(60, 100), 1),
        round(random.uniform(0.0, 0.15), 3),
        (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
    ))

for qual in quality_data:
    try:
        cursor.execute(
            'INSERT INTO clinical_quality (quality_id, patient_id, readmission_30day, readmission_days, hospital_acquired_infection, medication_adherence, care_coordination_score, patient_safety_incidents, clinical_outcome_score, complication_rate, measurement_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            qual
        )
    except Exception as e:
        pass

conn.commit()
print(f"✓ Inserted {len(quality_data)} clinical_quality records")

# Verify data
print("\n" + "="*50)
print("✅ Data insertion complete!")
print("="*50)
print("\nFinal record counts:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    status = "✓" if count > 0 else "✗"
    print(f"  {status} {table[0]}: {count} records")

conn.close()
print("\n✅ Database ready! Restart your dashboard.")
print("="*50)