from google.oauth2.service_account import Credentials
from googleapiclient import discovery
from string import ascii_uppercase


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class GoogleReport:
    def __init__(self, credentials) -> None:
        self.credentials = credentials
        self.title = ""
        self.header = []
        self.email = ""
        self.rows = []

    async def auth(self):
        credentials = Credentials.from_service_account_info(
            info=self.credentials, scopes=SCOPES)
        return await discovery.build("sheets", "v4", credentials=credentials)

    def add_title(self, title):
        self.title = title

    def add_header(self, *args):
        self.header = []
        for arg in args:
            self.header.append(arg)

    def add_email(self, email):
        self.email = email

    def add_rows(self, *args):
        for arg in args:
            self.rows.append(arg)

    async def create(self):
        service = self.auth()
        request_body = {
            'majorDimension': 'ROWS',
            'values': [self.header].extend(self.rows)
            }
        columnCount = len(max(self.header, key=lambda x: len(x)))
        spreadsheet_body = {
            "properties": {"title": self.title, "locale": "ru_RU"},
            "sheets": [
                {
                    "properties": {
                        "sheetType": "GRID",
                        "sheetId": 0,
                        "gridProperties": {
                            "rowCount": len(self.rows),
                            "columnCount": columnCount,
                        },
                    }
                }
            ],
        }
        request = await service.spreadsheets().create(body=spreadsheet_body)
        response = await request.execute()
        spreadsheet_id = response['spreadsheetId']
        request = await service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'Лист1!A1:{ascii_uppercase[columnCount-1]}{len(self.rows)}',
            valueInputOption='USER_ENTERED',
            body=request_body
        )
        await request.execute()
        return (
            'https://docs.google.com/spreadsheets/d/' +
            spreadsheet_id
            )
