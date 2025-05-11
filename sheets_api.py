from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "gskey.json"

credentials = None
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)


# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1ehUXfUaUawb7FTK3jzVjKgN3HtMZbC6e8MARF6cZOfA"


try:
    service = build("sheets", "v4", credentials=credentials)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A1:A5").execute()

    values = result.get("values", [])    
    print(values)

except HttpError as err:
    print(err)


