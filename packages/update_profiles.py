import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Path to your JSON key file
SERVICE_ACCOUNT_FILE = "service_account_key.json"

# Authenticate and connect to Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_ID = "1A5F00GuoiQ0KtqVjA5TNG4gFVmF1AQ6FEpdXY2OB6EI"
sheet = client.open_by_key(SHEET_ID).sheet1

# Get all data
data = sheet.get_all_records()

# Convert to Pandas DataFrame (optional, for easier handling)
df = pd.DataFrame(data)

# Save as CSV file
df.to_csv("form_responses.csv", index=False)

print("Downloaded latest form responses.")