from os import environ

import gspread
import colander

spreadsheet_keys = dict(
    tourneys='0AheWwIghVZlTdEdlRUZlaFBha2xFd1lLMUNXeEcyMnc',
    players='0AheWwIghVZlTdEs4QkdjMG1hRTZPY3ZvWk9IeGVEUFE',
    adults='0AheWwIghVZlTdEVQcDNUcV9aUktXZlppWWU4cldxZ3c'
)

player_fields = (
    'last_name', 'first_name', 'nickname', 'email', 'additional_emails',
    'mobile_phone', 'uslax', 'is_goalie', 'grade', 'school',
    'jersey_number', 'note',
    )

adult_fields = (
    'last_name', 'first_name', 'nickname', 'email', 'additional_emails',
    'home_phone', 'mobile_phone', 'address1', 'address2',
    'city', 'state', 'zip', 'note', 'la_id'
    )

cols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def serialize(resource, node):
    # Smart serialization

    # If schema node has a flag for relation, then we won't have a
    # value on the instance. We have to look it up.
    reference_name = getattr(node, 'relation', None)
    if reference_name:
        relations = resource.get_relationids(reference_name)
        v = ';'.join([str(i) for i in relations])
        return v

    value = getattr(resource, node.name)

    # <colander.null> -> 'None'
    if value is colander.null:
        return 'None'
    # Clean up strings
    if type(value) is str:
        return value.strip()

    # Otherwise, just hand it back
    return value


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

    def init_resources(self, wks_key, schema, resources):
        # Initial sync of data to spreadsheet

        spreadsheet = self.gc.open_by_key(spreadsheet_keys[wks_key])
        wks = spreadsheet.sheet1

        # If the spreadsheet isn't empty, bail out
        top_left = wks.acell('A1').value
        if top_left is not None:
            raise ValueError, 'Players spreadsheet is not empty'

        # Otherwise, wipe all the rows, make appropriate # of cols,
        # reserve the right number of rows
        wks.resize(rows=len(resources)+3,
                   cols=len(schema.nodes) - 1)

        # Some info about the schema nodes. Skip the first one, as it
        # is the special _csrf node used for substanced.schema
        nodes = schema.nodes[1:]
        num_cols = len(nodes)-1
        last_col = cols[num_cols]

        # Provide some header rows
        cell_list = wks.range('A1:' + last_col + '1')
        counter = 0
        for cell in cell_list:
            cell.value = nodes[counter].name
            counter += 1
        wks.update_cells(cell_list)

        # Let's write some data
        row_data = []
        for resource in resources:
            for node in nodes:
                # Get the value of the field via the node.name of this
                # schema field
                v = serialize(resource, node)
                row_data.append(v)


        cell_addr = 'A2:' + str(last_col) + str(len(resources)+1)
        print cell_addr, len(row_data)
        cell_list = wks.range(cell_addr)
        counter = 0
        for cell in cell_list:
            cell.value = row_data[counter]
            counter += 1

        wks.update_cells(cell_list)

        return

    def init_adults(self, adults):
        # Initial sync of adult data to spreadsheet

        spreadsheet = self.gc.open_by_key(spreadsheet_keys['adults'])
        wks = spreadsheet.sheet1

        row_data = []
        for adult in adults:
            for field in adult_fields:
                v = serialize(getattr(adult, field))
                row_data.append(v)

        cell_list = wks.range('A2:N' + str(len(adults)))
        counter = 0
        for cell in cell_list:
            cell.value = row_data[counter]
            counter += 1

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