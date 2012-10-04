"""Bulk load test/migration data"""

from csv import DictReader
import logging
import os
from os.path import join
import sys

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

import transaction

from fastbreak.interfaces import (
    ITeams,
    ITeam,
    IPeople,
    ICoach,
    IPlayer,
    IParent,
    ITournaments,
    ITournament)

def nameify(seq):
    return '-'.join(seq).lower()

def main(argv=sys.argv):
    if len(argv) > 4:
        cmd = os.path.basename(argv[0])
        s = 'usage: %s <config_uri> <csv_dir> <init>\n'
        print  s % cmd
        sys.exit()

    # Get arguments
    config_uri = argv[1]
    csv_dir = argv[2]
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

    team_refs = {}

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

        # Make teams from teams.csv
        for team_data in DictReader(open(join(csv_dir, 'teams.csv'))):
            external_id = int(team_data['id'])
            title = team_data['title']
            team = request.registry.content.create(
                ITeam, external_id=external_id, title=title)
            name = nameify(title.split(' '))
            teams[name] = team

            # Make it easier to associate the ref_teams in player data
            # with a team
            team_refs[external_id] = team

        # Players
        for player_data in DictReader(open(join(csv_dir,
                                                'players.csv'))):
            external_id = int(player_data['id'])
            first_name = player_data['first_name']
            last_name = player_data['last_name']

            ref_team = int(player_data['ref_team'])
            player = request.registry.content.create(
                IPlayer, external_id=external_id,
                first_name=first_name, last_name=last_name,
                team_name=ref_team, props=player_data)
            name = nameify([last_name, first_name, str(external_id)])
            people[name] = player

            # Connect the player to a team
            this_team = team_refs[ref_team]
            this_team_oid = this_team.oid
            player.connect_team_oid(this_team_oid)


if __name__ == '__main__':
    main()
    print "Done"
