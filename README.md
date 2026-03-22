# NiakVolt

## Prerequisites
- Python 3.12+

# 1. Create the Virtual Environment
python -m venv venv

# 2. Activate the Virtual Environment
venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt
# OR install manually:
pip install flask minimalmodbus

# 4. Save Dependencies
pip freeze > requirements.txt

# 5. Run the Project
start.bat (Windows)
## OR directly with Python:
python app.py