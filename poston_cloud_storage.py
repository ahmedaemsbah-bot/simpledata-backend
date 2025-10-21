import gspread
from google.oauth2.service_account import Credentials
import json

def post_stakeholder_data(stakeholder_data):

    SERVICE_ACCOUNT_FILE = "D:/Andriod_projects/simpledatateba-3a15f8b92427.json"
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SHEET_ID = "1xsf6NBAzVx_b4zXjyvHIvS37evVkoo-SCZdF6OGWfL8"
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.worksheet("stakeholders")

    # إضافة الصف الجديد
    row = [
        stakeholder_data["code"],
        stakeholder_data["name"],
        stakeholder_data["phone"],
        stakeholder_data["whatsapp"],
        stakeholder_data["email"],
        stakeholder_data["activity_type"],
        stakeholder_data["is_customer"],
        stakeholder_data["is_supplier"],
        stakeholder_data["is_employee"],
        json.dumps(stakeholder_data["customer_classes"], ensure_ascii=False),
        stakeholder_data["customer_credit_type"],
        stakeholder_data["customer_credit_limit"],
        stakeholder_data["customer_responsible_employee"],
        stakeholder_data["starting_balance"],
        stakeholder_data["is_active"],
        stakeholder_data["created_at"],
        stakeholder_data["updated_at"],
        
    ]
    sheet.append_row(row)
    print("✅ Added to Google Sheets: - poston_cloud_storage.py:37", row)
