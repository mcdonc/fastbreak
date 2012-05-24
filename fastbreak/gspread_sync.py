import gspread
from os import environ

spreadsheet_keys = dict(
    tourneys = '0AheWwIghVZlTdEdlRUZlaFBha2xFd1lLMUNXeEcyMnc',
)
class GDocSync:

    def __init__(self):
        self.un = environ['GDOC_UN']
        self.pw = environ['GDOC_PW']
        self.spreadsheets = {}

    def get_rows(self, spreadsheet, worksheet_ids):

        gc = gspread.login(self.un, self.pw)
        spreadsheet = gc.open_by_key(spreadsheet_keys[spreadsheet])

        results = {}
        for worksheet_id in worksheet_ids:
            wks = spreadsheet.worksheet(worksheet_id)
            results[worksheet_id] = wks.get_all_records()

        return results

def main():
    un = 'paulweveritt'
    pw = environ['GDOC_PW']



if __name__ == '__main__':
    main()