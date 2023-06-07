import gspread
import os
import json
from datetime import datetime


class Gspread_Service():
    def __init__(self) -> None:
        with open(
            f"{os.path.realpath(os.path.dirname(__file__))}/../config.json"
        ) as file:
            data = json.load(file)
        self.gc = gspread.service_account(data['path_to_google_credentials'])
        pass

    def test(self, data: list, spreadsheet_id: str) -> None:
        sheet = self.gc.open_by_key(spreadsheet_id).add_worksheet(datetime.now().strftime("%H:%M:%S"), 100, 100)
        sheet.update(f'A1:AK{len(data)}', data)
        sheet.sort((2, 'asc'), (1, 'asc'))
