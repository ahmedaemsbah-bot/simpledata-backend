from fastapi import FastAPI
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = FastAPI()

# تحميل مفتاح الخدمة
SERVICE_ACCOUNT_FILE = "D:/Andriod_projects/simpledatateba-3a15f8b92427.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=credentials)

SHEET_ID = "1xsf6NBAzVx_b4zXjyvHIvS37evVkoo-SCZdF6OGWfL8"


# 🟢 جلب أسماء جميع الأوراق داخل الملف
@app.get("/sheets")
def list_sheets():
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheets = sheet_metadata.get("sheets", [])
    sheet_names = [s["properties"]["title"] for s in sheets]
    return {"sheets": sheet_names}


# 🟢 قراءة بيانات من ورقة معينة (اسم الورقة + المدى)
@app.get("/read")
def read_sheet(range: str):
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=range
    ).execute()
    values = result.get("values", [])
    return {"data": values}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)