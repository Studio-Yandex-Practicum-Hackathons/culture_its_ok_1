from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from aiogoogle.resource import GoogleAPI
from core.config import settings
from pydantic import EmailStr


async def get_google_service(credentials: ServiceAccountCreds):
    async with Aiogoogle(service_account_creds=credentials) as aiogoogle:
        yield aiogoogle


class GoogleReport:
    def __init__(self) -> None:
        self._credentials = ServiceAccountCreds(
            scopes=settings.google.scopes, **settings.google.info.model_dump()
        )
        self.title = ''
        self.header = []
        self.email = ''
        self.rows = []

    def set_title(self, title: str) -> None:
        self.title = title

    def set_header(self, *args) -> None:
        self.header.clear()
        self.header.extend(*args)

    def set_email(self, email: EmailStr) -> None:
        self.email = email

    def add_rows(self, *args) -> None:
        self.rows.extend(*args)

    async def create(self):
        self._validate_fields()

        async with Aiogoogle(
                service_account_creds=self._credentials) as aioservice:
            row_count = len(self.header) + len(self.rows)
            column_count = max(
                self._max_width(self.header), self._max_width(self.rows)
            )

            sheets_api = await aioservice.discover('sheets', 'v4')
            drive_api = await aioservice.discover('drive', 'v3')

            spreadsheet_id = await self._create_table(
                aioservice, sheets_api, row_count, column_count
            )
            await self._update_table(
                aioservice, sheets_api, spreadsheet_id, row_count, column_count
            )
            await self._set_permissions(aioservice, drive_api, spreadsheet_id)

            return settings.google.spreadsheet_url.format(spreadsheet_id)

    async def _create_table(
            self,
            aioservice: Aiogoogle,
            sheets_api: GoogleAPI,
            row_count: int,
            column_count: int
    ) -> str:
        create_body = dict(
            properties=dict(
                title=self.title,
                locale='ru_RU',
            ),
            sheets=[dict(properties=dict(
                sheetType='GRID',
                sheetId=0,
                title='Лист1',
                gridProperties=dict(
                    rowCount=row_count,
                    columnCount=column_count,
                )
            ))]
        )

        response = await aioservice.as_service_account(
            sheets_api.spreadsheets.create(json=create_body)
        )
        return response['spreadsheetId']

    async def _update_table(
            self,
            aioservice: Aiogoogle,
            sheets_api: GoogleAPI,
            spreadsheet_id: str,
            row_count: int,
            column_count: int
    ) -> None:
        update_body = dict(
            majorDimension='ROWS',
            values=self.header + self.rows
        )

        await aioservice.as_service_account(
            sheets_api.spreadsheets.values.update(
                spreadsheetId=spreadsheet_id,
                range=f'R1C1:R{row_count}C{column_count}',
                valueInputOption='USER_ENTERED',
                json=update_body
            )
        )

    async def _set_permissions(
            self,
            aioservice: Aiogoogle,
            drive_api: GoogleAPI,
            spreadsheet_id: str,
    ) -> None:
        permissions_body = dict(
            type='user',
            role='writer',
            emailAddress=self.email
        )

        await aioservice.as_service_account(
            drive_api.permissions.create(
                fileId=spreadsheet_id,
                json=permissions_body,
                fields='id'
            ))

    @staticmethod
    def _max_width(table: list) -> int:
        return len(max(table, key=lambda x: len(x)))

    def _validate_fields(self):
        if not self.title:
            msg = 'Установите заголовок для файла отчёта'
            raise ValueError(msg)

        if not self.email:
            msg = ('Установите email, которому будет предоставлен доступ к '
                   'отчёту')
            raise ValueError(msg)
