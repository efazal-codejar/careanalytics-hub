"""
Database Initialization Script
Creates SQLite database and loads healthcare data
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

DATABASE_PATH = "healthcare_dashboard.db"

def create_tables():
    """Create database tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        age INTEGER,
        gender TEXT,
        chronic_conditions TEXT,
        insurance_type TEXT,
        enrollment_date TEXT,
        active BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Providers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        provider_id TEXT PRIMARY KEY,
        provider_name TEXT,
        specialty TEXT,
        network TEXT,
        years_experience INTEGER,
        accepts_medicaid BOOLEAN,
        accepts_medicare BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Encounters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS encounters (
        encounter_id TEXT PRIMARY KEY,
        patient_id TEXT,
        provider_id TEXT,
        encounter_date TEXT,
        encounter_type TEXT,
        icd10_code TEXT,
        diagnosis TEXT,
        procedures INTEGER,
        medications_prescribed INTEGER,
        visit_duration_minutes INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
    )
    """)
    
    # Gaps in Care table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gaps_in_care (
        gap_id TEXT PRIMARY KEY,
        patient_id TEXT,
        screening_type TEXT,
        is_gap BOOLEAN,
        days_overdue INTEGER,
        priority TEXT,
        last_completed_date TEXT,
        target_completion_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )
    """)
    
    # HEDIS Metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hedis_metrics (
        hedis_id TEXT PRIMARY KEY,
        measure_name TEXT,
        provider_id TEXT,
        numerator INTEGER,
        denominator INTEGER,
        performance_rate REAL,
        target_rate REAL,
        benchmark_rate REAL,
        measurement_year INTEGER,
        status TEXT,
        trend TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
    )
    """)
    
    # Provider Performance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS provider_performance (
        performance_id TEXT PRIMARY KEY,
        provider_id TEXT,
        provider_name TEXT,
        total_patients INTEGER,
        total_encounters INTEGER,
        patient_satisfaction_score REAL,
        average_visit_duration REAL,
        appointment_no_show_rate REAL,
        referral_rate REAL,
        avg_procedures_per_visit REAL,
        prescribing_efficiency REAL,
        patient_retention_rate REAL,
        quality_score REAL,
        measurement_period TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
    )
    """)
    
    # Clinical Quality table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clinical_quality (
        quality_id TEXT PRIMARY KEY,
        patient_id TEXT,
        readmission_30day BOOLEAN,
        readmission_days INTEGER,
        hospital_acquired_infection BOOLEAN,
        medication_adherence REAL,
        care_coordination_score REAL,
        patient_safety_incidents INTEGER,
        clinical_outcome_score REAL,
        complication_rate REAL,
        measurement_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Database tables created successfully")

def load_data(data_dir="data"):
    """Load CSV data into database"""
    if not os.path.exists(data_dir):
        print(f"✗ Data directory '{data_dir}' not found")
        return False
    
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Define file to table mapping
    file_table_map = {
        'patients.csv': 'patients',
        'providers.csv': 'providers',
        'encounters.csv': 'encounters',
        'gaps_in_care.csv': 'gaps_in_care',
        'hedis_metrics.csv': 'hedis_metrics',
        'provider_performance.csv': 'provider_performance',
        'clinical_quality.csv': 'clinical_quality'
    }
    
    loaded_count = 0
    
    for filename, table_name in file_table_map.items():
        filepath = os.path.join(data_dir, filename)
        
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                df.to_sql(table_name, conn, if_exists='append', index=False)
                print(f"✓ Loaded {filename} ({len(df)} records)")
                loaded_count += 1
            except Exception as e:
                print(f"✗ Error loading {filename}: {str(e)}")
        else:
            print(f"⚠ File not found: {filename}")
    
    conn.close()
    return loaded_count > 0

def create_indexes():
    """Create indexes for better query performance"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_patient_active ON patients(active)",
        "CREATE INDEX IF NOT EXISTS idx_encounter_patient ON encounters(patient_id)",
        "CREATE INDEX IF NOT EXISTS idx_encounter_provider ON encounters(provider_id)",
        "CREATE INDEX IF NOT EXISTS idx_encounter_date ON encounters(encounter_date)",
        "CREATE INDEX IF NOT EXISTS idx_gap_priority ON gaps_in_care(priority)",
        "CREATE INDEX IF NOT EXISTS idx_hedis_status ON hedis_metrics(status)",
        "CREATE INDEX IF NOT EXISTS idx_hedis_provider ON hedis_metrics(provider_id)",
        "CREATE INDEX IF NOT EXISTS idx_quality_readmission ON clinical_quality(readmission_30day)",
        "CREATE INDEX IF NOT EXISTS idx_provider_quality ON provider_performance(quality_score)"
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except Exception as e:
            print(f"Warning: Could not create index: {str(e)}")
    
    conn.commit()
    conn.close()
    print("✓ Indexes created successfully")

def verify_data():
    """Verify data was loaded correctly"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    tables = [
        'patients', 'providers', 'encounters', 'gaps_in_care',
        'hedis_metrics', 'provider_performance', 'clinical_quality'
    ]
    
    print("\n" + "="*60)
    print("Data Verification")
    print("="*60)
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
        except Exception as e:
            print(f"{table}: ERROR - {str(e)}")
    
    conn.close()

def main():
    """Main initialization function"""
    print("\n" + "="*60)
    print("Healthcare Dashboard Database Initialization")
    print("="*60)
    
    # Remove existing database for fresh start
    if os.path.exists(DATABASE_PATH):
        response = input(f"\n{DATABASE_PATH} already exists. Recreate? (y/n): ")
        if response.lower() != 'y':
            print("Initialization cancelled.")
            return
        os.remove(DATABASE_PATH)
        print(f"✓ Removed existing database")
    
    # Create tables
    print("\nCreating tables...")
    create_tables()
    
    # Load data
    print("\nLoading data from CSV files...")
    success = load_data()
    
    if success:
        # Create indexes
        print("\nCreating indexes...")
        create_indexes()
        
        # Verify
        verify_data()
        
        print("\n" + "="*60)
        print("✓ Database initialization completed successfully!")
        print("="*60)
    else:
        print("\n⚠ No data files found. Please run generate_healthcare_data.py first.")
        print("Usage: python generate_healthcare_data.py")

if __name__ == "__main__":
    main()