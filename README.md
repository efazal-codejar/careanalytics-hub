# CareAnalytics Hub 🏥

**Enterprise Healthcare Quality Management Platform**

A comprehensive, production-grade healthcare analytics dashboard for tracking HEDIS metrics, managing care gaps, monitoring provider performance, and generating AI-powered clinical insights.

## 📊 Overview

CareAnalytics Hub is a full-stack healthcare analytics application built for healthcare organizations to:

- **Track HEDIS Compliance** - Monitor quality metrics against 85%+ industry targets
- **Manage Care Gaps** - Identify and close gaps in preventive screenings across your patient population
- **Monitor Providers** - Analyze provider performance with patient satisfaction and quality scores
- **Population Health Analytics** - Dashboard view of risk distribution, age demographics, and clinical outcomes
- **AI-Powered Insights** - Ask questions about your data and get instant analytical recommendations
- **Month-over-Month Trends** - Track improvement across compliance, gaps, and patient satisfaction

## ✨ Key Features

### 1. Population Health Analytics Dashboard
- **4 Core KPIs**: Total Patients, Open Gaps, Average Risk Score, NPS Score
- **Risk Distribution**: Pie chart showing high/medium/low risk patient segments
- **Age Demographics**: Patient distribution across age groups
- **Gap Priority Analysis**: Visual breakdown of gap severity levels
- **Month-over-Month Trends**: 3-month performance tracking with analysis

### 2. Care Gaps by Screening Measure
- **8 Screening Measures Tracked**:
  - Diabetes Screening (HbA1c)
  - Blood Pressure Check (CBP)
  - Cholesterol Test (LDL-C)
  - Breast Cancer Screening
  - Cervical Cancer Screening
  - Colorectal Cancer Screening
  - Preventive Care Visits
  - Immunizations

- **Gap Status Indicators** 🟢🟡🔴:
  - 🟢 GOOD: <10% gap rate
  - 🟡 ATTENTION: 10-20% gap rate
  - 🔴 URGENT: >20% gap rate

- **Member-Level Details**: Drill-down to individual patient gaps with priority and days overdue
- **Clinical Resources**: CDC, ADA, AHA, USPSTF guidelines for each screening type
- **Export Functionality**: Download gap lists as CSV for outreach programs

### 3. HEDIS Quality Metrics
- **Compliance Tracking**: Real-time performance against 85% target
- **Measure-by-Measure Analysis**: Detailed breakdown of each quality metric
- **Action Plans**: Recommended interventions for below-target measures
- **Provider Accountability**: Individual provider compliance tracking

### 4. Provider Insights & Performance
- **Provider Rankings**: Sort by satisfaction, quality scores, patient volume
- **Individual Provider Drill-Down**: Detailed metrics including:
  - Patient satisfaction (0-5 scale)
  - Quality scores (0-100)
  - Appointment no-show rates
  - Patient retention rates
- **Performance Tiers**: Top performers, average performers, needs support
- **Improvement Plans**: Recommendations for coaching and support

### 5. Analytics & Trends
- **Interactive Month Selector**: Compare any 1-3 months
- **4 Trend Charts**:
  - Care Gaps Trend (open→closed)
  - HEDIS Compliance Trend
  - Patient Satisfaction Trend
  - Readmission Rate Trend
- **Detailed Analysis**: Each chart includes deep-dive insights and action items

### 6. AI Analytics Engine
- **6 Suggested Questions**: One-click analysis on key topics
- **Custom Questions**: Ask your own healthcare analytics questions
- **Local AI Processing**: All analysis done locally (no external APIs)
- **Actionable Insights**: Recommendations with financial impact projections

## 🏗️ Project Structure

```
careanalytics-hub/
├── frontend/
│   └── streamlit_app_production.py       # Main Streamlit application (650+ lines)
├── backend/
│   ├── app_backend.py                    # FastAPI backend (optional)
│   └── init_database.py                  # Database initialization
├── database/
│   └── healthcare_dashboard.db           # SQLite database (auto-created)
├── data/
│   └── (sample data files)
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
├── DEPLOYMENT.md                         # Streamlit Cloud deployment guide
├── GITHUB_SETUP.md                       # GitHub setup instructions
├── API_DOCUMENTATION.md                  # API endpoints (if using FastAPI)
├── DATABASE_SCHEMA.md                    # Database structure
├── INSTALLATION.md                       # Local setup guide
└── .gitignore                            # Git ignore file
```

## 📋 Requirements

- **Python**: 3.8+
- **OS**: Windows, macOS, Linux
- **Key Libraries**:
  - `streamlit` - Web framework
  - `pandas` - Data manipulation
  - `plotly` - Interactive charts
  - `sqlite3` - Database (built-in)
  - `numpy` - Numerical computing

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/careanalytics-hub.git
cd careanalytics-hub
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python backend/init_database.py
```

### 5. Generate Sample Data
```bash
python backend/generate_realistic_data.py
```

### 6. Run Application
```bash
streamlit run frontend/streamlit_app_production.py
```

The app will open in your browser at `http://localhost:8501`

## 📚 Documentation

- **[INSTALLATION.md](./INSTALLATION.md)** - Detailed setup instructions for all platforms
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deploy to Streamlit Cloud
- **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Database structure and tables
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - REST API endpoints (if enabled)
- **[GITHUB_SETUP.md](./GITHUB_SETUP.md)** - Push to GitHub
- **[USER_GUIDE.md](./USER_GUIDE.md)** - How to use each feature

## 🔧 Configuration

### Database
- Default location: `database/healthcare_dashboard.db`
- Auto-creates on first run
- Includes 5000 synthetic patient records

### Sample Data
**Default realistic dataset:**
- 5,000 patients
- 150 providers
- 1,200 care gaps (open/closed)
- 750 HEDIS metrics
- 5,000 clinical quality records

## 📊 Data Sources

All data is **synthetic and realistic** for:
- Portfolio/interview demonstrations
- Testing and development
- Training purposes

**No real patient data** is included.

## 🤖 AI Analytics

The AI Analytics engine provides intelligent insights using:
- **Local Processing**: All analysis happens on your machine
- **Real Data**: Analyzes actual metrics from your database
- **6 Suggested Topics**:
  1. Care Gaps Analysis
  2. HEDIS Compliance
  3. Provider Performance
  4. Readmission Prevention
  5. Patient Experience
  6. Key Opportunities

- **Custom Questions**: Ask your own healthcare questions

## 📈 Sample Metrics

**Default Dataset Includes:**
- Total Patients: 5,000
- Total Care Gaps: 1,200 (24% gap rate)
- Open Gaps: 420 (35%)
- Closed Gaps: 780 (65%)
- HEDIS Compliance: 84%
- Patient Satisfaction: 4.2/5.0
- NPS Score: +42
- Average Risk Score: 2.99/5.0

## 🎯 Use Cases

1. **Job Interview Portfolio**: Show healthcare analytics expertise
2. **Healthcare Organization**: Track real quality metrics
3. **Health Plan**: Monitor provider network performance
4. **ACO/Medical Group**: Manage HEDIS compliance
5. **Research**: Analyze healthcare quality patterns

## 🔐 Data Security

- **SQLite Database**: Local file-based storage
- **No Cloud**: All data stays on your machine
- **No API Keys**: No external dependencies
- **HIPAA-Ready**: Can be adapted for real patient data with proper safeguards

## 🐛 Troubleshooting

**Database not found?**
```bash
python backend/init_database.py
```

**App won't start?**
```bash
pip install --upgrade streamlit
streamlit run frontend/streamlit_app_production.py
```

**Data missing?**
```bash
python backend/generate_realistic_data.py
```

See [INSTALLATION.md](./INSTALLATION.md) for detailed troubleshooting.

## 🚀 Deployment

### Streamlit Cloud (FREE)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your GitHub repo
4. Live in seconds! 🎉

See [DEPLOYMENT.md](./DEPLOYMENT.md) for details.

## 📝 License

MIT License - See [LICENSE](./LICENSE) file

## 👤 Author

Created as a portfolio healthcare analytics project.

## 🙋 Support

For questions or issues:
1. Check [INSTALLATION.md](./INSTALLATION.md)
2. Review [FAQ.md](./FAQ.md)
3. Open an issue on GitHub

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📞 Contact

- GitHub: [@efazal-codejar](https://github.com/efazal-codejar)
- Email: i.erumfazal@yahoo.com
- LinkedIn: [Your Profile](https://www.linkedin.com/in/dr-erum-f-b01191193/)

---

**CareAnalytics Hub** - Enterprise Healthcare Analytics at Your Fingertips 🏥