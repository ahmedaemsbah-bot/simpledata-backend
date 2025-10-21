from fastapi import FastAPI , Request
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import ast
from collections import defaultdict
import json

from poston_cloud_storage import post_stakeholder_data

app = FastAPI()


SERVICE_ACCOUNT_FILE = "D:/Andriod_projects/simpledatateba-3a15f8b92427.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "1xsf6NBAzVx_b4zXjyvHIvS37evVkoo-SCZdF6OGWfL8"


class GoogleSheetService:
    def __init__(self, service_account_file: str, scopes: list, sheet_id: str):
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=scopes
        )
        self.service = build("sheets", "v4", credentials=self.credentials)
        self.sheet_id = sheet_id

    def read_data(self, range_: str):
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, range=range_
            ).execute()
            values = result.get("values", [])
            return values if values else []
        except Exception as e:
            print(f"Error reading Google Sheet: {e} - main.py:36")
            return []


############################# SEND to kotlin GET from sheets  ###################################################################################################
class SheetAnalyzer:
    def __init__(self, data):
        if not data:
            self.df = pd.DataFrame()
        else:
            headers = data[0]
            rows = data[1:]
            
            fixed_rows = []
            for row in rows:
                if len(row) < len(headers):
                    row = row + [None] * (len(headers) - len(row))
                elif len(row) > len(headers):
                    row = row[:len(headers)]
                fixed_rows.append(row)
            
            self.df = pd.DataFrame(fixed_rows, columns=headers)

    def empty(self):
        val = "No data or analysis type not recognized."
        return val
            
    def for_stakeholder_window(self,filtervalue="11111"):
        
    # current_customer_data analysis:
        current_customer_data = []
        if filtervalue:
            current_customer_data = self.df[self.df["code"] == filtervalue].to_dict(orient="records")  
            for record in current_customer_data:
                for field in ["is_customer", "is_supplier", "is_employee"]:
                    val = record.get(field)
                    if isinstance(val, str):
                        record[field] = val.upper() == "TRUE"
            if isinstance(record.get("customer_classes"), str):
                try:
                    record["customer_classes"] = json.loads(record["customer_classes"])
                except json.JSONDecodeError:
                    record["customer_classes"] = {}
                

    # customer_classes analysis:
        all_customer_classes_data =  defaultdict(set)
        for row in self.df.get("customer_classes", []):
            try:
                customer_dict = json.loads(row)
                for key, value in customer_dict.items():
                    all_customer_classes_data[key].add(value)
            except json.JSONDecodeError:
                continue
        all_customer_classes_shortlist = {k: sorted(v) for k, v in all_customer_classes_data.items()}
        
    # suplier_classes analysis:
    # employee_data analysis:
    # employees analysis:
        filtered_data = self.df[self.df["is_employee"].astype(str).str.upper() == "TRUE"]
        all_employees_list = dict(zip(filtered_data["code"], filtered_data["name"]))
        return {
            "current_stakeholder_data" :current_customer_data[0] ,
            "activity_types": [x for x in self.df["activity_type"].dropna().unique().tolist() if str(x).strip() != ""],
            "customer_classes":all_customer_classes_shortlist ,
            "customer_credit_types": [x for x in self.df["customer_credit_type"].dropna().unique().tolist() if str(x).strip() != ""],
            "all_employees": all_employees_list
            }

sheet_service = GoogleSheetService(SERVICE_ACCOUNT_FILE, SCOPES, SHEET_ID)

@app.get("/read")
def read_and_analyze(range: str = "stakeholders!A:Q" ,analysis: str = "basic",startdate: str="",enddate: str = "" , filterby: str = "", filtervalue: str = ""):

    data = sheet_service.read_data(range)
    analyzer = SheetAnalyzer(data)

    if analysis == "stakeholderwindow":
        return analyzer.for_stakeholder_window(filtervalue)
    
    else:
        return analyzer.empty()
# end of send to kotlin //
#################################### GET from kotlin POST on sheets #####################################################################################################
class Stakeholder(BaseModel):
    code: str
    name: str
    phone: str
    whatsapp: str
    email: str
    activity_type: str
    is_customer: bool
    is_supplier: bool
    is_employee: bool
    customer_classes: dict
    customer_credit_type: str
    customer_credit_limit: int
    customer_responsible_employee: str
    starting_balance: int
    is_active: bool
    created_at: str
    updated_at: str

@app.post("/add_stakeholder")
async def add_stakeholder(data: Stakeholder,request: Request):
    body = await request.json()
    print("📦 Raw JSON from Kotlin: - main.py:142", body)

    print("📥 Received: - main.py:144", data.dict())
    post_stakeholder_data(data.dict()) 
    return {"status": "success", "data": data.dict()}
    # return {"received": body}


################################################ Server #################################################################################################################
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=8080)
    uvicorn.run(app, host="192.168.1.10", port=8000)
    # uvicorn.run(app, host="0.0.0.0", port=8000)
# روابط للاختبار

# https://docs.google.com/spreadsheets/d/1xsf6NBAzVx_b4zXjyvHIvS37evVkoo-SCZdF6OGWfL8/edit?usp=sharing
# http://127.0.0.1:8080/read?range=stakeholders!A:N&analysis=stakeholderwindow
