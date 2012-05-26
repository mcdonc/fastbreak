# Import data into, and perhaps out of, Fastbreak.

from csv import DictReader
from os.path import join

import colander

from substanced.service import find_service

class Registration:
    def __init__(self, name, title, cost):
        self.oid = None
        self.name = name
        self.title = title
        self.cost = cost


# Some Registrations
regs = {}
for reg in (
#    ('Uniforms', 180, 'uniforms'),
#    ('Fall/Full Season 2012 ', 765, 'full_fall_season'),
#    ('Fall Season 2012', 300, 'fall_season'),
#    ('Full Season 2012', 550, 'full_season'),
#    ('Short Season Blue/Orange/White 2012', 300, 'short_bow'),
#    ('Short Season Silver 2012', 320, 'short_silver'),
#    ('Short Season Black 2012', 270, 'short_black'),
    ('Southern Lax', 85, 'so_lax'),
    ('Nations Cup', 150, 'nations_cup'),
    ('Beach Blast Tourney', 130, 'beach_tourney'),
    ('Beach Blast Camp', 100, 'beach_camp'),
    ('Capital Cup', 140, 'capital_cup'),
    ('Rock The Field', 150, 'rock_field'),
    ('Sun and Surf', 100, 'sun_surf')
    ):
    r = Registration(reg[2], reg[0], reg[1])
    regs[reg[2]] = r


class Migration:
    def __init__(self, context, request):
        self.adults = {}
        self.players = {}
        self.guardian_ids = set()
        self.signups = []

        self.root = request.root
        context = context
        registry = request.registry
        self.import_dir = registry.settings['import_dir']
        self.objectmap = find_service(context, 'objectmap')

    def load_adults(self):
        fn = join(self.import_dir, 'adults.csv')
        for p in DictReader(open(fn)):
            la_id = int(p['id'])
            self.adults[la_id] = p

    def load_players(self):
        fn = join(self.import_dir, 'players.csv')
        for p in DictReader(open(fn)):
            # Massage some integer values
            for attr in ('uslax', 'grade', 'guardian_ref', 'id',
                'jersey_number'):
                try:
                    new_value = int(p[attr])
                except ValueError:
                    new_value = colander.null
                p[attr] = new_value

            # Massage some boolean values
            if p['is_goalie'] == 'TRUE':
                p['is_goalie'] = True
            else:
                p['is_goalie'] = False

            la_id = p['id']
            self.players[la_id] = p


            # Keep track of guardian ids
            self.guardian_ids.add(p['guardian_ref'])

    def load_registrations(self):
        fn = join(self.import_dir, 'registrations.csv')
        for r in DictReader(open(fn)):
            player_ref = int(r['player_ref'])
            event_ref = r['event_ref']
            status = r['status']
            if status == 'Checked':
                status = 3
            else:
                status = 0
            balance = int(r['balance'])
            self.signups.append(dict(
                player_ref=player_ref,
                event_ref=event_ref,
                status=status,
                balance=balance
            ))
