# Database Schema 📊

Complete documentation of the CareAnalytics Hub SQLite database structure.

---

## Database Overview

- **Type**: SQLite3
- **Location**: `database/healthcare_dashboard.db`
- **Auto-Created**: Yes (on first run)
- **Tables**: 7
- **Records**: ~13,000 total

---

## Tables

### 1. patients
**Purpose**: Core patient population data

| Column | Type | Description |
|--------|------|-------------|
| patient_id | TEXT (PK) | Unique patient identifier (e.g., "P001") |
| age | INTEGER | Patient age (18-85) |
| gender | TEXT | M/F |
| risk_score | REAL | 1.0-5.0 (low to high risk) |
| enrollment_date | DATE | When patient enrolled |
| status | TEXT | Active/Inactive |

**Sample Data**: 5,000 patients

**Queries**:
```sql
-- Get high-risk patients
SELECT * FROM patients WHERE risk_score > 3.5;

-- Get patient count by age group
SELECT 
    CASE 
        WHEN age < 30 THEN '18-30'
        WHEN age < 40 THEN '31-40'
        WHEN age < 50 THEN '41-50'
        ELSE '50+'
    END as age_group,
    COUNT(*) as count
FROM patients
GROUP BY age_group;

-- Average risk score
SELECT AVG(risk_score) FROM patients;
```

---

### 2. gaps_in_care
**Purpose**: Patient care gaps (missing screenings/services)

| Column | Type | Description |
|--------|------|-------------|
| gap_id | TEXT (PK) | Unique identifier (e.g., "G_M3_001") |
| patient_id | TEXT (FK) | Reference to patients.patient_id |
| screening_type | TEXT | Type of screening (Diabetes, BP, Cancer, etc.) |
| priority | TEXT | High/Medium/Low |
| gap_type | TEXT | open/closed |
| days_overdue | INTEGER | How many days past due |
| target_completion_date | DATE | When should be closed |

**Sample Data**: 1,200 gaps

**Queries**:
```sql
-- Count gaps by priority
SELECT priority, COUNT(*) as count FROM gaps_in_care GROUP BY priority;

-- Open vs closed
SELECT gap_type, COUNT(*) FROM gaps_in_care GROUP BY gap_type;

-- Gaps by screening type
SELECT screening_type, COUNT(*) FROM gaps_in_care GROUP BY screening_type;

-- High priority open gaps
SELECT * FROM gaps_in_care 
WHERE priority = 'High' AND gap_type = 'open'
ORDER BY days_overdue DESC;

-- Gap closure rate
SELECT 
    COUNT(CASE WHEN gap_type = 'closed' THEN 1 END) * 100.0 / COUNT(*) as closure_rate
FROM gaps_in_care;
```

---

### 3. providers
**Purpose**: Healthcare provider information

| Column | Type | Description |
|--------|------|-------------|
| provider_id | TEXT (PK) | Unique provider ID (e.g., "PROV001") |
| provider_name | TEXT | Provider's full name |
| provider_type | TEXT | PCP/Specialist |
| specialty | TEXT | Medical specialty |
| phone | TEXT | Contact number |
| network_status | TEXT | Active/Inactive |

**Sample Data**: 150 providers

**Queries**:
```sql
-- Count by provider type
SELECT provider_type, COUNT(*) FROM providers GROUP BY provider_type;

-- Active providers
SELECT COUNT(*) FROM providers WHERE network_status = 'Active';

-- Providers by specialty
SELECT specialty, COUNT(*) FROM providers GROUP BY specialty;
```

---

### 4. provider_performance
**Purpose**: Provider quality metrics and satisfaction scores

| Column | Type | Description |
|--------|------|-------------|
| performance_id | TEXT (PK) | Unique identifier |
| provider_id | TEXT (FK) | Reference to providers.provider_id |
| provider_name | TEXT | Provider name (redundant but convenient) |
| total_patients | INTEGER | Number of patients assigned |
| patient_satisfaction_score | REAL | 0-5.0 scale |
| appointment_no_show_rate | REAL | % no-shows |
| referral_rate | REAL | % referrals made |
| quality_score | INTEGER | 0-100 |
| patient_retention_rate | REAL | % staying with provider |
| average_visit_duration | INTEGER | Minutes |

**Sample Data**: 150 records (one per provider)

**Queries**:
```sql
-- Top providers by satisfaction
SELECT provider_name, patient_satisfaction_score 
FROM provider_performance 
ORDER BY patient_satisfaction_score DESC LIMIT 10;

-- Providers below average
SELECT provider_name, patient_satisfaction_score 
FROM provider_performance 
WHERE patient_satisfaction_score < 4.0;

-- Average metrics across network
SELECT 
    AVG(patient_satisfaction_score) as avg_satisfaction,
    AVG(quality_score) as avg_quality,
    AVG(patient_retention_rate) as avg_retention
FROM provider_performance;

-- No-show issues
SELECT provider_name, appointment_no_show_rate 
FROM provider_performance 
WHERE appointment_no_show_rate > 0.15;
```

---

### 5. hedis_metrics
**Purpose**: HEDIS quality measure compliance tracking

| Column | Type | Description |
|--------|------|-------------|
| hedis_id | TEXT (PK) | Unique identifier |
| provider_id | TEXT (FK) | Reference to providers.provider_id |
| measure_name | TEXT | Quality measure (e.g., "HbA1c Testing") |
| performance_rate | REAL | % compliance (0-100) |
| target_rate | REAL | Target % (usually 85) |
| status | TEXT | Met/Not Met |
| trend | TEXT | Up/Down/Stable |
| description | TEXT | Measure description |

**Sample Data**: 750 records

**Queries**:
```sql
-- Average compliance
SELECT AVG(performance_rate) as avg_compliance FROM hedis_metrics;

-- Measures at target (85%+)
SELECT COUNT(*) FROM hedis_metrics WHERE performance_rate >= 85;

-- Below-target measures
SELECT measure_name, AVG(performance_rate) 
FROM hedis_metrics 
WHERE performance_rate < 85
GROUP BY measure_name;

-- Measures with upward trend
SELECT * FROM hedis_metrics WHERE trend = 'Up';

-- Provider-specific HEDIS
SELECT measure_name, performance_rate 
FROM hedis_metrics 
WHERE provider_id = 'PROV001'
ORDER BY performance_rate DESC;
```

---

### 6. clinical_quality
**Purpose**: Clinical quality outcomes and readmissions

| Column | Type | Description |
|--------|------|-------------|
| quality_id | TEXT (PK) | Unique identifier |
| patient_id | TEXT (FK) | Reference to patients.patient_id |
| provider_id | TEXT (FK) | Reference to providers.provider_id |
| readmission_30day | BOOLEAN | Readmitted within 30 days |
| medication_adherence_rate | REAL | % medications taken as prescribed |
| diabetes_control_rate | REAL | % with controlled diabetes |
| hypertension_control_rate | REAL | % with controlled BP |
| quality_score | INTEGER | 0-100 |
| comorbidities | INTEGER | Number of chronic conditions |

**Sample Data**: 5,000 records

**Queries**:
```sql
-- Readmission rate
SELECT 
    COUNT(CASE WHEN readmission_30day = 1 THEN 1 END) * 100.0 / COUNT(*) as readmission_rate
FROM clinical_quality;

-- Diabetes control rate
SELECT AVG(diabetes_control_rate) FROM clinical_quality;

-- High-comorbidity patients
SELECT patient_id, comorbidities 
FROM clinical_quality 
WHERE comorbidities > 3;

-- Quality scores distribution
SELECT 
    CASE 
        WHEN quality_score >= 80 THEN 'Excellent'
        WHEN quality_score >= 60 THEN 'Good'
        ELSE 'Needs Improvement'
    END as quality_level,
    COUNT(*) as count
FROM clinical_quality
GROUP BY quality_level;

-- Providers with high readmission rates
SELECT provider_id, 
    COUNT(CASE WHEN readmission_30day = 1 THEN 1 END) * 100.0 / COUNT(*) as readmission_rate
FROM clinical_quality
GROUP BY provider_id
HAVING readmission_rate > 20;
```

---

### 7. encounters
**Purpose**: Patient visit/encounter records

| Column | Type | Description |
|--------|------|-------------|
| encounter_id | TEXT (PK) | Unique identifier |
| patient_id | TEXT (FK) | Reference to patients.patient_id |
| provider_id | TEXT (FK) | Reference to providers.provider_id |
| encounter_date | DATE | Date of visit |
| encounter_type | TEXT | Office Visit/Telehealth/ER |
| diagnosis_code | TEXT | ICD-10 code |
| procedure_code | TEXT | CPT code |
| charges | REAL | Cost of visit |

**Sample Data**: 10,456 encounters

**Queries**:
```sql
-- Encounters by type
SELECT encounter_type, COUNT(*) FROM encounters GROUP BY encounter_type;

-- Total charges
SELECT SUM(charges) as total_revenue FROM encounters;

-- Average encounter cost
SELECT AVG(charges) as avg_cost FROM encounters;

-- Patient visit history
SELECT encounter_date, encounter_type, charges 
FROM encounters 
WHERE patient_id = 'P001'
ORDER BY encounter_date DESC;

-- Provider visit volume
SELECT provider_id, COUNT(*) as visits
FROM encounters
GROUP BY provider_id
ORDER BY visits DESC;

-- ER visits (potential readmissions)
SELECT COUNT(*) as er_visits FROM encounters WHERE encounter_type = 'ER';
```

---

## Data Relationships

```
patients
    ├── gaps_in_care (patient_id FK)
    ├── clinical_quality (patient_id FK)
    └── encounters (patient_id FK)

providers
    ├── provider_performance (provider_id FK)
    ├── hedis_metrics (provider_id FK)
    └── encounters (provider_id FK)
    └── clinical_quality (provider_id FK)
```

---

## Data Dictionary

### Priority Levels
- **High**: Critical/Health-threatening gaps
- **Medium**: Important but not urgent
- **Low**: Routine/Preventive

### Gap Status
- **open**: Not yet closed/filled
- **closed**: Successfully resolved

### Screening Types
- Diabetes Screening (HbA1c)
- Blood Pressure Check (CBP)
- Cholesterol Test (LDL-C)
- Breast Cancer Screening
- Cervical Cancer Screening
- Colorectal Cancer Screening
- Preventive Care Visit
- Immunizations

### Risk Scores
- 1.0-1.75: Low Risk
- 1.75-3.5: Medium Risk
- 3.5-5.0: High Risk

### Provider Types
- PCP: Primary Care Physician
- Specialist: Medical/Surgical specialist

### Encounter Types
- Office Visit: In-person clinic visit
- Telehealth: Virtual visit
- ER: Emergency room visit

---

## Database Size

**Typical Installation:**
```
patients:           5,000 rows
gaps_in_care:       1,200 rows
providers:          150 rows
provider_performance: 150 rows
hedis_metrics:      750 rows
clinical_quality:   5,000 rows
encounters:         10,456 rows
─────────────────────────────
TOTAL:              ~23,000 rows
```

**File Size**: ~3-5 MB

---

## Backup & Recovery

### Backup Database
```bash
# Windows
copy database\healthcare_dashboard.db database\healthcare_dashboard_backup.db

# macOS/Linux
cp database/healthcare_dashboard.db database/healthcare_dashboard_backup.db
```

### Restore from Backup
```bash
# Windows
copy database\healthcare_dashboard_backup.db database\healthcare_dashboard.db

# macOS/Linux
cp database/healthcare_dashboard_backup.db database/healthcare_dashboard.db
```

### Reset Database
```bash
# Delete database
del database\healthcare_dashboard.db

# Recreate
python backend/init_database.py
python backend/generate_realistic_data.py
```

---

## Performance Tips

### Indexes (If Using Real Data)
```sql
CREATE INDEX idx_patient_id ON gaps_in_care(patient_id);
CREATE INDEX idx_provider_id ON hedis_metrics(provider_id);
CREATE INDEX idx_encounter_type ON encounters(encounter_type);
```

### Query Optimization
```sql
-- ✅ GOOD: Use indexes
SELECT * FROM gaps_in_care WHERE patient_id = 'P001';

-- ❌ SLOW: Full table scan
SELECT * FROM gaps_in_care WHERE days_overdue > 10;
```

---

## Export Data

### Export to CSV
```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('database/healthcare_dashboard.db')
df = pd.read_sql("SELECT * FROM patients", conn)
df.to_csv('patients_export.csv', index=False)
```

### Export All Tables
```bash
# Use SQLite CLI
sqlite3 database/healthcare_dashboard.db

# Then in SQLite:
.headers on
.mode csv
.output patients.csv
SELECT * FROM patients;

# Repeat for other tables
```

---

## Troubleshooting

### Database Locked
```bash
# Usually resolves on restart of Streamlit
streamlit run frontend/streamlit_app_production.py
```

### Corrupted Database
```bash
# Delete and recreate
rm database/healthcare_dashboard.db
python backend/init_database.py
python backend/generate_realistic_data.py
```

### Wrong Data
```bash
# Regenerate sample data
python backend/generate_realistic_data.py
```

---

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQL Tutorial](https://www.w3schools.com/sql/)
- [Database Design Best Practices](https://en.wikipedia.org/wiki/Database_design)