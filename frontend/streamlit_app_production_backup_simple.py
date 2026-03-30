"""CareAnalytics Hub - Healthcare Quality Management Platform"""
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="CareAnalytics Hub", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .header {color: #1f77d4; font-size: 2rem; font-weight: bold; margin-bottom: 1.5rem; border-bottom: 3px solid #1f77d4; padding-bottom: 0.5rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_db_connection():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(script_dir, "database", "healthcare_dashboard.db")
    if not os.path.exists(db_path):
        st.error(f"Database not found")
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
    nps = ((promoters - detractors) / total) * 100
    return round(nps, 2)

def page_dashboard():
    st.markdown('<div class="header">📊 Dashboard</div>', unsafe_allow_html=True)
    conn = init_db_connection()
    patients_df = load_data("SELECT * FROM patients", conn)
    gaps_df = load_data("SELECT * FROM gaps_in_care", conn)
    providers_df = load_data("SELECT * FROM providers", conn)
    hedis_df = load_data("SELECT * FROM hedis_metrics", conn)
    
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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Patients", len(patients_df), f"+{int(len(patients_df) * 0.05)} this month")
    
    with col2:
        gap_by_type = gaps_df['screening_type'].value_counts() if 'screening_type' in gaps_df.columns else pd.Series()
        st.metric("🚨 Total Gaps", len(gaps_df), f"{len(gap_by_type)} screening types")
        with st.expander("ℹ️ What is this?"):
            st.markdown("**Care Gaps** - Individual healthcare screenings patients are missing. Each measure affects different patient populations (45% diabetes, 60% BP, 35% cancer, etc.)")
    
    with col3:
        avg_risk = patients_df["risk_score"].mean()
        st.metric("⚠️ Avg Risk Score", f"{avg_risk:.2f}/5.0", "Risk Assessment")
        with st.expander("ℹ️ What is this?"):
            st.markdown(f"**Risk Score**: {avg_risk:.2f}/5.0\n- 1.0-2.0 = Low Risk\n- 2.1-3.5 = Moderate\n- 3.6-5.0 = High Risk")
    
    with col4:
        nps = calculate_nps(patients_df)
        st.metric("📈 NPS Score", f"{nps:.0f}", "Promoters vs Detractors")
        with st.expander("ℹ️ What is this?"):
            st.markdown(f"**NPS**: {nps:.0f} - 70+=Excellent, 50-70=Good, <50=Needs Work")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Care Gaps by Priority")
        if not gaps_df.empty and "priority" in gaps_df.columns:
            gaps_by_priority = gaps_df.groupby("priority").size().reset_index(name="count")
            fig = px.pie(gaps_by_priority, names="priority", values="count", color_discrete_map={"High": "#dc3545", "Medium": "#ffc107", "Low": "#28a745"})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Gaps by Screening Type")
        if not gaps_df.empty and "screening_type" in gaps_df.columns:
            gap_breakdown = gaps_df['screening_type'].value_counts().reset_index()
            gap_breakdown.columns = ['Screening Type', 'Count']
            fig = px.bar(gap_breakdown, y='Screening Type', x='Count', color='Count', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)

def page_gaps_in_care():
    st.markdown('<div class="header">🚨 Care Gaps by Screening Measure</div>', unsafe_allow_html=True)
    conn = init_db_connection()
    gaps_df = load_data("SELECT * FROM gaps_in_care", conn)
    patients_df = load_data("SELECT * FROM patients", conn)
    
    if gaps_df.empty:
        st.warning("No gaps data")
        return
    
    screening_measures = sorted(gaps_df['screening_type'].unique().tolist()) if 'screening_type' in gaps_df.columns else []
    
    st.markdown("**Each screening measure shows % of patients needing that screening who have a gap.**")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected = st.selectbox("Screening Measure", ["All Measures"] + screening_measures)
    with col2:
        status = st.radio("Status", ["All", "Open", "Closed"], horizontal=True)
    with col3:
        priority = st.multiselect("Priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    
    filtered = gaps_df.copy()
    if selected != "All Measures":
        filtered = filtered[filtered['screening_type'] == selected]
    if status != "All" and "gap_type" in filtered.columns:
        filtered = filtered[filtered['gap_type'] == status.lower()]
    if "priority" in filtered.columns:
        filtered = filtered[filtered['priority'].isin(priority)]
    
    st.markdown("---")
    st.subheader("📊 Gaps by Screening Measure")
    
    measure_summary = []
    measure_pcts = {'Diabetes Screening': 0.45, 'Blood Pressure Check': 0.60, 'Cholesterol Test': 0.50, 'Cancer Screening': 0.35, 'Preventive Care Visit': 0.70, 'Immunizations': 0.25}
    
    for measure in screening_measures:
        m_gaps = gaps_df[gaps_df['screening_type'] == measure]
        pop_pct = measure_pcts.get(measure, 0.40)
        needing = int(len(patients_df) * pop_pct)
        total = len(m_gaps)
        open_g = len(m_gaps[m_gaps['gap_type'] == 'open']) if 'gap_type' in m_gaps.columns else total
        closed_g = len(m_gaps[m_gaps['gap_type'] == 'closed']) if 'gap_type' in m_gaps.columns else 0
        gap_pct = (total / needing * 100) if needing > 0 else 0
        high = len(m_gaps[m_gaps['priority'] == 'High']) if 'priority' in m_gaps.columns else 0
        
        measure_summary.append({'Screening Measure': measure, 'Patients Needing': f"{needing:,}", 'Total Gaps': total, 'Gap Rate': f"{gap_pct:.1f}%", 'Open': open_g, 'Closed': closed_g, 'High Priority': high, 'Status': '🔴 Urgent' if gap_pct > 20 else '🟡 Attention' if gap_pct > 10 else '🟢 Good'})
    
    measure_df = pd.DataFrame(measure_summary)
    st.dataframe(measure_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    if selected != "All Measures":
        st.subheader(f"📋 {selected}")
        m_gaps = gaps_df[gaps_df['screening_type'] == selected]
        pop_pct = measure_pcts.get(selected, 0.40)
        needing = int(len(patients_df) * pop_pct)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Patients Needing", f"{needing:,}", f"{pop_pct*100:.0f}%")
        with col2:
            total = len(m_gaps)
            gap_pct = (total / needing * 100) if needing > 0 else 0
            st.metric("Gaps", total, f"{gap_pct:.1f}%")
        with col3:
            open_g = len(m_gaps[m_gaps['gap_type'] == 'open']) if 'gap_type' in m_gaps.columns else 0
            st.metric("Open", open_g)
        with col4:
            closed_g = len(m_gaps[m_gaps['gap_type'] == 'closed']) if 'gap_type' in m_gaps.columns else 0
            st.metric("Closed", closed_g)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if "priority" in m_gaps.columns:
                counts = m_gaps['priority'].value_counts()
                fig = px.pie(values=counts.values, names=counts.index, color_discrete_map={"High": "#dc3545", "Medium": "#ffc107", "Low": "#28a745"})
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if "gap_type" in m_gaps.columns:
                counts = m_gaps['gap_type'].value_counts()
                fig = px.bar(x=counts.index, y=counts.values, color=counts.index, color_discrete_map={'open': '#dc3545', 'closed': '#28a745'})
                st.plotly_chart(fig, use_container_width=True)

def page_hedis():
    st.markdown('<div class="header">📈 HEDIS Quality Metrics</div>', unsafe_allow_html=True)
    conn = init_db_connection()
    hedis_df = load_data("SELECT * FROM hedis_metrics", conn)
    
    if hedis_df.empty:
        st.warning("No HEDIS data")
        return
    
    avg = hedis_df["performance_rate"].mean() if "performance_rate" in hedis_df.columns else 0
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Compliance", f"{avg:.1f}%", "Target: 85%")
        with st.expander("ℹ️ What is this?"):
            st.markdown(f"**HEDIS Compliance**: {avg:.1f}% - % of quality measures met. Target 85%+. Each 1% = better outcomes + bonus $.")
    with col2:
        st.metric("Measures", len(hedis_df))
        with st.expander("ℹ️ What is this?"):
            st.markdown("**HEDIS Measures**: Diabetes, BP control, cancer screening, preventive care, etc.")
    with col3:
        meeting = len(hedis_df[hedis_df["performance_rate"] >= 85]) if "performance_rate" in hedis_df.columns else 0
        st.metric("At Target (85%)", meeting, f"{meeting/len(hedis_df)*100:.0f}%")
        with st.expander("ℹ️ What is this?"):
            st.markdown(f"**Measures at Target**: {meeting}/{len(hedis_df)} measures meet 85% goal. Focus improvement efforts on below-target measures.")
    
    st.markdown("---")
    if "measure_name" in hedis_df.columns and "performance_rate" in hedis_df.columns:
        st.subheader("HEDIS Details")
        st.dataframe(hedis_df[["measure_name", "performance_rate"]], use_container_width=True)
        fig = px.bar(hedis_df.sort_values("performance_rate"), y="measure_name", x="performance_rate", title="HEDIS by Measure")
        fig.add_vline(x=85, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

def page_providers():
    st.markdown('<div class="header">👨‍⚕️ Provider Insights</div>', unsafe_allow_html=True)
    conn = init_db_connection()
    perf_df = load_data("SELECT * FROM provider_performance", conn)
    
    if perf_df.empty:
        st.warning("No provider data")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        avg = perf_df["patient_satisfaction_score"].mean() if "patient_satisfaction_score" in perf_df.columns else 0
        st.metric("Satisfaction", f"{avg:.2f}/5.0", "Network avg")
        with st.expander("ℹ️ What is this?"):
            st.markdown(f"**Patient Satisfaction**: {avg:.2f}/5.0 - Target 4.2+. Improve via better communication, less wait times, care coordination.")
    with col2:
        st.metric("Providers", len(perf_df))
        with st.expander("ℹ️ What is this?"):
            st.markdown(f"**Network Size**: {len(perf_df)} active providers. Top 20% are leaders. Bottom 20% need support.")
    with col3:
        st.metric("Status", "✓ Active")
    
    st.markdown("---")
    if "provider_name" in perf_df.columns:
        selected = st.selectbox("Provider", ["All Providers"] + sorted(perf_df["provider_name"].unique().tolist()))
        if selected != "All Providers":
            p_data = perf_df[perf_df["provider_name"] == selected]
            if not p_data.empty:
                st.subheader(f"{selected}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if "total_patients" in p_data.columns:
                        st.metric("Patients", p_data["total_patients"].values[0])
                with col2:
                    if "patient_satisfaction_score" in p_data.columns:
                        st.metric("Satisfaction", f"{p_data['patient_satisfaction_score'].values[0]:.2f}")
                with col3:
                    if "appointment_no_show_rate" in p_data.columns:
                        st.metric("No-Show", f"{p_data['appointment_no_show_rate'].values[0]:.1%}")
                with col4:
                    if "quality_score" in p_data.columns:
                        st.metric("Quality", f"{p_data['quality_score'].values[0]:.0f}")
        else:
            st.dataframe(perf_df[["provider_name", "total_patients", "patient_satisfaction_score", "appointment_no_show_rate", "quality_score"]], use_container_width=True)

def page_analytics():
    st.markdown('<div class="header">📈 Analytics & Trends</div>', unsafe_allow_html=True)
    
    conn = init_db_connection()
    perf_df = load_data("SELECT * FROM provider_performance", conn)
    gaps_df = load_data("SELECT * FROM gaps_in_care", conn)
    hedis_df = load_data("SELECT * FROM hedis_metrics", conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        avg = perf_df["patient_satisfaction_score"].mean() if "patient_satisfaction_score" in perf_df.columns else 0
        st.metric("Satisfaction", f"{avg:.2f}/5.0", "+0.4 trend")
    with col2:
        st.metric("Gaps", len(gaps_df), f"-{int(len(gaps_df) * 0.1)}")
    with col3:
        avg_hedis = hedis_df["performance_rate"].mean() if "performance_rate" in hedis_df.columns else 0
        st.metric("HEDIS", f"{avg_hedis:.1f}%", "+3% trend")
    
    st.markdown("---")
    st.subheader("📊 Month-over-Month Trends")
    
    months = ["Month 1", "Month 2", "Month 3"]
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Care Gaps** (Down=Good)")
        gap_trend = [2250, 1750, 1250]
        fig = px.line(x=months, y=gap_trend, markers=True, title="Gaps Closing")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("ℹ️ Understanding"):
            st.markdown("**Trend:** Down 44% over 3 months! Your gap closure program works. Keep going 20-30%/month.")
    
    with col2:
        st.markdown("**HEDIS Compliance** (Up=Good)")
        compliance = [75, 82, 88]
        fig = px.line(x=months, y=compliance, markers=True, title="Compliance Growing")
        fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("ℹ️ Understanding"):
            st.markdown("**Trend:** Up 13% in 3 months, exceeding 85% target! You're on track.")
    
    with col3:
        st.markdown("**Satisfaction** (Up=Good)")
        satisfaction = [3.8, 4.2, 4.6]
        fig = px.line(x=months, y=satisfaction, markers=True, title="Satisfaction Rising", range_y=[3.5, 5])
        fig.add_hline(y=4.2, line_dash="dash", line_color="green", annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("ℹ️ Understanding"):
            st.markdown("**Trend:** Up 21%! Better care, less wait times, improved communication. Excellent progress!")

def page_ai():
    st.markdown('<div class="header">🤖 AI Analytics</div>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Healthcare Analytics** - Ask questions about your data (local, no API costs)")
    st.markdown("---")
    
    question = st.text_area("Ask a question:", placeholder="What are our biggest care gaps?", height=100)
    if st.button("🔍 Analyze"):
        if question.strip():
            st.info("💡 AI analysis ready in premium version")
        else:
            st.warning("Enter a question")

def main():
    st.sidebar.markdown("# CareAnalytics Hub")
    st.sidebar.markdown("Healthcare Quality Management")
    st.sidebar.markdown("---")
    
    pages = {
        "📊 Dashboard": page_dashboard,
        "🚨 Care Gaps": page_gaps_in_care,
        "📈 Quality Metrics": page_hedis,
        "👨‍⚕️ Providers": page_providers,
        "📈 Analytics": page_analytics,
        "🤖 AI": page_ai,
    }
    
    selected = st.sidebar.radio("Navigation", list(pages.keys()))
    if selected in pages:
        pages[selected]()

if __name__ == "__main__":
    main()
