# Installation Guide 🛠️

Complete step-by-step instructions to set up CareAnalytics Hub on Windows, macOS, or Linux.

## Prerequisites

- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **Text Editor or IDE** (VS Code recommended) - [Download here](https://code.visualstudio.com/)

### Verify Python Installation

```bash
python --version
# or
python3 --version
```

Should show 3.8+. If not, download from [python.org](https://www.python.org)

---

## 🪟 Windows Installation

### Step 1: Clone Repository

```powershell
# Navigate to where you want the project
cd Documents

# Clone the repository
git clone https://github.com/yourusername/careanalytics-hub.git
cd careanalytics-hub
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# You should see (venv) at the start of your command line
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed pandas-1.x.x plotly-5.x.x streamlit-1.x.x ...
```

### Step 4: Initialize Database

```powershell
# Create database and tables
python backend/init_database.py

# You should see: ✓ Database created successfully
```

### Step 5: Generate Sample Data

```powershell
# Populate with realistic sample data
python backend/generate_realistic_data.py

# You should see: ✓ Data generated successfully
```

### Step 6: Run Application

```powershell
# Start the Streamlit app
streamlit run frontend/streamlit_app_production.py
```

**Success! Your browser should open to** `http://localhost:8501`

---

## 🍎 macOS Installation

### Step 1: Clone Repository

```bash
# Navigate to where you want the project
cd ~/Documents

# Clone the repository
git clone https://github.com/yourusername/careanalytics-hub.git
cd careanalytics-hub
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) at the start of your terminal
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
# Create database and tables
python3 backend/init_database.py

# You should see: ✓ Database created successfully
```

### Step 5: Generate Sample Data

```bash
# Populate with realistic sample data
python3 backend/generate_realistic_data.py

# You should see: ✓ Data generated successfully
```

### Step 6: Run Application

```bash
# Start the Streamlit app
streamlit run frontend/streamlit_app_production.py
```

**Success! Your browser should open to** `http://localhost:8501`

---

## 🐧 Linux Installation

### Step 1: Clone Repository

```bash
# Navigate to where you want the project
cd ~/

# Clone the repository
git clone https://github.com/yourusername/careanalytics-hub.git
cd careanalytics-hub
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) at the start of your terminal
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
# Create database and tables
python3 backend/init_database.py

# You should see: ✓ Database created successfully
```

### Step 5: Generate Sample Data

```bash
# Populate with realistic sample data
python3 backend/generate_realistic_data.py

# You should see: ✓ Data generated successfully
```

### Step 6: Run Application

```bash
# Start the Streamlit app
streamlit run frontend/streamlit_app_production.py
```

**Success! Your browser should open to** `http://localhost:8501`

---

## 🚀 Verify Installation

Once the app is running, test these features:

1. **Dashboard Page** ✅
   - Should show 4 KPI cards
   - Charts should load

2. **Care Gaps Page** ✅
   - Select a screening measure
   - View member list

3. **AI Analytics Page** ✅
   - Click a suggested question
   - Get instant analysis

## 📁 Folder Structure

After installation, your folder should look like:

```
careanalytics-hub/
├── venv/                              # Virtual environment (created)
├── database/
│   └── healthcare_dashboard.db        # SQLite database (created)
├── frontend/
│   └── streamlit_app_production.py
├── backend/
│   ├── init_database.py
│   └── generate_realistic_data.py
├── requirements.txt
├── README.md
└── other documentation files
```

## 🐛 Troubleshooting

### Problem: "Python not found"
```powershell
# Make sure Python is in your PATH
# Try using python3 instead
python3 --version
```

### Problem: "Permission denied" on activation script
**Windows:**
```powershell
# Run PowerShell as Administrator first
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux:**
```bash
# Make script executable
chmod +x venv/bin/activate
source venv/bin/activate
```

### Problem: "Database not found"
```bash
# Recreate the database
python backend/init_database.py
python backend/generate_realistic_data.py
```

### Problem: "ModuleNotFoundError: No module named 'streamlit'"
```bash
# Make sure venv is activated, then reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

### Problem: Streamlit won't start
```bash
# Upgrade Streamlit
pip install --upgrade streamlit

# Run with verbose output
streamlit run --logger.level=debug frontend/streamlit_app_production.py
```

### Problem: "Port 8501 already in use"
```bash
# Use a different port
streamlit run frontend/streamlit_app_production.py --server.port 8502
```

### Problem: Slow initial load
- First load takes longer (Streamlit compiling)
- Subsequent loads are faster
- Clear browser cache if very slow

## 📚 Next Steps

1. **Local Testing**: Test all features locally
2. **Explore Code**: Review the main app code
3. **Customize Data**: Modify sample data generation
4. **Deploy to Streamlit Cloud**: Follow [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🎓 Learning Resources

- **Streamlit**: https://docs.streamlit.io/
- **Pandas**: https://pandas.pydata.org/docs/
- **Plotly**: https://plotly.com/python/
- **SQLite**: https://www.sqlite.org/docs.html

## 💡 Tips & Tricks

**Deactivate Virtual Environment**
```bash
deactivate
```

**Reactivate (after closing terminal)**
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**Fresh Start (if everything breaks)**
```bash
# Delete and recreate everything
rm -rf venv database/healthcare_dashboard.db

# Then follow installation steps again
```

**Check Installed Packages**
```bash
pip list
```

**Update All Packages**
```bash
pip install --upgrade -r requirements.txt
```

---

**Installation complete!** 🎉 Head to [README.md](./README.md) for usage instructions.