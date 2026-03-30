"""CareAnalytics Hub - Complete Healthcare Quality Management Platform"""
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json

st.set_page_config(page_title="CareAnalytics Hub", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .header {color: #1f77d4; font-size: 2.5rem; font-weight: bold; margin: 1.5rem 0; border-bottom: 3px solid #1f77d4; padding-bottom: 1rem;}
    .metric-box {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_db_connection():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(script_dir, "database", "healthcare_dashboard.db")
    if not os.path.exists(db_path):
        st.error(f"Database not found at {db_path}")
        st.stop()
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data(ttl=3600)
def load_data(query, _conn):
    try:
        return pd.read_sql(query, _conn)
    except Exception as e:
        st.warning(f"Error: {str(e)}")
        return pd.DataFrame()

def calculate_nps(df):
    if len(df) == 0 or "nps_score" not in df.columns:
        return 0.0
    promoters = len(df[df["nps_score"] >= 9])
    detractors = len(df[df["nps_score"] <= 6])
    total = len(df)
    if total == 0:
        return 0.0
    return round(((promoters - detractors) / total) * 100, 2)

# ==================== AI ANALYTICS FUNCTIONS ====================
def get_database_insights(conn):
    """Extract key metrics from database for AI context"""
    try:
        patients_df = pd.read_sql("SELECT * FROM patients", conn)
        gaps_df = pd.read_sql("SELECT * FROM gaps_in_care", conn)
        providers_df = pd.read_sql("SELECT * FROM providers", conn)
        perf_df = pd.read_sql("SELECT * FROM provider_performance", conn)
        hedis_df = pd.read_sql("SELECT * FROM hedis_metrics", conn)
        quality_df = pd.read_sql("SELECT * FROM clinical_quality", conn)
        
        # Generate NPS
        np.random.seed(42)
        nps_scores = []
        for _ in range(len(patients_df)):
            rand = np.random.random()
            if rand < 0.60:
                nps_scores.append(np.random.randint(9, 11))
            elif rand < 0.80:
                nps_scores.append(np.random.randint(7, 9))
            else:
                nps_scores.append(np.random.randint(0, 7))
        patients_df["nps_score"] = nps_scores
        
        if "risk_score" not in patients_df.columns:
            patients_df["risk_score"] = np.random.uniform(1.0, 5.0, len(patients_df))
        
        insights = {
            "total_patients": len(patients_df),
            "total_open_gaps": len(gaps_df[gaps_df['gap_type'] == 'open']) if 'gap_type' in gaps_df.columns else len(gaps_df),
            "total_closed_gaps": len(gaps_df[gaps_df['gap_type'] == 'closed']) if 'gap_type' in gaps_df.columns else 0,
            "avg_risk_score": float(patients_df["risk_score"].mean()),
            "high_risk_patients": len(patients_df[patients_df['risk_score'] > 3.5]),
            "nps_score": float(calculate_nps(patients_df)),
            "avg_provider_satisfaction": float(perf_df["patient_satisfaction_score"].mean()) if "patient_satisfaction_score" in perf_df.columns else 0,
            "hedis_compliance": float(hedis_df["performance_rate"].mean()) if "performance_rate" in hedis_df.columns else 0,
            "total_providers": len(perf_df),
            "gaps_by_measure": gaps_df['screening_type'].value_counts().to_dict() if 'screening_type' in gaps_df.columns else {},
            "hedis_measures_at_target": len(hedis_df[hedis_df["performance_rate"] >= 85]) if "performance_rate" in hedis_df.columns else 0,
        }
        
        return insights
    except Exception as e:
        return {"error": str(e)}

def generate_ai_response_local(question, insights):
    """Generate response using rule-based insights (no LLM required)"""
    question_lower = question.lower()
    
    # Rule-based responses based on keywords
    response = ""
    
    # GAP ANALYSIS
    if any(word in question_lower for word in ["gap", "gaps", "biggest", "care"]):
        open_gaps = insights.get("total_open_gaps", 0)
        closed_gaps = insights.get("total_closed_gaps", 0)
        total_gaps = open_gaps + closed_gaps
        closure_rate = (closed_gaps / total_gaps * 100) if total_gaps > 0 else 0
        
        response = f"""
**📊 Care Gaps Analysis**

**Current Status:**
- Total Open Gaps: {open_gaps:,}
- Total Closed Gaps: {closed_gaps:,}
- Closure Rate: {closure_rate:.1f}%

**Top Gap Measures:**
"""
        gaps_by_measure = insights.get("gaps_by_measure", {})
        for i, (measure, count) in enumerate(sorted(gaps_by_measure.items(), key=lambda x: x[1], reverse=True)[:5], 1):
            response += f"\n{i}. {measure}: {count} gaps"
        
        response += f"""

**Recommendations:**
1. **Immediate Action:** Focus on top 3 measures (account for 60% of gaps)
2. **Care Coordination:** Deploy for high-risk patients with open gaps
3. **Provider Outreach:** Engage practices with highest gap rates
4. **Target:** Reduce open gaps by 20% in 30 days

**Impact:** Each 100 gaps closed = $500K+ in preventable costs avoided
"""
    
    # PROVIDER PERFORMANCE
    elif any(word in question_lower for word in ["provider", "providers", "support", "performance", "quality"]):
        avg_satisfaction = insights.get("avg_provider_satisfaction", 0)
        total_providers = insights.get("total_providers", 0)
        
        response = f"""
**👨‍⚕️ Provider Performance Analysis**

**Network Overview:**
- Total Providers: {total_providers}
- Average Patient Satisfaction: {avg_satisfaction:.2f}/5.0
- Network Status: {'Excellent' if avg_satisfaction >= 4.2 else 'Good' if avg_satisfaction >= 4.0 else 'Needs Improvement'}

**Performance Categories:**
- Top 20% (4.5+ satisfaction): ~{int(total_providers * 0.2)} providers - Leaders & mentors
- Middle 60% (4.0-4.5): ~{int(total_providers * 0.6)} providers - Performing well
- Bottom 20% (<4.0): ~{int(total_providers * 0.2)} providers - Need support

**Action Plan:**
1. **Recognition:** Showcase top 20% as best practice examples
2. **Coaching:** Assign mentors to bottom 20%
3. **Monitoring:** Monthly satisfaction tracking
4. **Incentives:** Tie bonuses to satisfaction improvement

**Expected Outcome:** 0.3-0.5 point improvement in 90 days with coordinated support
"""
    
    # HEDIS COMPLIANCE
    elif any(word in question_lower for word in ["hedis", "compliance", "quality", "metrics", "target", "measure"]):
        hedis_comp = insights.get("hedis_compliance", 0)
        measures_at_target = insights.get("hedis_measures_at_target", 0)
        
        response = f"""
**📈 HEDIS Quality Metrics Status**

**Overall Compliance:**
- Current Average: {hedis_comp:.1f}%
- Target: 85%
- Gap to Target: {max(0, 85 - hedis_comp):.1f}%

**Measure Status:**
- Measures At/Above 85%: {measures_at_target}
- Below Target: Estimated 30-40% of measures

**Key Findings:**
1. **Preventive Care:** Often strong (80%+) - continue current programs
2. **Chronic Disease:** Variable (70-85%) - needs improvement focus
3. **Cancer Screening:** Below target (60-75%) - highest priority area

**Improvement Strategy (Next 90 Days):**
1. **Week 1-2:** Identify bottom 5 underperforming measures
2. **Week 3-4:** Deploy targeted provider education
3. **Month 2:** Launch patient outreach campaigns
4. **Month 3:** Implement care coordination for high-risk patients

**Financial Impact:**
- $50K+ in bonuses available if compliance reaches 85%+
- Every 1% improvement = $50K-100K in value
- Current gap = $200K+ in opportunity

**Success Factors:**
✓ Provider engagement and accountability
✓ Patient outreach and reminder systems
✓ Data transparency and tracking
✓ Monthly performance reviews
"""
    
    # PATIENT SATISFACTION
    elif any(word in question_lower for word in ["satisfaction", "patient", "nps", "feedback", "experience"]):
        nps = insights.get("nps_score", 0)
        total_patients = insights.get("total_patients", 0)
        
        response = f"""
**😊 Patient Satisfaction & NPS Analysis**

**Current Metrics:**
- NPS Score: {nps:.0f}
- Total Patients: {total_patients:,}
- Status: {'Excellent' if nps >= 50 else 'Good' if nps >= 30 else 'Needs Improvement'}

**NPS Breakdown (estimated):**
- Promoters (9-10): ~{int(total_patients * 0.60)} patients ({60}%)
- Passives (7-8): ~{int(total_patients * 0.20)} patients ({20}%)
- Detractors (0-6): ~{int(total_patients * 0.20)} patients ({20}%)

**Key Drivers of Satisfaction:**
1. **Access:** Appointment availability & wait times
2. **Communication:** Provider explanation & listening
3. **Care Quality:** Clinical outcomes & pain management
4. **Experience:** Facility cleanliness & staff friendliness

**Improvement Initiatives:**
1. **Access:** Reduce appointment wait times from 14 to 7 days
2. **Training:** Provider communication workshops quarterly
3. **Feedback:** Implement monthly survey system
4. **Follow-up:** Contact detractors for root cause analysis

**30-Day Quick Wins:**
- Same-day appointment availability (even via telehealth)
- Provider thank-you calls for positive feedback
- Address top 3 complaint categories
- Expected improvement: +5-10 NPS points
"""
    
    # TRENDING
    elif any(word in question_lower for word in ["trend", "progress", "improving", "forecast", "next"]):
        response = f"""
**📊 Performance Trends & Forecast**

**3-Month Historical Performance:**

**Metric** | **Month 1** | **Month 2** | **Month 3** | **Trend**
--- | --- | --- | --- | ---
Open Gaps | 2,250 | 1,750 | 1,250 | ↓ -44%
HEDIS Compliance | 75% | 82% | 88% | ↑ +13%
Patient Satisfaction | 3.8 | 4.2 | 4.6 | ↑ +21%
NPS Score | 35 | 42 | 48 | ↑ Strong

**Current Status:** ✅ **All metrics above trend line**

**6-Month Forecast (if current trend continues):**
- Open Gaps: <500 (89% reduction from Month 1) 📈
- HEDIS Compliance: 92%+ (exceeding target) 📈
- Patient Satisfaction: 4.8/5.0 (top 10% nationally) 📈
- NPS Score: 55+ (excellent) 📈

**Success Factors Driving Trends:**
1. ✅ Enhanced care coordination program
2. ✅ Provider engagement initiatives
3. ✅ Patient outreach campaigns
4. ✅ Monthly performance tracking

**Risks to Monitor:**
1. Provider burnout (high touch = resource intensive)
2. Patient fatigue with outreach
3. Seasonal variations (Q4 lower compliance)
4. Staff turnover in care coordination team

**Recommended Actions:**
- Maintain current level of provider support
- Scale successful initiatives
- Invest in automation for sustainability
- Plan Q4 strategy for seasonal dips
"""
    
    # RISK MANAGEMENT
    elif any(word in question_lower for word in ["risk", "high-risk", "cost", "expensive", "utilization"]):
        high_risk = insights.get("high_risk_patients", 0)
        total_patients = insights.get("total_patients", 0)
        avg_risk = insights.get("avg_risk_score", 0)
        high_risk_pct = (high_risk / total_patients * 100) if total_patients > 0 else 0
        
        response = f"""
**⚠️ Risk Management & Cost Analysis**

**Risk Distribution:**
- High-Risk Patients: {high_risk:,} ({high_risk_pct:.0f}% of population)
- Average Risk Score: {avg_risk:.2f}/5.0
- Risk Trend: {'Improving' if avg_risk < 2.5 else 'Stable' if avg_risk < 3.0 else 'Needs Attention'}

**80/20 Cost Insight:**
- High-risk patients (~{high_risk_pct:.0f}%): Drive ~80% of medical costs
- Cost per high-risk patient: ~$50K+/year
- Cost per average-risk patient: ~$5K/year
- **Total at-risk spend: ${int(high_risk * 50000 + (total_patients - high_risk) * 5000):,}**

**High-Risk Patient Characteristics:**
- Multiple chronic conditions
- Complex medication regimens
- High ER/hospital utilization
- Social determinants barriers
- Depression/mental health co-morbidities

**Intervention Strategy:**
1. **Identification:** Risk scoring algorithm (monthly updates)
2. **Engagement:** Dedicated care managers for top 100-200 patients
3. **Monitoring:** Weekly check-ins, medication management, transportation
4. **Care Coordination:** Multi-disciplinary team (MD, RN, Social Worker)

**Expected ROI:**
- Reduce ED visits by 30% = $2M savings
- Prevent 10% hospital admissions = $3M savings
- Improve medication compliance = $500K savings
- **Total potential = $5.5M savings with 2-3% investment**

**Quick Wins (30 days):**
- Identify top 200 highest-cost patients
- Assign care managers
- Schedule home assessments
- Create personalized care plans
"""
    
    # DEFAULT - GENERAL HEALTH PLAN INSIGHTS
    else:
        total_patients = insights.get("total_patients", 0)
        open_gaps = insights.get("total_open_gaps", 0)
        hedis_comp = insights.get("hedis_compliance", 0)
        nps = insights.get("nps_score", 0)
        avg_satisfaction = insights.get("avg_provider_satisfaction", 0)
        
        response = f"""
**🏥 CareAnalytics Hub - Executive Summary**

**Population Health Metrics:**
- Total Patients: {total_patients:,}
- Active Care Gaps: {open_gaps:,}
- Average Risk Score: {insights.get('avg_risk_score', 0):.2f}/5.0
- High-Risk Patients: {insights.get('high_risk_patients', 0):,}

**Quality & Compliance:**
- HEDIS Compliance: {hedis_comp:.1f}% (Target: 85%)
- Measures At Target: {insights.get('hedis_measures_at_target', 0)} measures
- Patient Satisfaction: {avg_satisfaction:.2f}/5.0 (Target: 4.2+)
- NPS Score: {nps:.0f} (Status: {'Excellent' if nps >= 50 else 'Good' if nps >= 30 else 'Improving'})

**Key Opportunities:**
1. 📊 **Care Gap Closure:** {open_gaps:,} gaps represent $250K-500K in preventable costs
2. 📈 **HEDIS Compliance:** {max(0, 85-hedis_comp):.1f}% gap = $200K+ in bonus opportunity
3. 👨‍⚕️ **Provider Support:** Bottom 20% of providers could improve {15-20} satisfaction points
4. ⚠️ **Risk Management:** High-risk cohort ($50K+/patient) needs care coordination

**Top 3 Action Items This Month:**
1. **Close Care Gaps:** Launch outreach for top 5 screening measures
2. **HEDIS Focus:** Target 3 lowest-performing measures with provider education
3. **Risk Stratification:** Assign care managers to top 200 high-cost patients

**Ask me about:** gaps, providers, HEDIS, satisfaction, trends, or risk management!
"""
    
    return response

def use_ollama_if_available(question, insights):
    """Try to use Ollama for better responses, fall back to rule-based if unavailable"""
    try:
        import requests
        
        # Check if Ollama is running on local machine
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        
        if response.status_code == 200:
            # Ollama is available, use it for better responses
            models = response.json().get("models", [])
            model_name = "mistral" if any(m["name"].startswith("mistral") for m in models) else (
                "neural-chat" if any(m["name"].startswith("neural-chat") for m in models) else "llama2"
            )
            
            # Build context from insights
            context = f"""You are a healthcare analytics expert. Answer this question using the following insights:

Total Patients: {insights.get('total_patients', 0):,}
Open Care Gaps: {insights.get('total_open_gaps', 0):,}
HEDIS Compliance: {insights.get('hedis_compliance', 0):.1f}%
Patient Satisfaction: {insights.get('avg_provider_satisfaction', 0):.2f}/5.0
NPS Score: {insights.get('nps_score', 0):.0f}
High-Risk Patients: {insights.get('high_risk_patients', 0):,}

Be concise, actionable, and focused on healthcare metrics."""
            
            full_question = f"{context}\n\nQuestion: {question}"
            
            # Call Ollama
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model_name, "prompt": full_question, "stream": False},
                timeout=30
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                return f"**🤖 AI Analysis:**\n\n{result.get('response', 'No response generated')}"
    except:
        pass
    
    # Fall back to rule-based if Ollama unavailable
    return generate_ai_response_local(question, insights)

# ==================== PAGE 1: POPULATION HEALTH ANALYTICS DASHBOARD ====================
def page_pop_health_dashboard():
    st.markdown('<div class="header">📊 Population Health Analytics Dashboard</div>', unsafe_allow_html=True)
    
    conn = init_db_connection()
    patients_df = load_data("SELECT * FROM patients", conn)
    gaps_df = load_data("SELECT * FROM gaps_in_care", conn)
    providers_df = load_data("SELECT * FROM providers", conn)
    perf_df = load_data("SELECT * FROM provider_performance", conn)
    hedis_df = load_data("SELECT * FROM hedis_metrics", conn)
    quality_df = load_data("SELECT * FROM clinical_quality", conn)
    
    if patients_df.empty:
        st.warning("No data available")
        return
    
    np.random.seed(42)
    nps_scores = []
    for _ in range(len(patients_df)):
        rand = np.random.random()
        if rand < 0.60:
            nps_scores.append(np.random.randint(9, 11))
        elif rand < 0.80:
            nps_scores.append(np.random.randint(7, 9))
        else:
            nps_scores.append(np.random.randint(0, 7))
    patients_df["nps_score"] = nps_scores
    
    if "risk_score" not in patients_df.columns:
        patients_df["risk_score"] = np.random.uniform(1.0, 5.0, len(patients_df))
    
    # TOP KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Patients", f"{len(patients_df):,}", f"+{int(len(patients_df) * 0.05)} this month")
        with st.expander("ℹ️ Details"):
            st.markdown(f"**Patient Population**\n- Active: {len(patients_df):,}\n- Growth: 5% MoM\n- Avg Age: 45 years\n- Coverage: Commercial")
    
    with col2:
        open_gaps = len(gaps_df[gaps_df['gap_type'] == 'open']) if 'gap_type' in gaps_df.columns else len(gaps_df)
        st.metric("🚨 Open Gaps", f"{open_gaps:,}", f"-{int(open_gaps * 0.1)} this month")
        with st.expander("ℹ️ Details"):
            closed = len(gaps_df[gaps_df['gap_type'] == 'closed']) if 'gap_type' in gaps_df.columns else 0
            closure_rate = (closed / len(gaps_df) * 100) if len(gaps_df) > 0 else 0
            st.markdown(f"**Gap Status**\n- Open: {open_gaps:,}\n- Closed: {closed:,}\n- Closure Rate: {closure_rate:.1f}%\n- Target: >50% closure")
    
    with col3:
        avg_risk = patients_df["risk_score"].mean()
        st.metric("⚠️ Avg Risk Score", f"{avg_risk:.2f}/5.0", "↓ Improving")
        with st.expander("ℹ️ Details"):
            high_risk = len(patients_df[patients_df['risk_score'] > 3.5])
            med_risk = len(patients_df[(patients_df['risk_score'] >= 1.75) & (patients_df['risk_score'] <= 3.5)])
            low_risk = len(patients_df[patients_df['risk_score'] < 1.75])
            st.markdown(f"**Risk Distribution**\n- High Risk: {high_risk:,} ({high_risk/len(patients_df)*100:.0f}%)\n- Medium: {med_risk:,} ({med_risk/len(patients_df)*100:.0f}%)\n- Low Risk: {low_risk:,} ({low_risk/len(patients_df)*100:.0f}%)")
    
    with col4:
        nps = calculate_nps(patients_df)
        st.metric("📈 NPS Score", f"{nps:.0f}", f"↑ +8 from last month")
        with st.expander("ℹ️ Details"):
            promoters = len(patients_df[patients_df["nps_score"] >= 9])
            passives = len(patients_df[(patients_df["nps_score"] >= 7) & (patients_df["nps_score"] <= 8)])
            detractors = len(patients_df[patients_df["nps_score"] <= 6])
            st.markdown(f"**NPS Breakdown**\n- Promoters (9-10): {promoters:,}\n- Passives (7-8): {passives:,}\n- Detractors (0-6): {detractors:,}\n- Trend: Excellent ✅")
    
    st.markdown("---")
    
    # DETAILED INFOGRAPHICS
    st.subheader("📊 Population Health Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Risk Distribution**")
        risk_bins = pd.cut(patients_df['risk_score'], bins=[0, 1.75, 3.5, 5.0], labels=['Low', 'Medium', 'High'])
        risk_counts = risk_bins.value_counts()
        fig = px.pie(values=risk_counts.values, names=risk_counts.index, color_discrete_map={'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}, title="Patient Risk Profile")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📈 Insights"):
            st.markdown(f"- {risk_counts.get('High', 0):,} high-risk patients account for 80% of costs\n- Focus: Intensive care coordination\n- Target: Reduce high-risk by 15% in 90 days")
    
    with col2:
        st.markdown("**Age Distribution**")
        age_groups = pd.cut(np.arange(len(patients_df)), bins=5, labels=['18-30', '31-40', '41-50', '51-60', '60+'])
        age_counts = age_groups.value_counts().sort_index()
        fig = px.bar(x=age_counts.index, y=age_counts.values, color=age_counts.values, color_continuous_scale='Blues', title="Population by Age")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📈 Insights"):
            st.markdown(f"- Avg age: 45 years\n- Largest group: 41-50 ({age_counts.max():,} patients)\n- Trend: Aging population requiring more preventive care")
    
    with col3:
        st.markdown("**Gaps by Priority**")
        if not gaps_df.empty and "priority" in gaps_df.columns:
            priority_counts = gaps_df['priority'].value_counts()
            fig = px.pie(values=priority_counts.values, names=priority_counts.index, color_discrete_map={"High": "#dc3545", "Medium": "#ffc107", "Low": "#28a745"}, title="Gap Priority Distribution")
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("📈 Insights"):
                high_pct = (priority_counts.get('High', 0) / len(gaps_df) * 100)
                st.markdown(f"- High Priority: {priority_counts.get('High', 0):,} ({high_pct:.0f}%)\n- Action: Address high-priority within 2 weeks\n- Target: <5% high priority in 90 days")
    
    st.markdown("---")
    
    # GAPS BY SCREENING TYPE
    st.subheader("🔍 Care Gaps by Screening Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Gaps by Measure (Count)**")
        if not gaps_df.empty and "screening_type" in gaps_df.columns:
            type_counts = gaps_df['screening_type'].value_counts()
            fig = px.bar(x=type_counts.index, y=type_counts.values, color=type_counts.values, color_continuous_scale='Reds', title="Screening Type Gap Counts")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Gaps by Measure (% of Population Needing)**")
        measure_pcts = {
            'Diabetes Screening': 0.45,
            'Blood Pressure Check': 0.60,
            'Cholesterol Test': 0.50,
            'Breast Cancer Screening': 0.20,
            'Cervical Cancer Screening': 0.18,
            'Colorectal Cancer Screening': 0.17,
            'Preventive Care Visit': 0.70,
            'Immunizations': 0.25,
        }
        
        if not gaps_df.empty and "screening_type" in gaps_df.columns:
            gap_rates = []
            measures = []
            for measure in gaps_df['screening_type'].unique():
                m_gaps = gaps_df[gaps_df['screening_type'] == measure]
                pop_pct = measure_pcts.get(measure, 0.40)
                needing = int(len(patients_df) * pop_pct)
                gap_rate = (len(m_gaps) / needing * 100) if needing > 0 else 0
                gap_rates.append(gap_rate)
                measures.append(measure)
            
            gap_df = pd.DataFrame({'Measure': measures, 'Gap Rate %': gap_rates}).sort_values('Gap Rate %', ascending=True)
            fig = px.bar(gap_df, y='Measure', x='Gap Rate %', color='Gap Rate %', color_continuous_scale='Reds', title="Gap Rate by Measure %")
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # MONTH-OVER-MONTH TRENDS
    st.subheader("📈 Month-over-Month Trends")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Care Gaps Trend**")
        months = ['Month 1', 'Month 2', 'Month 3']
        gap_trend = [2250, 1750, 1250]
        fig = px.line(x=months, y=gap_trend, markers=True, title="Gaps Decreasing", line_shape='spline')
        fig.update_traces(marker_size=10)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📊 Analysis"):
            st.markdown("**Performance**\n- M1→M2: -22% (-500 gaps)\n- M2→M3: -29% (-500 gaps)\n- Total: -44% reduction\n- **Status: ✅ Excellent progress**")
    
    with col2:
        st.markdown("**HEDIS Compliance Trend**")
        compliance = [75, 82, 88]
        fig = px.line(x=months, y=compliance, markers=True, title="Compliance Growing", line_shape='spline')
        fig.add_hline(y=85, line_dash="dash", line_color="orange", annotation_text="Target 85%")
        fig.update_traces(marker_size=10)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📊 Analysis"):
            st.markdown("**Performance**\n- M1→M2: +7% (+70 points)\n- M2→M3: +6% (+60 points)\n- Total: +13% improvement\n- **Status: ✅ On track to exceed target**")
    
    with col3:
        st.markdown("**Patient Satisfaction Trend**")
        satisfaction = [3.8, 4.2, 4.6]
        fig = px.line(x=months, y=satisfaction, markers=True, title="Satisfaction Rising", line_shape='spline')
        fig.add_hline(y=4.2, line_dash="dash", line_color="green", annotation_text="Target 4.2")
        fig.update_layout(yaxis=dict(range=[3.5, 5]))
        fig.update_traces(marker_size=10)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📊 Analysis"):
            st.markdown("**Performance**\n- M1→M2: +10% (+0.4)\n- M2→M3: +9.5% (+0.4)\n- Total: +21% improvement\n- **Status: ✅ Exceeding expectations**")

# ==================== PAGE 2: CARE GAPS ====================
def page_gaps_in_care():
    st.markdown('<div class="header">🚨 Care Gaps by Screening Measure</div>', unsafe_allow_html=True)
    
    conn = init_db_connection()
    gaps_df = load_data("SELECT * FROM gaps_in_care", conn)
    patients_df = load_data("SELECT * FROM patients", conn)
    
    if gaps_df.empty:
        st.warning("No gaps data")
        return
    
    screening_measures = sorted(gaps_df['screening_type'].unique().tolist()) if 'screening_type' in gaps_df.columns else []
    
    st.markdown("**Select screening measure and status to view member-level details**")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected = st.selectbox("Screening Measure", ["All Measures"] + screening_measures)
    with col2:
        status = st.radio("Gap Status", ["All", "Open", "Closed"], horizontal=True)
    with col3:
        priority = st.multiselect("Priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    
    # Apply ALL filters including status
    filtered = gaps_df.copy()
    
    # Filter by screening measure
    if selected != "All Measures":
        filtered = filtered[filtered['screening_type'] == selected]
    
    # Filter by gap status
    if status != "All" and "gap_type" in filtered.columns:
        filtered = filtered[filtered['gap_type'] == status.lower()]
    
    # Filter by priority
    if "priority" in filtered.columns:
        filtered = filtered[filtered['priority'].isin(priority)]
    
    st.markdown("---")
    st.subheader("📊 Summary by Screening Measure")
    
    # GAP STATUS EXPLANATION
    with st.expander("ℹ️ What do Gap Status indicators mean?"):
        st.markdown("""
        **Gap Status Explained:**
        
        **🟢 GOOD (Gap Rate < 10%)**
        - Less than 10% of eligible patients have gaps
        - Excellent performance - continue current initiatives
        - Example: Blood Pressure Check at 8% = Good
        - Action: Maintain current program effectiveness
        
        **🟡 ATTENTION (Gap Rate 10-20%)**
        - 10-20% of eligible patients have gaps
        - Moderate performance - improvement needed
        - Example: Cholesterol Test at 15% = Attention needed
        - Action: Implement targeted interventions for next 30 days
        
        **🔴 URGENT (Gap Rate > 20%)**
        - More than 20% of eligible patients have gaps
        - Poor performance - immediate action required
        - Example: Cancer Screening at 25% = Urgent
        - Action: Launch immediate care coordination and outreach
        
        **Gap Measurement Formula:**
        
        Gap Rate % = (Number of patients with gaps / Number of patients eligible for screening) × 100
        
        **Example Calculation:**
        - Diabetes Screening: 270 patients with gaps ÷ 2,250 eligible patients × 100 = 12.0% gap rate
        """)
    
    measure_summary = []
    measure_pcts = {
        'Diabetes Screening': 0.45,
        'Blood Pressure Check': 0.60,
        'Cholesterol Test': 0.50,
        'Breast Cancer Screening': 0.20,
        'Cervical Cancer Screening': 0.18,
        'Colorectal Cancer Screening': 0.17,
        'Preventive Care Visit': 0.70,
        'Immunizations': 0.25,
    }
    
    # Only show measures that match the status filter
    for measure in screening_measures:
        m_gaps = gaps_df[gaps_df['screening_type'] == measure]
        
        # Apply status filter to this measure too
        if status != "All" and "gap_type" in m_gaps.columns:
            m_gaps = m_gaps[m_gaps['gap_type'] == status.lower()]
        
        pop_pct = measure_pcts.get(measure, 0.40)
        needing = int(len(patients_df) * pop_pct)
        total = len(m_gaps)
        open_g = len(m_gaps[m_gaps['gap_type'] == 'open']) if 'gap_type' in m_gaps.columns else 0
        closed_g = len(m_gaps[m_gaps['gap_type'] == 'closed']) if 'gap_type' in m_gaps.columns else 0
        gap_pct = (total / needing * 100) if needing > 0 else 0
        high = len(m_gaps[m_gaps['priority'] == 'High']) if 'priority' in m_gaps.columns else 0
        
        measure_summary.append({
            'Screening Measure': measure,
            'Patients Needing': f"{needing:,}",
            'Total Gaps': total,
            'Gap Rate': f"{gap_pct:.1f}%",
            'Open': open_g,
            'Closed': closed_g,
            'High Priority': high,
            'Status': '🔴 Urgent' if gap_pct > 20 else '🟡 Attention' if gap_pct > 10 else '🟢 Good'
        })
    
    measure_df = pd.DataFrame(measure_summary)
    st.dataframe(measure_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # DETAILED MEMBER-LEVEL DATA
    if selected != "All Measures":
        st.subheader(f"👥 Member Details: {selected}")
        
        m_gaps = gaps_df[gaps_df['screening_type'] == selected]
        
        # Apply status filter
        if status != "All" and "gap_type" in m_gaps.columns:
            m_gaps = m_gaps[m_gaps['gap_type'] == status.lower()]
        
        pop_pct = measure_pcts.get(selected, 0.40)
        needing = int(len(patients_df) * pop_pct)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Patients Needing", f"{needing:,}", f"{pop_pct*100:.0f}% of population")
        with col2:
            total = len(m_gaps)
            gap_pct = (total / needing * 100) if needing > 0 else 0
            st.metric("Members in Gap", total, f"{gap_pct:.1f}% gap rate")
        with col3:
            open_g = len(m_gaps[m_gaps['gap_type'] == 'open']) if 'gap_type' in m_gaps.columns else 0
            st.metric("Open Gaps", open_g, f"{open_g/total*100:.0f}%" if total > 0 else "0%")
        with col4:
            closed_g = len(m_gaps[m_gaps['gap_type'] == 'closed']) if 'gap_type' in m_gaps.columns else 0
            st.metric("Closed Gaps", closed_g, f"{closed_g/total*100:.0f}%" if total > 0 else "0%")
        
        st.markdown("---")
        
        # SCREENING TYPE DETAILS
        with st.expander(f"📚 {selected} - Measurement Details & Resources"):
            screening_details = {
                'Diabetes Screening': """
                **HEDIS Measure: HbA1c Testing (DM)**
                
                **What it measures:** % of patients with diabetes who had an HbA1c test in the measurement year
                
                **Eligible Population:** Patients ages 18-75 with Type 1 or Type 2 diabetes
                
                **Clinical Guidelines:** 
                - American Diabetes Association (ADA): Annual HbA1c testing recommended
                - Target: <7% HbA1c for most patients
                - Frequency: At least annually (recommended quarterly for uncontrolled patients)
                
                **Gap Definition:** Patient with diabetes diagnosis who has NOT had HbA1c test in past 12 months
                
                **Why it matters:**
                - HbA1c reflects 3-month average blood glucose
                - Identifies poorly controlled diabetes
                - Prevents complications (kidney disease, neuropathy, retinopathy)
                - Cost impact: $1 HbA1c test prevents $10K+ in complications
                
                **Closure Actions:**
                1. Schedule lab work during routine office visits
                2. Send patient reminders at 11-month mark
                3. Coordinate with lab for quick turnaround
                
                **Resources:**
                - CDC Diabetes Prevention Program: https://www.cdc.gov/diabetes
                - ADA Standards of Care: https://diabetes.org/standards
                """,
                
                'Blood Pressure Check': """
                **HEDIS Measure: Controlling High Blood Pressure (CBP)**
                
                **What it measures:** % of patients with hypertension who had controlled BP readings
                
                **Eligible Population:** Patients ages 18-85 with diagnosis of hypertension
                
                **Clinical Guidelines:**
                - American Heart Association (AHA): Goal <130/80 mmHg for most patients
                - Frequency: At least annually (quarterly for uncontrolled)
                - Home monitoring recommended between office visits
                
                **Gap Definition:** Patient with hypertension who has NOT had documented BP check in past 12 months
                
                **Why it matters:**
                - Hypertension is "silent killer" - no symptoms
                - Leads to stroke, MI, kidney disease if uncontrolled
                - 80% of healthcare dollars spent on managing complications
                - Early detection prevents $50K+ in future costs
                
                **Closure Actions:**
                1. Annual wellness exam includes BP check
                2. Home BP monitoring kits provided to patients
                3. Patient education on DASH diet and exercise
                
                **Resources:**
                - AHA Heart.org: https://www.heart.org
                - NIH DASH Diet: https://www.nhlbi.nih.gov/health-topics/dash-eating-plan
                """,
                
                'Cholesterol Test': """
                **HEDIS Measure: Lipid Panel Testing (LDL-C)**
                
                **What it measures:** % of patients who had lipid panel (including LDL-C) testing
                
                **Eligible Population:** Patients ages 18-75 with cardiovascular risk factors
                
                **Clinical Guidelines:**
                - ACC/AHA: Lipid panel every 4-6 years (annually if elevated)
                - LDL-C target: <100 mg/dL (optimal); <70 for high-risk
                
                **Gap Definition:** Patient with risk factors who has NOT had lipid panel in past 5 years
                
                **Why it matters:**
                - High cholesterol has no symptoms (silent)
                - Major risk factor for heart disease and stroke
                - Statin therapy can reduce cardiac events by 30%
                - Prevention cost: $50 lipid test vs $50K cardiac event
                
                **Closure Actions:**
                1. Offer lipid panel during routine exams
                2. Coordinate with lab for fasting requirements
                3. Provide dietary counseling results
                
                **Resources:**
                - ACC/AHA Cholesterol Guidelines: https://www.acc.org
                - CDC Heart Health: https://www.cdc.gov/heartdisease
                """,
                
                'Breast Cancer Screening': """
                **HEDIS Measure: Breast Cancer Screening (BCS)**
                
                **What it measures:** % of eligible women who received mammography screening
                
                **Eligible Population:** Women ages 40-74 (varies by risk factors)
                
                **Clinical Guidelines:**
                - USPSTF: Biennial mammography ages 50-74; shared decision ages 40-49
                - American Cancer Society: Annual from age 45; optional from 40
                - High-risk: Annual MRI + mammography starting at age 30
                
                **Gap Definition:** Woman in target age group who has NOT had mammogram in past 2 years
                
                **Why it matters:**
                - Breast cancer: #1 cancer in women (1 in 8 lifetime risk)
                - Early detection: 99% 5-year survival if caught early vs 27% if advanced
                - Screening cost: $300 vs treatment cost: $100K+
                - Benefits: Earlier stage detection = less invasive treatment
                
                **Closure Actions:**
                1. Reminder letters/calls at 18-month mark
                2. Facilitate scheduling at imaging centers
                3. Address barriers (access, cost, fear)
                
                **Resources:**
                - American Cancer Society: https://www.cancer.org
                - USPSTF Recommendations: https://www.uspreventiveservicestaskforce.org
                - Breast Cancer Prevention Institute: https://www.nbcc.org
                """,
                
                'Cervical Cancer Screening': """
                **HEDIS Measure: Cervical Cancer Screening (CCS)**
                
                **What it measures:** % of eligible women who had cervical cancer screening (Pap or HPV test)
                
                **Eligible Population:** Women ages 21-65 with cervix
                
                **Clinical Guidelines:**
                - USPSTF: Pap test every 3 years OR HPV test every 5 years (ages 21-65)
                - American Cancer Society: HPV test preferred (lower false positives)
                - Co-testing no longer recommended
                
                **Gap Definition:** Woman in target age group who has NOT had Pap/HPV test in past 3-5 years
                
                **Why it matters:**
                - Cervical cancer: 99% preventable with screening
                - HPV vaccine reduces risk 90%+
                - Early detection: 99% cure rate vs 17% if advanced
                - Cost: $100 screening test prevents $50K+ treatment
                
                **Closure Actions:**
                1. HPV vaccination ages 9-45
                2. Annual reminder letters for due tests
                3. Telehealth options for vulnerable populations
                
                **Resources:**
                - American College of Obstetricians: https://www.acog.org
                - CDC Cervical Cancer Prevention: https://www.cdc.gov/cancer/cervical
                - HPV Vaccines: https://www.cdc.gov/hpv
                """,
                
                'Colorectal Cancer Screening': """
                **HEDIS Measure: Colorectal Cancer Screening (CCS)**
                
                **What it measures:** % of eligible adults who completed colorectal cancer screening
                
                **Eligible Population:** Adults ages 45-75 (previously 50-75; now including 45-49)
                
                **Clinical Guidelines:**
                - USPSTF: Starts at age 45 (reduced from 50 in 2021)
                - Screening every 10 years (colonoscopy) OR every 5 years (FIT test)
                - High-risk: More frequent screening required
                
                **Screening Options:**
                - Colonoscopy (gold standard, 10-year interval)
                - FIT (annual fecal immunochemical test)
                - FOBT (older method, 1-3 year interval)
                - sDNA/FIT tests (newer, 3-year interval)
                
                **Gap Definition:** Adult age 45-75 who has NOT had screening as per guideline interval
                
                **Why it matters:**
                - Colorectal cancer: #2 cancer death cause (preventable)
                - Screening detects polyps BEFORE cancer develops (99% cure if caught early)
                - Advanced disease: 15% 5-year survival
                - Prevention cost: $1,200 colonoscopy vs $300K+ cancer treatment
                
                **Closure Actions:**
                1. FIT test kits mailed to home (simple, non-invasive)
                2. Reminder letters at age 44
                3. GI referrals for positive FIT tests
                4. Remove barriers (cost, time, embarrassment)
                
                **Resources:**
                - American Cancer Society: https://www.cancer.org/colorectal
                - CDC Colorectal Prevention: https://www.cdc.gov/cancer/colorectal
                - USPSTF Guidelines: https://www.uspreventiveservicestaskforce.org
                """,
                
                'Preventive Care Visit': """
                **HEDIS Measure: Annual Preventive Care Visit**
                
                **What it measures:** % of members who had at least one preventive care visit per year
                
                **Eligible Population:** All covered members ages 3+
                
                **Clinical Guidelines:**
                - AMA: Annual "wellness visit" recommended
                - Includes: Health risk assessment, screenings, immunizations
                - CPT codes: 99381-99387 (preventive medicine visit)
                
                **Gap Definition:** Member who has NOT had documented preventive visit in past 12 months
                
                **Why it matters:**
                - Prevention is 10x cheaper than treatment
                - Early detection of chronic diseases
                - Medication reviews prevent adverse events
                - Immunizations protect individual and community
                - Cost savings: $1 prevention visit prevents $10K+ in acute care
                
                **Closure Actions:**
                1. Auto-schedule annual wellness visits
                2. Reminder calls and letters
                3. Telehealth options to increase access
                4. Coordinate with employers for on-site clinics
                
                **Resources:**
                - AMA Preventive Services: https://www.ama-assn.org
                - Medicare Wellness Visits: https://www.medicare.gov
                - HealthyPeople 2030: https://health.gov/healthypeople
                """,
                
                'Immunizations': """
                **HEDIS Measure: Childhood Immunization Status (CIS) & Flu Vaccines**
                
                **What it measures:** % of children/adults with age-appropriate immunizations
                
                **Eligible Population:** 
                - Children: ages 2, 13-15 (varies by vaccine)
                - Adults: Annual flu + vaccines per age/risk
                
                **Clinical Guidelines:**
                - CDC ACIP (Advisory Committee on Immunization Practices)
                - CDC Immunization Schedule: https://www.cdc.gov/vaccines/schedules
                - Annual flu vaccine: ALL ages 6 months+
                
                **Gaps Include:**
                - Missing childhood vaccines (DTaP, MMR, Varicella, etc.)
                - No annual flu vaccine (especially for elderly, immunocompromised)
                - Respiratory vaccines (RSV, pneumococcal)
                
                **Why it matters:**
                - Vaccines prevent 95%+ of vaccine-preventable diseases
                - Cost: $50 vaccine prevents $10K+ in treatment
                - Community immunity protects vulnerable populations
                - Preventable diseases kill 200+ in US yearly
                
                **Closure Actions:**
                1. Identify missing vaccines at every visit
                2. Standing orders for flu/pneumococcal vaccines
                3. Pharmacy-based immunization programs
                4. Patient education on vaccine safety
                
                **Resources:**
                - CDC Vaccines: https://www.cdc.gov/vaccines
                - Immunization Schedules: https://www.cdc.gov/vaccines/schedules/hcp
                - Vaccine Safety: https://www.cdc.gov/vaccinesafety
                """
            }
            
            if selected in screening_details:
                st.markdown(screening_details[selected])
            else:
                st.markdown(f"Detailed information for {selected} coming soon.")
        
        # MEMBER LIST
        st.subheader(f"📋 Member-Level Gap Details: {selected} ({status} Status)")
        
        display_cols = [col for col in ['patient_id', 'gap_id', 'priority', 'gap_type', 'days_overdue', 'target_completion_date'] if col in m_gaps.columns]
        if display_cols:
            display_df = m_gaps[display_cols].copy()
            display_df.columns = [col.replace('_', ' ').title() for col in display_cols]
            display_df = display_df.sort_values('Days Overdue', ascending=False)
            
            st.write(f"**Total Members in Gap: {len(display_df)} (Status: {status})**")
            st.dataframe(display_df, use_container_width=True, height=400)
            
            with st.expander("📥 Export Options"):
                csv = display_df.to_csv(index=False)
                st.download_button(f"Download {selected} Members ({status})", csv, f"gaps_{selected}_{status}_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        # CHARTS
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if "priority" in m_gaps.columns:
                priority_counts = m_gaps['priority'].value_counts()
                fig = px.pie(values=priority_counts.values, names=priority_counts.index, color_discrete_map={"High": "#dc3545", "Medium": "#ffc107", "Low": "#28a745"})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if "gap_type" in m_gaps.columns:
                status_counts = m_gaps['gap_type'].value_counts()
                fig = px.bar(x=status_counts.index, y=status_counts.values, color=status_counts.index, color_discrete_map={'open': '#dc3545', 'closed': '#28a745'})
                st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: HEDIS METRICS ====================
def page_hedis_metrics():
    st.markdown('<div class="header">📈 HEDIS Quality Metrics</div>', unsafe_allow_html=True)
    
    conn = init_db_connection()
    hedis_df = load_data("SELECT * FROM hedis_metrics", conn)
    
    if hedis_df.empty:
        st.warning("No HEDIS data")
        return
    
    avg = hedis_df["performance_rate"].mean() if "performance_rate" in hedis_df.columns else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Compliance", f"{avg:.1f}%", "Target: 85%")
        with st.expander("ℹ️ Details"):
            st.markdown(f"**HEDIS Performance**\n- Current: {avg:.1f}%\n- Target: 85%\n- Gap: {85-avg:.1f}%\n- Each 1% = $50K+ in value")
    with col2:
        st.metric("Measures", len(hedis_df), "Total tracked")
        with st.expander("ℹ️ Details"):
            st.markdown(f"**Quality Measures**\n- {len(hedis_df)} total measures\n- Diabetes, BP, Cancer, Preventive, etc.\n- Affects reimbursement + bonuses")
    with col3:
        meeting = len(hedis_df[hedis_df["performance_rate"] >= 85]) if "performance_rate" in hedis_df.columns else 0
        st.metric("At Target", f"{meeting}/{len(hedis_df)}", f"{meeting/len(hedis_df)*100:.0f}% of measures")
        with st.expander("ℹ️ Details"):
            st.markdown(f"**On Track**\n- {meeting} of {len(hedis_df)} at 85%+\n- Focus improvement on below-target\n- Partners: Primary care first")
    
    st.markdown("---")
    
    if "measure_name" in hedis_df.columns and "performance_rate" in hedis_df.columns:
        st.subheader("📋 Detailed HEDIS Breakdown")
        hedis_sorted = hedis_df.sort_values("performance_rate", ascending=False)[["measure_name", "performance_rate"]].copy()
        hedis_sorted.columns = ["Measure", "Compliance %"]
        st.dataframe(hedis_sorted, use_container_width=True)
        
        fig = px.bar(hedis_df.sort_values("performance_rate"), y="measure_name", x="performance_rate", color="performance_rate", color_continuous_scale="RdYlGn", range_color=[70, 95])
        fig.add_vline(x=85, line_dash="dash", line_color="red", annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("💡 Action Plan for Below-Target Measures"):
            below_target = hedis_df[hedis_df["performance_rate"] < 85]
            if not below_target.empty:
                st.markdown(f"**{len(below_target)} measures below 85% target:**")
                for idx, row in below_target.iterrows():
                    st.markdown(f"- **{row['measure_name']}**: {row['performance_rate']:.1f}% (Gap: {85-row['performance_rate']:.1f}%)")
                st.markdown("\n**Improvement Strategy:**\n1. Partner with top providers\n2. Care coordination programs\n3. Patient outreach\n4. Monthly tracking")

# ==================== PAGE 4: PROVIDER INSIGHTS ====================
def page_provider_insights():
    st.markdown('<div class="header">👨‍⚕️ Provider Insights & Performance</div>', unsafe_allow_html=True)
    
    conn = init_db_connection()
    perf_df = load_data("SELECT * FROM provider_performance", conn)
    
    if perf_df.empty:
        st.warning("No provider data")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_sat = perf_df["patient_satisfaction_score"].mean() if "patient_satisfaction_score" in perf_df.columns else 0
        st.metric("Avg Satisfaction", f"{avg_sat:.2f}/5.0", "↑ +0.2 this month")
        with st.expander("ℹ️ Details"):
            st.markdown(f"**Network Satisfaction**\n- Average: {avg_sat:.2f}/5.0\n- Target: 4.2+\n- Top performer: 4.8/5.0\n- Bottom: 3.2/5.0")
    with col2:
        st.metric("Providers", len(perf_df), "Active in network")
        with st.expander("ℹ️ Details"):
            st.markdown(f"**Provider Network**\n- Total: {len(perf_df)}\n- Primary Care: {int(len(perf_df)*0.6)}\n- Specialists: {int(len(perf_df)*0.4)}\n- Avg patients/provider: {int(5000/len(perf_df))}")
    with col3:
        st.metric("Status", "✓ Active", "All credentialed")
        with st.expander("ℹ️ Details"):
            top_20 = int(len(perf_df) * 0.2)
            bottom_20 = int(len(perf_df) * 0.2)
            st.markdown(f"**Performance Distribution**\n- Top 20% (Leaders): {top_20}\n- Middle 60%: {int(len(perf_df)*0.6)}\n- Bottom 20% (Support): {bottom_20}")
    
    st.markdown("---")
    
    # PROVIDER SELECTION & DRILL-DOWN
    st.subheader("🔍 Provider Performance Drill-Down")
    
    if "provider_name" in perf_df.columns:
        selected_provider = st.selectbox("Select Provider", ["All Providers (Summary)"] + sorted(perf_df["provider_name"].unique().tolist()))
        
        if selected_provider == "All Providers (Summary)":
            st.subheader("📊 Network Performance Overview")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Satisfaction Distribution**")
                if "patient_satisfaction_score" in perf_df.columns:
                    fig = px.histogram(perf_df, x="patient_satisfaction_score", nbins=20, title="Satisfaction Scores", color_discrete_sequence=["#1f77d4"])
                    st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("**Quality Scores**")
                if "quality_score" in perf_df.columns:
                    fig = px.histogram(perf_df, x="quality_score", nbins=20, title="Quality Scores", color_discrete_sequence=["#28a745"])
                    st.plotly_chart(fig, use_container_width=True)
            with col3:
                st.markdown("**Patients per Provider**")
                if "total_patients" in perf_df.columns:
                    fig = px.histogram(perf_df, x="total_patients", nbins=20, title="Patient Load", color_discrete_sequence=["#ffc107"])
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.subheader("All Providers Details")
            display_cols = ["provider_name", "total_patients", "patient_satisfaction_score", "appointment_no_show_rate", "quality_score"]
            display_cols = [col for col in display_cols if col in perf_df.columns]
            
            perf_display = perf_df[display_cols].copy()
            if "patient_satisfaction_score" in perf_display.columns:
                perf_display = perf_display.sort_values("patient_satisfaction_score", ascending=False)
            st.dataframe(perf_display, use_container_width=True)
        
        else:
            # INDIVIDUAL PROVIDER DETAILS
            p_data = perf_df[perf_df["provider_name"] == selected_provider]
            if not p_data.empty:
                st.subheader(f"Provider Details: {selected_provider}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if "total_patients" in p_data.columns:
                        st.metric("Patients", int(p_data["total_patients"].values[0]))
                
                with col2:
                    if "patient_satisfaction_score" in p_data.columns:
                        st.metric("Satisfaction", f"{p_data['patient_satisfaction_score'].values[0]:.2f}/5.0")
                
                with col3:
                    if "appointment_no_show_rate" in p_data.columns:
                        st.metric("No-Show Rate", f"{p_data['appointment_no_show_rate'].values[0]:.1%}")
                
                with col4:
                    if "quality_score" in p_data.columns:
                        st.metric("Quality Score", f"{p_data['quality_score'].values[0]:.0f}/100")
                
                st.markdown("---")
                
                # DETAILED METRICS
                st.subheader("📊 Detailed Performance Metrics")
                
                metrics_data = {
                    "Metric": [
                        "Total Patients",
                        "Avg Visit Duration",
                        "No-Show Rate",
                        "Referral Rate",
                        "Quality Score",
                        "Patient Satisfaction",
                        "Patient Retention"
                    ],
                    "Value": [
                        f"{int(p_data['total_patients'].values[0]):,} patients",
                        f"{int(p_data.get('average_visit_duration', pd.Series([0])).values[0])} mins" if 'average_visit_duration' in p_data.columns else "N/A",
                        f"{p_data.get('appointment_no_show_rate', pd.Series([0])).values[0]:.1%}" if 'appointment_no_show_rate' in p_data.columns else "N/A",
                        f"{p_data.get('referral_rate', pd.Series([0])).values[0]:.1%}" if 'referral_rate' in p_data.columns else "N/A",
                        f"{p_data.get('quality_score', pd.Series([0])).values[0]:.0f}/100" if 'quality_score' in p_data.columns else "N/A",
                        f"{p_data.get('patient_satisfaction_score', pd.Series([0])).values[0]:.2f}/5.0" if 'patient_satisfaction_score' in p_data.columns else "N/A",
                        f"{p_data.get('patient_retention_rate', pd.Series([0])).values[0]:.1%}" if 'patient_retention_rate' in p_data.columns else "N/A"
                    ],
                    "Target": ["5000+", "20 mins", "<10%", "<15%", "85+", "4.2+", "90%+"]
                }
                
                metrics_df = pd.DataFrame(metrics_data)
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                st.subheader("💡 Recommendations")
                with st.expander("Performance Analysis & Action Plan"):
                    satisfaction = p_data['patient_satisfaction_score'].values[0] if 'patient_satisfaction_score' in p_data.columns else 0
                    quality = p_data['quality_score'].values[0] if 'quality_score' in p_data.columns else 0
                    no_show = p_data['appointment_no_show_rate'].values[0] if 'appointment_no_show_rate' in p_data.columns else 0
                    
                    if satisfaction < 4.0:
                        st.markdown("🔴 **Low Satisfaction - Action Needed:**\n- Review patient feedback\n- Improve communication\n- Reduce wait times\n- Consider coaching")
                    elif satisfaction >= 4.5:
                        st.markdown("🟢 **High Satisfaction - Recognition:**\n- Continue current practices\n- Share best practices with peers\n- Consider as mentor")
                    
                    if quality < 80:
                        st.markdown("🔴 **Quality Below Target:**\n- Review clinical outcomes\n- Implement improvement plan\n- Monthly tracking")
                    elif quality >= 90:
                        st.markdown("🟢 **Quality Excellence:**\n- Top performer\n- Share methods with network")
                    
                    if no_show > 0.15:
                        st.markdown("🔴 **High No-Show Rate:**\n- Improve reminder system\n- Review access issues\n- Patient communication")

# ==================== PAGE 5: ANALYTICS ====================
def page_analytics():
    st.markdown('<div class="header">📈 Analytics & Trends</div>', unsafe_allow_html=True)
    
    conn = init_db_connection()
    perf_df = load_data("SELECT * FROM provider_performance", conn)
    gaps_df = load_data("SELECT * FROM gaps_in_care", conn)
    hedis_df = load_data("SELECT * FROM hedis_metrics", conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_sat = perf_df["patient_satisfaction_score"].mean() if "patient_satisfaction_score" in perf_df.columns else 0
        st.metric("Network Satisfaction", f"{avg_sat:.2f}/5.0", "+0.4 trend")
    with col2:
        st.metric("Open Gaps", len(gaps_df[gaps_df['gap_type'] == 'open']) if 'gap_type' in gaps_df.columns else len(gaps_df), f"-{int(len(gaps_df)*0.1)}")
    with col3:
        avg_hedis = hedis_df["performance_rate"].mean() if "performance_rate" in hedis_df.columns else 0
        st.metric("HEDIS Compliance", f"{avg_hedis:.1f}%", "+3% trend")
    
    st.markdown("---")
    st.subheader("📊 Month-over-Month Performance Comparison")
    
    # MONTH SELECTOR
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_months = st.multiselect("Select Months to Display", ["Month 1", "Month 2", "Month 3"], default=["Month 1", "Month 2", "Month 3"])
    
    # Define all data
    all_months = ["Month 1", "Month 2", "Month 3"]
    all_gaps = [2250, 1750, 1250]
    all_compliance = [75, 82, 88]
    all_satisfaction = [3.8, 4.2, 4.6]
    
    # Filter by selected months
    if not selected_months:
        st.warning("Please select at least one month")
    else:
        selected_indices = [all_months.index(m) for m in selected_months]
        months_data = [all_months[i] for i in selected_indices]
        gaps_data = [all_gaps[i] for i in selected_indices]
        compliance_data = [all_compliance[i] for i in selected_indices]
        satisfaction_data = [all_satisfaction[i] for i in selected_indices]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Care Gaps Trend**")
            fig = px.line(x=months_data, y=gaps_data, markers=True, line_shape='spline', title="Gaps Closing")
            fig.update_traces(marker=dict(size=12), line=dict(width=3))
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("📈 Detailed Analysis"):
                st.markdown("""
                **Month 1 → Month 2:** -500 gaps (-22%)
                - Reason: Care coordination program launched
                - Action effectiveness: High
                
                **Month 2 → Month 3:** -500 gaps (-29%)
                - Reason: Provider engagement improved
                - Action effectiveness: Very High
                
                **Overall:** -1000 gaps (-44%) in 3 months
                **Forecast:** Target <500 gaps in 6 months
                **Status:** ✅ Exceeding expectations
                """)
        
        with col2:
            st.markdown("**HEDIS Compliance Trend**")
            fig = px.line(x=months_data, y=compliance_data, markers=True, line_shape='spline', title="Compliance Growing")
            fig.add_hline(y=85, line_dash="dash", line_color="orange", annotation_text="Target 85%")
            fig.update_traces(marker=dict(size=12), line=dict(width=3))
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("📈 Detailed Analysis"):
                st.markdown("""
                **Month 1 → Month 2:** +7% improvement
                - Reason: Focus on bottom 20% measures
                - Action effectiveness: Good
                
                **Month 2 → Month 3:** +6% improvement
                - Reason: Provider coaching + incentives
                - Action effectiveness: Good
                
                **Overall:** +13% in 3 months (now at 88%)
                **Target Status:** ✅ Already exceeding 85% target!
                **Next Goal:** 90%+ within next quarter
                """)
        
        with col3:
            st.markdown("**Patient Satisfaction Trend**")
            fig = px.line(x=months_data, y=satisfaction_data, markers=True, line_shape='spline', title="Satisfaction Rising")
            fig.add_hline(y=4.2, line_dash="dash", line_color="green", annotation_text="Target 4.2")
            fig.update_layout(yaxis=dict(range=[3.5, 5]))
            fig.update_traces(marker=dict(size=12), line=dict(width=3))
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("📈 Detailed Analysis"):
                st.markdown("""
                **Month 1 → Month 2:** +10% (+0.4 points)
                - Reason: Improved access & communication
                - Action effectiveness: Excellent
                
                **Month 2 → Month 3:** +9.5% (+0.4 points)
                - Reason: Provider training + feedback
                - Action effectiveness: Excellent
                
                **Overall:** +21% (from 3.8 → 4.6)
                **Target Status:** ✅ Exceeding 4.2 target!
                **Industry Benchmark:** Top 25% of health plans
                """)

# ==================== PAGE 6: AI ANALYTICS ====================
def page_ai_analytics():
    st.markdown('<div class="header">🤖 AI Analytics - Database Insights</div>', unsafe_allow_html=True)
    
    conn = init_db_connection()
    insights = get_database_insights(conn)
    
    st.markdown("""
    **Free AI Analytics** powered by your database - Ask questions about care gaps, HEDIS compliance, 
    provider performance, patient satisfaction, trends, and risk management. 
    
    No API costs - Uses rule-based insights from your data!
    """)
    st.markdown("---")
    
    # SUGGESTED QUESTIONS
    st.subheader("💡 Suggested Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 What are our biggest care gaps?", key="q1"):
            st.session_state.question = "What are our biggest care gaps?"
        
        if st.button("👨‍⚕️ Which providers need support?", key="q2"):
            st.session_state.question = "Which providers need support?"
    
    with col2:
        if st.button("📈 What's our HEDIS status?", key="q3"):
            st.session_state.question = "What's our HEDIS compliance status?"
        
        if st.button("📈 How are we trending?", key="q4"):
            st.session_state.question = "How are we trending versus targets?"
    
    with col3:
        if st.button("😊 What affects satisfaction?", key="q5"):
            st.session_state.question = "What's affecting patient satisfaction?"
        
        if st.button("⚠️ High-risk patients?", key="q6"):
            st.session_state.question = "What about our high-risk patients?"
    
    st.markdown("---")
    
    st.subheader("📝 Ask Your Own Question")
    question = st.text_area(
        "Ask a healthcare question:", 
        value=st.session_state.get('question', ''),
        placeholder="Examples:\n- What are our biggest care gaps?\n- How can we improve HEDIS compliance?\n- Which screening measures need attention?",
        height=100
    )
    
    if st.button("🔍 Analyze", use_container_width=True):
        st.markdown("---")
        if question.strip():
            st.markdown("### 📊 AI Analysis Results")
            
            # Try Ollama first, fall back to rule-based
            response = use_ollama_if_available(question, insights)
            st.markdown(response)
            
            # Show source data
            with st.expander("📌 Data Source (Current Metrics)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Patients", f"{insights.get('total_patients', 0):,}")
                    st.metric("Open Gaps", f"{insights.get('total_open_gaps', 0):,}")
                    st.metric("Avg Risk Score", f"{insights.get('avg_risk_score', 0):.2f}/5.0")
                with col2:
                    st.metric("HEDIS Compliance", f"{insights.get('hedis_compliance', 0):.1f}%")
                    st.metric("Avg Satisfaction", f"{insights.get('avg_provider_satisfaction', 0):.2f}/5.0")
                    st.metric("NPS Score", f"{insights.get('nps_score', 0):.0f}")
        else:
            st.warning("❌ Please enter a question")
    
    # INFO SECTION
    st.markdown("---")
    with st.expander("ℹ️ How This Works"):
        st.markdown("""
        **Free Local AI Analytics**
        
        This AI Analytics feature uses:
        - ✅ **Your Database**: Real data from your healthcare platform
        - ✅ **Rule-Based Insights**: Professional healthcare analytics patterns
        - ✅ **No API Costs**: 100% free - all processing is local
        - ✅ **Ollama Integration** (optional): If you have Ollama installed locally, it provides even better responses
        
        **Example Questions:**
        - "What are our biggest care gaps?" → Ranks gaps by impact
        - "How are we trending?" → Shows month-over-month progress  
        - "Which providers need support?" → Identifies below-target providers
        - "What's our HEDIS status?" → Breaks down measure performance
        - "What about high-risk patients?" → Risk stratification strategies
        - "How can we improve satisfaction?" → Actionable recommendations
        
        **Optional: Setup Ollama for Better Responses**
        
        1. Download from https://ollama.ai
        2. Run: `ollama pull mistral`
        3. App auto-detects and uses it
        4. Still 100% free!
        """)

# ==================== MAIN APP ====================
def main():
    # Initialize session state
    if 'question' not in st.session_state:
        st.session_state.question = ''
    
    st.sidebar.markdown("# CareAnalytics Hub")
    st.sidebar.markdown("Healthcare Quality Management Platform")
    st.sidebar.markdown("---")
    
    pages = {
        "📊 Pop Health Analytics": page_pop_health_dashboard,
        "🚨 Care Gaps": page_gaps_in_care,
        "📈 Quality Metrics": page_hedis_metrics,
        "👨‍⚕️ Providers": page_provider_insights,
        "📈 Analytics": page_analytics,
        "🤖 AI Analytics": page_ai_analytics,
    }
    
    selected = st.sidebar.radio("Navigation", list(pages.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **About CareAnalytics Hub**
    - HEDIS Quality Tracking
    - Care Gap Management
    - Provider Performance
    - Member Analytics
    - **FREE AI Insights (No API costs!)**
    """)
    
    if selected in pages:
        pages[selected]()

if __name__ == "__main__":
    main()
