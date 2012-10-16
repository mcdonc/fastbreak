""" Convert data from LeagueAthletics CSV into Fastbreak data
"""

from csv import DictReader
import logging
import os
from os.path import join
from StringIO import StringIO
import sys

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

from substanced.file import File

import transaction

from fastbreak.interfaces import (
    ITeams,
    ITeam,
    IPeople,
    ICoach,
    IPlayer,
    IGuardian,
    ITournaments,
    ITournament)

from fastbreak.utils import (\
    HEADCOACH,
    ASSTCOACH,
    MANAGER,
    split_emails,
    nameify
    )

class Tournaments(dict):
    def __init__(self, full_path):
        f = DictReader(full_path)
        for r in DictReader(open(full_path, 'r')):
            form_id = r['form_id']
            self[form_id] = (dict(
                form_id=form_id,
                form_value=r['form_value'],
                name=r['form_value'],
                title=r['title'],
                dates=r['dates'],
                city=r['city'],
                state=r['state'],
                venue=r['venue'],
                position=int(r['position'])
            ))


class Teams(dict):
    def __init__(self, full_path):
        f = DictReader(full_path)
        for r in DictReader(open(full_path, 'r')):
            team_name = r['Team_Name']
            self[team_name] = dict(
                external_id=int(r['Team_ID']),
                title=team_name,
                position=int(r['Position']),
            )


def split_emails(emails_string):
    """ Given a string with a semi-colon-delim, split """

    data = set()
    for addr1 in emails_string.strip().split(';'):
        data.add(addr1.strip())

    return list(data)


class Members:
    """ Used only for finding the external_id on a guardian """

    def __init__(self, full_path, teams_data):
        self.players = {}
        self.guardians = {}
        self.teams_data = teams_data
        f = DictReader(full_path)
        for r in DictReader(open(full_path, 'r')):
            type = r['Type']
            external_id = int(r['RecordID'])
            # The row has the team name, for example 'STORM Blue'.
            # We need the external_id of the team.
            team_id = None
            if r['Team Name'] != '':
                team_id = self.teams_data[r['Team Name']]['external_id']
            if type == 'Player':
                player = self.make_player(r, external_id, team_id)
                self.players[external_id] = player
            elif type == 'Parent':
                guardian = self.make_guardian(r, external_id, team_id)
                self.guardians[external_id] = guardian
            else:
                raise KeyError, "Unknown 'Type': " + type

    def make_player(self, row, external_id, team_id):
        """ Given a row of CSV data, clean it up and return dict  """

        guardian_ids = []
        for g in (row['Guardian1 ID'], row['Guardian2 ID']):
            if g.strip() != '':
                guardian_ids.append(int(g.strip()))
        player = dict(
            external_id=external_id,
            first_name=row['First Name'],
            last_name=row['Last Name'],
            emails=split_emails(row['Email']),
            jersey_number=row['Jersey #'],
            grade=row['Grade'],
            cell_phone=row['Cell Phone'],
            position=row['Position'],
            school='School not listed',
            experience='Experience not listed',
            refs_team=[team_id, ],
            refs_guardians=guardian_ids,
            mobile_phone=row['Cell Phone']
        )

        return player


    def make_guardian(self, row, external_id, team_id):
        """ Given a row of CSV data, clean it up and return dict  """

        guardian = dict(
            external_id=external_id,
            first_name=row['First Name'],
            last_name=row['Last Name'],
            emails=split_emails(row['Email']),
            mobile_phone=row['Cell Phone'],
            position=row['Position'],
            refs_team=[team_id, ]
        )

        return guardian

    def link_registration_data(self, full_path, tournaments_data):
        """ Given registration CSV, update player info  """

        # The stupid CSV from LeagueAthletics has a label as the first
        # line, work around this
        lines = open(full_path, 'r').readlines()[1:]
        new_file = StringIO('\n'.join(lines))

        for r in DictReader(new_file):
            if r['Team Name'] == '':
                # We have a registrant who was not assigned to a team
                continue
            external_id = int(r['Record ID'])
            player = self.players[external_id]

            player['pinnie_size'] = r['pinnie_size']
            player['shorts_size'] = r['shorts_size']
            player['school'] = r['school']
            player['experience'] = r['years_experience']

            # Process tournaments
            player['tournaments'] = {}
            for this_tournament in tournaments_data.values():
                form_id = this_tournament['form_id']
                form_value = this_tournament['form_value']
                if r[form_id] == form_value:
                    player['tournaments'][form_id] = True


def main(argv=sys.argv):
    if len(argv) > 4:
        cmd = os.path.basename(argv[0])
        s = 'usage: %s <config_uri> <import_dir> <init>\n'
        print  s % cmd
        sys.exit()

    # Get arguments
    config_uri = argv[1]
    import_dir = argv[2]
    csv_dir = join(import_dir, 'csv')
    headshots_dir = join(import_dir, 'headshots')
    try:
        init = argv[3] == 'init'
    except IndexError:
        init = False

    # Setup the environment
    setup_logging(config_uri)
    log = logging.getLogger(__name__)
    env = bootstrap(config_uri)
    root = env['root']
    request = env['request']


    # Tournaments, Teams, Members, Coaches and Team Managers
    tournaments_data = Tournaments(join(csv_dir, 'tournaments.csv'))
    teams_data = Teams(join(csv_dir, 'teams.csv'))
    members_data = Members(join(csv_dir, 'members.csv'), teams_data)

    # Take registration data and update player data such as what
    # tournaments played in. This data is unique to a registration
    # form, isn't contained on global member data.
    members_data.link_registration_data(join(csv_dir, 'registrants.csv'),
                                        tournaments_data)

    with transaction.manager:
        # If needed, blow away existing data
        if init:
            for name in ('teams', 'people', 'tournaments'):
                if root.get(name):
                    del root[name]

            # Make top-level folders
            teams = request.registry.content.create(ITeams)
            root['teams'] = teams
            people = request.registry.content.create(IPeople)
            root['people'] = people
            tournaments = request.registry.content.create(ITournaments)
            root['tournaments'] = tournaments


        # Convenience
        teams = root['teams']
        people = root['people']
        tournaments = root['tournaments']

        # Teams
        team_refs = {} # Make it easy to find these later
        for v in teams_data.values():
            external_id = v['external_id']
            team = request.registry.content.create(
                ITeam,
                external_id=external_id,
                title=v['title'],
                props=v)
            name = nameify(v['title'].split(' '))
            teams[name] = team
            team_refs[external_id] = team

        # Tournaments
        tournament_refs = {} # Make it easy to find these later
        for v in tournaments_data.values():
            external_id = v['form_id']
            tournament = request.registry.content.create(
                ITournament,
                external_id=external_id,
                title=v['title'],
                position=v['position'],
                props=v)
            tournaments[external_id] = tournament
            tournament_refs[external_id] = tournament

        # Guardians and other adults
        guardian_refs = {} # Make it easy to find these later
        for v in members_data.guardians.values():
            external_id = v['external_id']
            first_name = v['first_name']
            last_name = v['last_name']

            name = nameify([last_name, first_name, str(external_id)])
            if name in people.keys():
                # Already exists, likely a guardian of another player
                continue

            guardian = request.registry.content.create(
                IGuardian, external_id=external_id,
                first_name=first_name, last_name=last_name,
                emails=v['emails'],
                props=v)
            people[name] = guardian
            guardian_refs[external_id] = guardian

        # Associate coaches and managers with teams
        for v in members_data.guardians.values():
            position = v['position']
            if position not in ('Coach', 'Asst Coach', 'Manager'):
                continue
            team_oids = []
            if position == 'Coach':
                role = HEADCOACH
            elif position == 'Asst Coach':
                role = ASSTCOACH
            elif position == 'Manager':
                role = MANAGER
            else:
                raise KeyError, 'Position %s is unknown' % position
            for external_id in v['refs_team']:
                team = team_refs[external_id]
                team_oids.append(team.oid)
                adult = guardian_refs[v['external_id']]
                adult.connect_role(role, team_oids)


        # Players
        for v in members_data.players.values():
            external_id = v['external_id']
            first_name = v['first_name']
            last_name = v['last_name']

            name = nameify([last_name, first_name, str(external_id)])
            player = request.registry.content.create(
                IPlayer, external_id=external_id,
                first_name=first_name, last_name=last_name,
                emails=v['emails'], jersey_number=v['jersey_number'],
                grade=v['grade'],position=v['position'],
                school=v['school'], experience=v['experience'],
                props=v)
            people[name] = player

            # Connect the player to a team
            team_oids = []
            for external_id in v['refs_team']:
                team = team_refs[external_id]
                team_oids.append(team.oid)
            player.connect_team_oids(team_oids)

            # Connect the player to guardians
            guardian_oids = []
            for external_id in v['refs_guardians']:
                guardian = guardian_refs[external_id]
                guardian_oids.append(guardian.oid)
            player.connect_guardian_oids(guardian_oids)

            # Connect the player to tournaments. Some players might be
            # in a registration with no tournaments
            if v.get('tournaments', False):
                tournament_oids = []
                for k, v in v['tournaments'].items():
                    tournament = tournament_refs[k]
                    tournament_oids.append(tournament.oid)
                player.connect_tournament_oids(tournament_oids)

            # Connect headshots
            large_fn = join(headshots_dir, '%s %s.jpg') % (last_name,
                                                           first_name)
            tb_fn = join(headshots_dir, '%s %s TB.jpg') % (last_name,
                                                           first_name)
            if os.path.exists(tb_fn):
                fileobj = open(tb_fn)
            else:
                print "No headshot for", last_name, first_name
                fileobj = open(join(headshots_dir, 'no_headshot.jpg'))
            stream = File(fileobj)
            player.add('headshot_small.jpg', stream)

    # Validations

    # Make sure we don't have any children with no parents!
    for person in root['people'].values():
        # Get the players
        if IPlayer.providedBy(person):
            if len(person.guardians()) == 0:
                print "no guardians", person.title

    # Do we have any coaches
    for person in members_data.guardians.values():
        if person['last_name'] == 'McFadden':
            print 'Coach', person['position']

    for team in root['teams'].values():
        print team.title, team.head_coaches(),\
        team.assistant_coaches(), team.managers()

    return


if __name__ == '__main__':
    main()
    print "Done"
