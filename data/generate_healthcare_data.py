"""
Healthcare Dashboard Data Generation Script
Generates realistic synthetic data for HEDIS metrics, Gaps in Care, Provider Performance, and Clinical Quality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class HealthcareDataGenerator:
    def __init__(self, num_patients=5000, num_providers=150):
        self.num_patients = num_patients
        self.num_providers = num_providers
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        
    def generate_patients(self):
        """Generate patient data with demographics and conditions"""
        patient_ids = [f"PAT{i:06d}" for i in range(1, self.num_patients + 1)]
        
        # Age distribution: realistic healthcare population
        ages = np.random.gamma(shape=8, scale=6, size=self.num_patients)
        ages = np.clip(ages, 18, 95).astype(int)
        
        # Gender distribution
        genders = np.random.choice(['M', 'F'], self.num_patients, p=[0.48, 0.52])
        
        # Chronic conditions prevalence
        conditions = []
        for age in ages:
            patient_conditions = []
            # Diabetes prevalence increases with age
            if random.random() < (age / 100 * 0.30):
                patient_conditions.append('Diabetes')
            # Hypertension
            if random.random() < (age / 100 * 0.35):
                patient_conditions.append('Hypertension')
            # Asthma
            if random.random() < 0.08:
                patient_conditions.append('Asthma')
            # Heart Disease
            if random.random() < (age / 100 * 0.15):
                patient_conditions.append('Heart Disease')
            # COPD
            if random.random() < (age / 100 * 0.08):
                patient_conditions.append('COPD')
            
            conditions.append('|'.join(patient_conditions) if patient_conditions else 'None')
        
        # Insurance types
        insurance = np.random.choice(
            ['Medicare', 'Medicaid', 'Commercial', 'Uninsured'],
            self.num_patients,
            p=[0.35, 0.25, 0.35, 0.05]
        )
        
        patients_df = pd.DataFrame({
            'patient_id': patient_ids,
            'age': ages,
            'gender': genders,
            'chronic_conditions': conditions,
            'insurance_type': insurance,
            'enrollment_date': [self.start_date + timedelta(days=random.randint(0, 730)) 
                               for _ in range(self.num_patients)],
            'active': np.random.choice([True, False], self.num_patients, p=[0.92, 0.08])
        })
        
        return patients_df
    
    def generate_providers(self):
        """Generate provider data"""
        provider_ids = [f"PROV{i:05d}" for i in range(1, self.num_providers + 1)]
        
        specialties = ['Primary Care', 'Cardiology', 'Endocrinology', 'Pulmonology', 
                      'Nephrology', 'Psychiatry', 'Orthopedics', 'Dermatology']
        
        providers_df = pd.DataFrame({
            'provider_id': provider_ids,
            'provider_name': [f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Rodriguez'])} {random.choice(['A', 'B', 'C'])}" 
                             for _ in range(self.num_providers)],
            'specialty': np.random.choice(specialties, self.num_providers),
            'network': np.random.choice(['Network A', 'Network B', 'Network C'], self.num_providers),
            'years_experience': np.random.randint(2, 35, self.num_providers),
            'accepts_medicaid': np.random.choice([True, False], self.num_providers, p=[0.85, 0.15]),
            'accepts_medicare': np.random.choice([True, False], self.num_providers, p=[0.90, 0.10])
        })
        
        return providers_df
    
    def generate_encounters(self, patients_df, providers_df):
        """Generate healthcare encounters (visits)"""
        encounters = []
        
        for idx, patient in patients_df.iterrows():
            # Active patients have 2-15 encounters in the year; inactive have 0-2
            if patient['active']:
                num_encounters = np.random.poisson(5)  # Average 5 encounters/year
            else:
                num_encounters = np.random.randint(0, 2)
            
            for _ in range(num_encounters):
                encounter_date = self.start_date + timedelta(days=random.randint(0, 730))
                
                encounters.append({
                    'encounter_id': f"ENC{random.randint(100000, 999999)}",
                    'patient_id': patient['patient_id'],
                    'provider_id': random.choice(providers_df['provider_id'].values),
                    'encounter_date': encounter_date,
                    'encounter_type': np.random.choice(['Office Visit', 'Telehealth', 'ER', 'Inpatient'], 
                                                       p=[0.60, 0.20, 0.10, 0.10]),
                    'icd10_code': np.random.choice(['E11.9', 'I10', 'J45.9', 'I50.9', 'J44.9'], p=[0.25, 0.25, 0.15, 0.20, 0.15]),
                    'diagnosis': np.random.choice(['Diabetes Type 2', 'Hypertension', 'Asthma', 'Heart Failure', 'COPD']),
                    'procedures': random.randint(0, 3),
                    'medications_prescribed': random.randint(1, 8),
                    'visit_duration_minutes': random.randint(10, 90)
                })
        
        return pd.DataFrame(encounters)
    
    def generate_gaps_in_care(self, patients_df, providers_df):
        """Generate Gaps in Care metrics"""
        gaps = []
        
        screening_types = ['Diabetes Screening', 'Blood Pressure Check', 'Cholesterol Screening', 
                          'Cancer Screening', 'Preventive Care Visit', 'Vaccinations']
        
        for patient in patients_df.sample(min(3000, len(patients_df))).iterrows():
            for screening in screening_types:
                # Probability of gap increases for certain demographics
                age = patient[1]['age']
                gap_probability = 0.15 + (age / 100 * 0.20)
                gap_probability = min(gap_probability, 0.60)
                
                gaps.append({
                    'gap_id': f"GAP{random.randint(100000, 999999)}",
                    'patient_id': patient[1]['patient_id'],
                    'screening_type': screening,
                    'is_gap': random.random() < gap_probability,
                    'days_overdue': random.randint(0, 365) if random.random() < gap_probability else 0,
                    'priority': np.random.choice(['High', 'Medium', 'Low'], p=[0.20, 0.50, 0.30]),
                    'last_completed_date': self.start_date + timedelta(days=random.randint(-730, 0)),
                    'target_completion_date': self.start_date + timedelta(days=random.randint(0, 180))
                })
        
        return pd.DataFrame(gaps)
    
    def generate_hedis_metrics(self, patients_df, providers_df):
        """Generate HEDIS (Healthcare Effectiveness Data and Information Set) metrics"""
        hedis_metrics = []
        
        hedis_measures = {
            'Diabetes Care - Eye Exam': {'numerator_threshold': 0.45, 'target': 0.85},
            'Diabetes Care - Kidney Check': {'numerator_threshold': 0.40, 'target': 0.85},
            'Diabetes Care - HbA1c Control': {'numerator_threshold': 0.35, 'target': 0.80},
            'High Blood Pressure Controlled': {'numerator_threshold': 0.38, 'target': 0.80},
            'Antidepressant Medication Adherence': {'numerator_threshold': 0.42, 'target': 0.80},
            'Asthma Medication Ratio': {'numerator_threshold': 0.40, 'target': 0.80},
            'Annual Dental Visit': {'numerator_threshold': 0.35, 'target': 0.75}
        }
        
        for measure, targets in hedis_measures.items():
            for provider in providers_df.sample(min(50, len(providers_df))).iterrows():
                # Generate realistic performance
                numerator = random.randint(80, 450)  # Eligible members with measure met
                denominator = random.randint(500, 1000)  # Total eligible members
                rate = (numerator / denominator) * 100
                
                hedis_metrics.append({
                    'hedis_id': f"HEDIS{random.randint(100000, 999999)}",
                    'measure_name': measure,
                    'provider_id': provider[1]['provider_id'],
                    'numerator': numerator,
                    'denominator': denominator,
                    'performance_rate': round(rate, 2),
                    'target_rate': targets['target'] * 100,
                    'benchmark_rate': 75.5,
                    'measurement_year': 2024,
                    'status': 'Met' if rate >= targets['target'] * 100 else 'Not Met',
                    'trend': np.random.choice(['Improving', 'Stable', 'Declining'], p=[0.40, 0.40, 0.20])
                })
        
        return pd.DataFrame(hedis_metrics)
    
    def generate_provider_performance(self, providers_df, encounters_df):
        """Generate Provider Performance metrics"""
        performance = []
        
        for provider in providers_df.iterrows():
            provider_encounters = encounters_df[encounters_df['provider_id'] == provider[1]['provider_id']]
            num_patients = len(provider_encounters['patient_id'].unique())
            total_visits = len(provider_encounters)
            
            performance.append({
                'performance_id': f"PERF{random.randint(100000, 999999)}",
                'provider_id': provider[1]['provider_id'],
                'provider_name': provider[1]['provider_name'],
                'total_patients': num_patients,
                'total_encounters': total_visits,
                'patient_satisfaction_score': round(random.uniform(3.5, 5.0), 2),
                'average_visit_duration': round(np.random.normal(35, 10), 1),
                'appointment_no_show_rate': round(random.uniform(0.05, 0.25), 3),
                'referral_rate': round(random.uniform(0.10, 0.40), 3),
                'avg_procedures_per_visit': round(random.uniform(0.5, 2.5), 2),
                'prescribing_efficiency': round(random.uniform(0.60, 0.95), 2),
                'patient_retention_rate': round(random.uniform(0.70, 0.98), 3),
                'quality_score': round(random.uniform(60, 100), 1),
                'measurement_period': '2024'
            })
        
        return pd.DataFrame(performance)
    
    def generate_clinical_quality(self, patients_df):
        """Generate Clinical Quality metrics"""
        quality = []
        
        for patient in patients_df.sample(min(2000, len(patients_df))).iterrows():
            age = patient[1]['age']
            conditions = patient[1]['chronic_conditions']
            
            # Risk factors based on age and conditions
            risk_score = min(100, age * 0.5 + random.uniform(0, 30))
            
            quality.append({
                'quality_id': f"QUAL{random.randint(100000, 999999)}",
                'patient_id': patient[1]['patient_id'],
                'readmission_30day': random.random() < (risk_score / 1000),
                'readmission_days': random.randint(1, 30) if random.random() < (risk_score / 1000) else None,
                'hospital_acquired_infection': random.random() < 0.02,
                'medication_adherence': round(random.uniform(0.50, 1.0), 2),
                'care_coordination_score': round(random.uniform(0, 100), 1),
                'patient_safety_incidents': random.randint(0, 2),
                'clinical_outcome_score': round(random.uniform(60, 100), 1),
                'complication_rate': round(random.uniform(0.0, 0.15), 3),
                'measurement_date': self.start_date + timedelta(days=random.randint(0, 730))
            })
        
        return pd.DataFrame(quality)
    
    def generate_all_data(self):
        """Generate all datasets"""
        print("Generating patient data...")
        patients = self.generate_patients()
        
        print("Generating provider data...")
        providers = self.generate_providers()
        
        print("Generating encounters...")
        encounters = self.generate_encounters(patients, providers)
        
        print("Generating Gaps in Care...")
        gaps = self.generate_gaps_in_care(patients, providers)
        
        print("Generating HEDIS metrics...")
        hedis = self.generate_hedis_metrics(patients, providers)
        
        print("Generating Provider Performance...")
        performance = self.generate_provider_performance(providers, encounters)
        
        print("Generating Clinical Quality metrics...")
        quality = self.generate_clinical_quality(patients)
        
        return {
            'patients': patients,
            'providers': providers,
            'encounters': encounters,
            'gaps_in_care': gaps,
            'hedis_metrics': hedis,
            'provider_performance': performance,
            'clinical_quality': quality
        }
    
    def save_to_csv(self, data, output_dir='data'):
        """Save all datasets to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in data.items():
            filepath = os.path.join(output_dir, f"{name}.csv")
            df.to_csv(filepath, index=False)
            print(f"✓ Saved {name}.csv ({len(df)} rows)")
        
        return output_dir

if __name__ == "__main__":
    print("=" * 60)
    print("Healthcare Dashboard Data Generator")
    print("=" * 60)
    
    generator = HealthcareDataGenerator(num_patients=5000, num_providers=150)
    data = generator.generate_all_data()
    
    print("\n" + "=" * 60)
    print("Saving to CSV files...")
    print("=" * 60)
    
    output_dir = generator.save_to_csv(data)
    
    print("\n" + "=" * 60)
    print("Data Generation Complete!")
    print("=" * 60)
    print(f"\nDataset Summary:")
    for name, df in data.items():
        print(f"  {name}: {len(df)} records")
    print(f"\nOutput directory: {output_dir}/")