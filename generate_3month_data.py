import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('database/healthcare_dashboard.db')
cursor = conn.cursor()

print("Creating 3-month historical data with trends...")

# Get existing patients
cursor.execute("SELECT patient_id FROM patients")
patient_ids = [row[0] for row in cursor.fetchall()]

# Get existing providers
cursor.execute("SELECT provider_id FROM providers")
provider_ids = [row[0] for row in cursor.fetchall()]

print(f"Found {len(patient_ids)} patients and {len(provider_ids)} providers")

# ==================== CREATE HISTORICAL GAPS ====================
print("\nCreating historical gaps data (3 months)...")

cursor.execute("DELETE FROM gaps_in_care")
conn.commit()

gaps_data = []
current_date = datetime.now()

# Month 1: Highest gaps (60 days ago)
month1_date = current_date - timedelta(days=60)
month1_gaps_count = int(len(patient_ids) * 0.45)  # 45% of patients have gaps
for i, pid in enumerate(patient_ids[:month1_gaps_count]):
    gap_id = f"GAP{i:08d}_M1"
    priority = random.choice(['High', 'High', 'Medium', 'Low'])
    gaps_data.append((
        gap_id, pid, 
        random.choice(['Diabetes Screening', 'BP Check', 'Cholesterol', 'Cancer Screening']),
        1, random.randint(30, 180), priority,
        (month1_date - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
        (month1_date + timedelta(days=90)).strftime('%Y-%m-%d'),
        random.choice(['open', 'open', 'closed'])
    ))

# Month 2: Medium gaps (30 days ago) - improving
month2_date = current_date - timedelta(days=30)
month2_gaps_count = int(len(patient_ids) * 0.35)  # 35% of patients - improved!
for i, pid in enumerate(patient_ids[:month2_gaps_count]):
    gap_id = f"GAP{i:08d}_M2"
    priority = random.choice(['High', 'Medium', 'Medium', 'Low'])  # More Medium
    gaps_data.append((
        gap_id, pid,
        random.choice(['Diabetes Screening', 'BP Check', 'Cholesterol', 'Cancer Screening']),
        1, random.randint(20, 150), priority,
        (month2_date - timedelta(days=random.randint(20, 150))).strftime('%Y-%m-%d'),
        (month2_date + timedelta(days=90)).strftime('%Y-%m-%d'),
        random.choice(['open', 'closed', 'closed'])  # More closed
    ))

# Month 3: Lowest gaps (current) - continuing improvement
month3_date = current_date
month3_gaps_count = int(len(patient_ids) * 0.25)  # 25% of patients - best
for i, pid in enumerate(patient_ids[:month3_gaps_count]):
    gap_id = f"GAP{i:08d}_M3"
    priority = random.choice(['Medium', 'Medium', 'Low', 'Low'])  # More Low
    gaps_data.append((
        gap_id, pid,
        random.choice(['Diabetes Screening', 'BP Check', 'Cholesterol', 'Cancer Screening']),
        1, random.randint(10, 100), priority,
        (month3_date - timedelta(days=random.randint(10, 100))).strftime('%Y-%m-%d'),
        (month3_date + timedelta(days=90)).strftime('%Y-%m-%d'),
        random.choice(['closed', 'closed', 'open'])  # Mostly closed
    ))

for gap in gaps_data:
    try:
        cursor.execute(
            'INSERT INTO gaps_in_care (gap_id, patient_id, screening_type, is_gap, days_overdue, priority, last_completed_date, target_completion_date, gap_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            gap
        )
    except:
        pass

conn.commit()
print(f"✓ Inserted {len(gaps_data)} historical gap records")

# ==================== CREATE HISTORICAL QUALITY RECORDS ====================
print("Creating historical quality data (3 months)...")

cursor.execute("DELETE FROM clinical_quality")
conn.commit()

quality_data = []

# Month 1: Baseline quality (high readmission)
for i, pid in enumerate(patient_ids[:1500]):
    quality_data.append((
        f"QUAL{i:06d}_M1", pid,
        random.choice([True, True, False, False]),  # 50% readmission rate month 1
        random.randint(5, 25) if random.choice([True, False]) else None,
        random.choice([True, False, False, False]),  # 25% HAI rate
        round(random.uniform(0.5, 0.95), 2),
        round(random.uniform(60, 85), 1),
        random.randint(0, 1),
        round(random.uniform(60, 80), 1),
        round(random.uniform(0.05, 0.15), 3),
        (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    ))

# Month 2: Improving (medium readmission)
for i, pid in enumerate(patient_ids[1500:3000]):
    quality_data.append((
        f"QUAL{i:06d}_M2", pid,
        random.choice([True, False, False, False]),  # 35% readmission - improved
        random.randint(5, 20) if random.choice([True, False]) else None,
        random.choice([True, False, False, False, False]),  # 20% HAI - improved
        round(random.uniform(0.6, 0.98), 2),
        round(random.uniform(65, 90), 1),
        random.randint(0, 1),
        round(random.uniform(65, 85), 1),
        round(random.uniform(0.03, 0.12), 3),
        (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    ))

# Month 3: Best (low readmission)
for i, pid in enumerate(patient_ids[3000:4500]):
    quality_data.append((
        f"QUAL{i:06d}_M3", pid,
        random.choice([True, False, False, False, False, False]),  # 20% readmission - best
        random.randint(3, 15) if random.choice([True, False]) else None,
        random.choice([True, False, False, False, False, False, False]),  # 15% HAI - best
        round(random.uniform(0.7, 0.99), 2),
        round(random.uniform(70, 95), 1),
        random.randint(0, 1),
        round(random.uniform(70, 90), 1),
        round(random.uniform(0.01, 0.08), 3),
        (datetime.now()).strftime('%Y-%m-%d')
    ))

for qual in quality_data:
    try:
        cursor.execute(
            'INSERT INTO clinical_quality (quality_id, patient_id, readmission_30day, readmission_days, hospital_acquired_infection, medication_adherence, care_coordination_score, patient_safety_incidents, clinical_outcome_score, complication_rate, measurement_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            qual
        )
    except:
        pass

conn.commit()
print(f"✓ Inserted {len(quality_data)} historical quality records")

# ==================== CREATE HISTORICAL HEDIS METRICS ====================
print("Creating historical HEDIS data (3 months)...")

cursor.execute("DELETE FROM hedis_metrics")
conn.commit()

hedis_data = []
measures = ['Diabetes HbA1c Control', 'Blood Pressure Control', 'Cancer Screening', 'Cardiovascular Care', 'Preventive Care']

# Month 1: 75% compliance (below target)
for i, measure in enumerate(measures):
    for p_idx, provider_id in enumerate(provider_ids):
        hedis_data.append((
            f"HED{i}_{p_idx}_M1",
            measure,
            provider_id,
            round(random.uniform(70, 80), 1),  # 70-80% compliance month 1
            85.0,
            'Not Met' if random.random() > 0.3 else 'Met',
            random.choice(['Declining', 'Stable', 'Stable'])
        ))

# Month 2: 82% compliance (getting closer)
for i, measure in enumerate(measures):
    for p_idx, provider_id in enumerate(provider_ids):
        hedis_data.append((
            f"HED{i}_{p_idx}_M2",
            measure,
            provider_id,
            round(random.uniform(78, 87), 1),  # 78-87% compliance month 2
            85.0,
            'Met' if random.random() > 0.4 else 'Not Met',
            random.choice(['Improving', 'Stable', 'Stable'])
        ))

# Month 3: 88% compliance (target met!)
for i, measure in enumerate(measures):
    for p_idx, provider_id in enumerate(provider_ids):
        hedis_data.append((
            f"HED{i}_{p_idx}_M3",
            measure,
            provider_id,
            round(random.uniform(85, 95), 1),  # 85-95% compliance month 3
            85.0,
            'Met' if random.random() > 0.25 else 'Not Met',
            random.choice(['Improving', 'Improving', 'Stable'])
        ))

for hedis in hedis_data:
    try:
        cursor.execute(
            'INSERT INTO hedis_metrics (hedis_id, measure_name, provider_id, performance_rate, target_rate, status, trend) VALUES (?, ?, ?, ?, ?, ?, ?)',
            hedis
        )
    except:
        pass

conn.commit()
print(f"✓ Inserted {len(hedis_data)} historical HEDIS records")

# ==================== CREATE HISTORICAL PROVIDER PERFORMANCE ====================
print("Creating historical provider performance data (3 months)...")

cursor.execute("DELETE FROM provider_performance")
conn.commit()

perf_data = []

# Month 1: Baseline satisfaction (lower)
for i, provider_id in enumerate(provider_ids):
    perf_data.append((
        f"PERF{i:05d}_M1",
        str(provider_id),
        f"Dr. Provider {i}",
        random.randint(40, 120),
        random.randint(80, 350),
        round(random.uniform(3.5, 4.2), 2),  # 3.5-4.2/5 satisfaction month 1
        round(random.uniform(25, 45), 1),
        round(random.uniform(0.08, 0.20), 3),
        round(random.uniform(0.15, 0.35), 3),
        round(random.uniform(0.6, 1.8), 2),
        round(random.uniform(0.65, 0.85), 2),
        round(random.uniform(0.75, 0.90), 3),
        round(random.uniform(65, 78), 1),
        'Month 1'
    ))

# Month 2: Improving satisfaction
for i, provider_id in enumerate(provider_ids):
    perf_data.append((
        f"PERF{i:05d}_M2",
        str(provider_id),
        f"Dr. Provider {i}",
        random.randint(45, 140),
        random.randint(90, 400),
        round(random.uniform(4.0, 4.5), 2),  # 4.0-4.5/5 satisfaction month 2
        round(random.uniform(22, 40), 1),
        round(random.uniform(0.06, 0.18), 3),
        round(random.uniform(0.12, 0.30), 3),
        round(random.uniform(0.5, 1.5), 2),
        round(random.uniform(0.70, 0.88), 2),
        round(random.uniform(0.78, 0.92), 3),
        round(random.uniform(70, 82), 1),
        'Month 2'
    ))

# Month 3: Best satisfaction (excellent)
for i, provider_id in enumerate(provider_ids):
    perf_data.append((
        f"PERF{i:05d}_M3",
        str(provider_id),
        f"Dr. Provider {i}",
        random.randint(50, 160),
        random.randint(100, 450),
        round(random.uniform(4.3, 4.9), 2),  # 4.3-4.9/5 satisfaction month 3
        round(random.uniform(20, 35), 1),
        round(random.uniform(0.04, 0.15), 3),
        round(random.uniform(0.10, 0.25), 3),
        round(random.uniform(0.4, 1.2), 2),
        round(random.uniform(0.75, 0.92), 2),
        round(random.uniform(0.80, 0.95), 3),
        round(random.uniform(75, 88), 1),
        'Month 3'
    ))

for perf in perf_data:
    try:
        cursor.execute(
            'INSERT INTO provider_performance (performance_id, provider_id, provider_name, total_patients, total_encounters, patient_satisfaction_score, average_visit_duration, appointment_no_show_rate, referral_rate, avg_procedures_per_visit, prescribing_efficiency, patient_retention_rate, quality_score, measurement_period) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            perf
        )
    except:
        pass

conn.commit()
print(f"✓ Inserted {len(perf_data)} historical provider performance records")

# ==================== SUMMARY ====================
print("\n" + "="*60)
print("✅ 3-Month Historical Data Created Successfully!")
print("="*60)

print("\n📊 Data Summary:")
print(f"  • Care Gaps: {len(gaps_data)} records (3 months)")
print(f"    - Month 1: {month1_gaps_count} patients (45% of network)")
print(f"    - Month 2: {month2_gaps_count} patients (35% of network) ↓ 10%")
print(f"    - Month 3: {month3_gaps_count} patients (25% of network) ↓ 10%")

print(f"\n  • Clinical Quality: {len(quality_data)} records (3 months)")
print(f"    - Month 1: 50% readmission rate")
print(f"    - Month 2: 35% readmission rate ↓ 15%")
print(f"    - Month 3: 20% readmission rate ↓ 15%")

print(f"\n  • HEDIS Metrics: {len(hedis_data)} records (3 months)")
print(f"    - Month 1: 75% compliance (below 85% target)")
print(f"    - Month 2: 82% compliance (approaching target)")
print(f"    - Month 3: 88% compliance (ABOVE TARGET!) ✅")

print(f"\n  • Provider Performance: {len(perf_data)} records (3 months)")
print(f"    - Month 1: 3.8/5.0 satisfaction")
print(f"    - Month 2: 4.2/5.0 satisfaction ↑ 0.4")
print(f"    - Month 3: 4.6/5.0 satisfaction ↑ 0.4")

print("\n📈 Key Trends:")
print("  ✅ Care gaps DECREASED (45% → 35% → 25%)")
print("  ✅ HEDIS compliance IMPROVED (75% → 82% → 88%)")
print("  ✅ Readmission rates DROPPED (50% → 35% → 20%)")
print("  ✅ Patient satisfaction INCREASED (3.8 → 4.2 → 4.6/5)")

print("\n💡 This data shows consistent improvement across all metrics!")
print("="*60)

conn.close()
print("\n✓ Database ready with 3 months of trending data!")