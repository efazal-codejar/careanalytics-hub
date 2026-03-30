import os

app_code = '''
# [COMPLETE APP CODE HERE - see below]
'''

target_file = r"C:\Users\iamer\Documents\Python\healthcare-hedis-dashboard-c\frontend\streamlit_app_production.py"
backup_file = target_file.replace('.py', '_backup.py')

try:
    if os.path.exists(target_file):
        with open(target_file, 'r') as f:
            old_content = f.read()
        with open(backup_file, 'w') as f:
            f.write(old_content)
        print(f"Backup created: {backup_file}")
    
    with open(target_file, 'w') as f:
        f.write(app_code)
    
    print(f"✅ App updated: {target_file}")
    print("\nNext: Stop streamlit (Ctrl+C) then run:")
    print("streamlit run frontend/streamlit_app_production.py")
    
except Exception as e:
    print(f"ERROR: {e}")
