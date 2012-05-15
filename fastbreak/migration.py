# Import data into, and perhaps out of, Fastbreak.

from csv import DictReader
from os.path import join

from substanced.service import find_service

class Migration:
    def __init__(self, context, request):
        self.adults = {}
        self.players = {}
        self.guardian_ids = {}

        self.root = request.root
        context = context
        registry = request.registry
        self.import_dir = registry.settings['import_dir']
        self.objectmap = find_service(context, 'objectmap')

    def load_adults(self):
        gids = self.guardian_ids.keys()

        fn = join(self.import_dir, 'adults.csv')
        for p in DictReader(open(fn)):
            la_id = int(p['id'])
            self.adults[la_id] = p

    def load_players(self):
        fn = join(self.import_dir, 'players.csv')
        for p in DictReader(open(fn)):
            la_id = int(p['id'])
            p['guardian_ref'] = int(p['guardian_ref'])
            self.players[la_id] = p

            # Keep track of guardian ids
            self.guardian_ids[p['guardian_ref']] = None


if __name__ == '__main__':
    import_dir = '/Users/paul/projects/scratchpad/stormlax/var'
    m = Migration(import_dir)
    for team in ('Blue', 'Orange', 'White', 'Black', 'Silver'):
        m.add_team(team)
    m.load_adults()
    m.load_players()