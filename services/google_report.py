from googleapiclient import discovery


class GoogleReport:
    def __init__(self, credentials) -> None:
        self.credentials = credentials
        self.title = ""
        self.headers = []
        self.email = ""
        self.rows = 0
        self.columns = 0

    def auth(self):
        service = discovery.build("sheets", "v4", credentials=self.credentials)
        return service

    def add_title(self, title):
        self.title = title
        return self

    def add_headers(self, *args):
        for arg in args:
            if len(arg) > self.columns:
                self.columns = len(arg)
            self.headers.append(arg)
        self.add_rows(len(args))
        return self

    def add_email(self, email):
        self.email = email
        return self

    def add_rows(self, num):
        self.rows += num
        return self

    def create(self):
        service = self.auth()
        spreadsheet_body = {
            "properties": {"title": self.title, "locale": "ru_RU"},
            "sheets": [
                {
                    "properties": {
                        "sheetType": "GRID",
                        "sheetId": 0,
                        "gridProperties": {
                            "rowCount": self.rows,
                            "columnCount": self.columns,
                        },
                    }
                }
            ],
            "body": self.headers,
        }

        service.spreadsheets().create(body=spreadsheet_body)
