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

    # assumes root['splash_pages'] was initialized in Site
    log.info('Adding top-level folders...')
    with transaction.manager:
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

        # Make teams from the teams.csv dir
        for team in DictReader(open(join(csv_dir, 'teams.csv'))):
            external_id = team['Team_ID']
            title = team['Team_Name']
            del team['Team_Password']
            new_team = request.registry.content.create(
                ITeam, external_id=external_id,
                title=title, props=team)

        # Make people from the people.csv dir
        all_team_names = set()
        all_players = []
        for player in DictReader(open(join(csv_dir, 'people.csv'))):
            external_id = player['RecordID']
            firstname = player['First Name']
            lastname = player['Last Name']
            team_name = player['Team Name']
            if team_name == '':
                print "No team for:", firstname, lastname
            new_player = request.registry.content.create(
                IPlayer, external_id=external_id,
                firstname=firstname, lastname=lastname,
                team_name=team_name,
                props=player)
            all_players.append(new_player)
            all_team_names.add(team_name)

        # Print list of players by team, sorted
        for team_name in all_team_names:
            print "==================="
            print team_name
            print "==================="
            this_team = []
            for player in all_players:
                if player.team_name == team_name:
                    this_team.append(player)

            # Sort and print full names
            new_team_titles = sorted(this_team, key=lambda p: p.title)
            for p in new_team_titles:
                print p.title

            print "\n"
            print "Email Addresses"
            print "-------------------\n"


            # Print email addresses for player and guardians
            for p in new_team_titles:
                email_set = set()
                for email in (p.props['Email'],
                              p.props['Guardian1 Email'],
                              p.props['Guardian2 Email']):
                    s1 = email.strip()
                    if s1 == '':
                        continue
                    for segment in s1.split(';'):
                        email_set.add(segment.strip())
                for e in email_set:
                    print e

            print "\n   "

        tournaments = request.registry.content.create(
            ITournaments)
        #root['tournaments'] = tournaments


if __name__ == '__main__':
    main()
    print "Done"
