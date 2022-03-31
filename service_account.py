import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def create_keyfile_dict():
    variables_keys = {
        "type": os.environ.get("SHEET_TYPE"),
        "project_id": os.environ.get("SHEET_PROJECT_ID"),
        "private_key_id": os.environ.get("SHEET_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("SHEET_PRIVATE_KEY"),
        "client_email": os.environ.get("SHEET_CLIENT_EMAIL"),
        "client_id": os.environ.get("SHEET_CLIENT_ID"),
        "auth_uri": os.environ.get("SHEET_AUTH_URI"),
        "token_uri": os.environ.get("SHEET_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.environ.get("SHEET_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.environ.get("SHEET_CLIENT_X509_CERT_URL")
    }
    return variables_keys

class Spreadsheet:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']  # define the scope
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), scope)  # account credentials
    client = gspread.authorize(credentials)  # authorize clientsheet

    sheet = None  # Specific sheet in CSV file

    # Grab the name of spreadsheet on init
    def __init__(self, sheet_name, sheet_page):
        self.sheet_name = sheet_name
        self.open_sheet(sheet_page)

    # Open spreadsheet for editing and parsing
    def open_sheet(self, sheet_page):
        try:
            self.sheet = self.client.open(self.sheet_name).worksheet(sheet_page)
            print(f'Opened sheet: {self.sheet_name}')
        except gspread.SpreadsheetNotFound:
            print('Spreadsheet does not exist.')