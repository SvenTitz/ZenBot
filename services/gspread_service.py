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

    def write_cwl_data(self, data: list, clanname: str, spreadsheet_id: str) -> str:
        sheetname = clanname + ' ' + datetime.now().strftime("%H:%M:%S")
        columns = max(len(d) for d in data)
        rows = len(data)
        startCell = 'A1'
        endCell = f'{self.__get_column_letter(columns)}{rows}'  # e.g. AD36
        range = f'{startCell}:{endCell}'

        if (spreadsheet_id is None):
            spreadsheet = self.gc.create('Zen Bot CWL Data')
            spreadsheet.share(None, perm_type='anyone', role='writer')
        else:
            spreadsheet = self.gc.open_by_key(spreadsheet_id)

        sheet = spreadsheet.add_worksheet(sheetname, rows, columns)
        sheet.update(range, data)

        # sort by TH, then player name
        sheet.sort((2, 'asc'), (1, 'asc'))
        return sheet.url

    """
    converts a number into a spreadsheet column name.
    for example: __get_column_letter(29) -> 'AD'
    """
    def __get_column_letter(self, number: int) -> str:
        d, m = divmod(number, 26)
        return '' if number < 0 else self.__get_column_letter(d-1)+chr(m+65)
