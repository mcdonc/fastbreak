from os import environ

import gspread
import colander

spreadsheet_keys = dict(
    tourneys = '0AheWwIghVZlTdEdlRUZlaFBha2xFd1lLMUNXeEcyMnc',
    players = '0AheWwIghVZlTdEs4QkdjMG1hRTZPY3ZvWk9IeGVEUFE',
)

fields = (
    'last_name', 'first_name', 'nickname', 'email', 'additional_emails',
    'mobile_phone', 'uslax', 'is_goalie', 'grade', 'school',
    'jersey_number', 'note',
)

def serialize(value):
    return 'None' if value == colander.null else value

class GDocSync:

    def __init__(self):
        self.un = environ['GDOC_UN']
        self.pw = environ['GDOC_PW']
        self.spreadsheets = {}
        self.gc = gspread.login(self.un, self.pw)


    def get_rows(self, spreadsheet, worksheet_ids):

        spreadsheet = self.gc.open_by_key(spreadsheet_keys[spreadsheet])

        results = {}
        for worksheet_id in worksheet_ids:
            wks = spreadsheet.worksheet(worksheet_id)
            results[worksheet_id] = wks.get_all_records()

        return results

    def init_players(self, players):
        # Initial sync of player data to spreadsheet

        spreadsheet = self.gc.open_by_key(spreadsheet_keys['players'])
        wks = spreadsheet.sheet1

        row_data = []
        for player in players:
            for field in fields:
                v = serialize(getattr(player, field))
                row_data.append(v)
            # Now the references
            team = player.teams()[0].title
            row_data.append(team)
            pg_id = player.primary_guardian()[0].la_id
            row_data.append(pg_id)
            og_id = player.all_guardians()[0].la_id
            row_data.append(og_id)
            # And housekeeping
            row_data.append(player.la_id)

        cell_list = wks.range('A2:P' + str(len(players)))
        counter = 0
        for cell in cell_list:
            cell.value = row_data[counter]
            counter = counter + 1

        wks.update_cells(cell_list)

        return

    def append_people(self, spreadsheet):

        # Given a list of rows, if the LeagueAthletics ID doesn't yet
        # exist, append a new row. Sort all the rows first based on
        # last_name first_name.

        spreadsheet = self.gc.open_by_key(spreadsheet_keys[spreadsheet])
        existing_la_ids = {}
        wks = spreadsheet.sheet1
        for row in wks.get_all_records():
            existing_la_ids[row['la_id']] = None
        existing_la_ids = existing_la_ids.keys()

        return


def main():
    un = 'paulweveritt'
    pw = environ['GDOC_PW']



if __name__ == '__main__':
    main()