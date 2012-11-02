from csv import DictWriter
from StringIO import StringIO

from pyramid.response import Response
from pyramid.view import view_config

from fastbreak.interfaces import (
    ITeams,
    ITeam
    )

class TeamsView(object):
    title = ''
    subnav_items = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/teams_view.pt',
                 permission='view',
                 context=ITeams)
    def teams_view(self):
        return dict(
            heading=self.context.title,
            teams=self.context.values()
        )


class TeamView(object):
    title = ''
    subnav_items = [
        dict(title='Overview', suffix='overview'),
        dict(title='Positions', suffix='positions'),
        dict(title='Contacts', suffix='contacts'),
        dict(title='FallBall Roster', suffix='tourney_fallballtourney'),
        dict(title='Recruiting Info', suffix='tourney_recruitinginfo'),
        dict(title='Cheat Sheet', suffix='cheat_sheet'),
        dict(title='Tournaments', suffix='tournaments'),
        #dict(title='Grid', suffix='grid'),
        dict(title='Email List', suffix='emails')
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/team_overview.pt',
                 name='overview',
                 permission='view',
                 context=ITeam)
    def team_overview(self):
        context = self.context

        return dict(
            heading=context.title + ' Overview',
            players=context.players(),
            head_coaches=context.head_coaches(),
            assistant_coaches=context.assistant_coaches(),
            managers=context.managers()
        )


    @view_config(renderer='templates/team_contacts.pt',
                 name='contacts',
                 permission='view',
                 context=ITeam)
    def team_contacts(self):
        csv_url = self.request.resource_url(self.context,
                                            'download_roster')
        return dict(
            heading=self.context.title + ' Contacts',
            players=self.context.players(),
            csv_url=csv_url
        )

    @view_config(renderer='templates/team_fallballtourney.pt',
                 name='tourney_fallballtourney',
                 permission='view',
                 context=ITeam)
    def team_fallballtourney(self):
        return dict(
            heading=self.context.title + ' FallBall',
            players=self.context.players(),
            hc=self.context.head_coaches()[0]
        )


    @view_config(renderer='templates/team_recruitinginfo.pt',
                 name='tourney_recruitinginfo',
                 permission='view',
                 context=ITeam)
    def team_recruitinginfo(self):
        players = sorted(
            self.context.players(),
            key=lambda p: p.grade + p.jersey_number.zfill(2)
        )
        return dict(
            heading=self.context.title + ' Recruiting',
            players=players,
            hc=self.context.head_coaches()[0]
        )


    @view_config(renderer='templates/team_grid.pt',
                 name='grid',
                 permission='view',
                 context=ITeam)
    def team_grid(self):
        json_url = self.request.resource_url(self.context,
                                             'players.json')
        csv_url = self.request.resource_url(self.context,
                                            'download_roster')
        return dict(
            heading='Players',
            team=self.context,
            players=self.context.players(),
            json_url=json_url,
            csv_url=csv_url
        )

    @view_config(name='players.json',
                 renderer='json',
                 permission='view',
                 context=ITeam
    )
    def players_json(self):
        player_data = []
        for player in self.context.players():
            player_data.append(
                dict(
                    id='id_' + str(player.external_id),
                    num=player.external_id,
                    title=player.title,
                    last_name=player.last_name,
                    first_name=player.first_name,
                    emails=player.props['emails'],
                    pinnie_size=player.props['pinnie_size'],
                    shorts_size=player.props['shorts_size'],
                    jersey_number=player.props['jersey_number'],
                )
            )
        return player_data

    @view_config(renderer='templates/team_tournaments.pt',
                 permission='view',
                 name='tournaments',
                 context=ITeam)
    def team_tournaments(self):
        request = self.request
        context = self.context

        tournaments = []
        player_ids = [p.oid for p in context.players()]
        all_tournaments = sorted(request.root['tournaments'].values(),
                                 key=lambda x: x.position)
        for tournament in all_tournaments:
            player_oids = []
            for player in tournament.players():
                if player.oid in player_ids:
                    player_oids.append(player.oid)
            t = dict(
                title=tournament.title,
                count=len(player_oids),
                player_oids=player_oids
            )
            tournaments.append(t)

        players_data = []
        for player in self.context.players():
            attending = []
            for tournament in tournaments:
                attending.append(player.oid in tournament['player_oids'])
            players_data.append(dict(
                title=player.title,
                attending=attending
            ))
        return dict(
            heading=self.context.title + ' Tournaments',
            team=self.context,
            tournaments=tournaments,
            players_data=players_data
        )


    @view_config(name='download_roster',
                 permission='view',
                 context=ITeam)
    def download_roster(self):
        fieldnames = [
            'last_name', 'first_name', 'grade', 'school', 'experience',
            'tourneys', 'emails', 'guardian1_name', 'guardian1_emails']
        output = StringIO()
        writer = DictWriter(output, fieldnames=fieldnames)
        headers = dict((n, n) for n in fieldnames)
        writer.writerow(headers)
        for player in self.context.players():
            g1 = player.guardians()[0]
            g1_last_name = g1.last_name
            g1_first_name = g1.first_name
            g1_title = g1.title
            g1_emails = ','.join(g1.emails)

            tournaments = [t.title for t in player.tournaments()]

            writer.writerow(dict(
                last_name=player.last_name,
                first_name=player.first_name,
                grade=player.grade,
                school=player.school,
                experience=player.experience,
                tourneys='/'.join(tournaments),
                emails=', '.join(player.emails),
                guardian1_name=g1_title,
                guardian1_emails=g1_emails
            ))

        fn = self.context.__name__ + '-roster.csv'
        res = Response(content_type='text/csv', )
        res.content_disposition = 'attachment;filename=%s' % fn
        res.body = output.getvalue()

        return res

    @view_config(renderer='templates/team_cheat_sheet.pt',
                 permission='view',
                 name='cheat_sheet',
                 context=ITeam)
    def cheat_sheet_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title

        all_players = self.context.players()

        # Get the players into rows of 4
        per_row = 3
        results = []
        for i in range(0, len(all_players), per_row):
            row = []
            for j in range(0, per_row):
                try:
                    row.append(all_players[i + j])
                except IndexError:
                    continue
            results.append(row)

        heading = '%s Cheat Sheet (%s Players)' % (
            self.context.title, len(all_players)
            )
        return dict(
            heading=heading,
            results=results
        )

    @view_config(renderer='templates/team_positions.pt',
                 permission='view',
                 name='positions',
                 context=ITeam)
    def positions_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title

        # Organize the players into sequences by position
        by_position = {'Attack': [], 'Midfield': [], 'Defense': [],
                       'Player': [], 'Goalie': []}

        all_players = self.context.players()
        for player in all_players:
            by_position[player.position].append(player)

        # Get the players into rows of 4
        per_row = 4
        for position, position_players in by_position.items():
            results = []
            for i in range(0, len(position_players), per_row):
                row = []
                for j in range(0, per_row):
                    try:
                        row.append(position_players[i + j])
                    except IndexError:
                        continue
                results.append(row)
                # Now that we have re-organized position_players into
            # "results" (sequences of per_row length, replace.
            by_position[position] = results

        positions = [
            dict(title='Attack', players=by_position['Attack']),
            dict(title='Midfield', players=by_position['Midfield']),
            dict(title='Defense', players=by_position['Defense']),
            dict(title='Player', players=by_position['Player']),
            dict(title='Goalie', players=by_position['Goalie']),
        ]

        heading = '%s By Position (%s Players)' % (
            self.context.title, len(all_players)
            )
        return dict(
            heading=heading,
            positions=positions,
            total_players=len(all_players)
        )


    @view_config(renderer='templates/team_emails.pt',
                 permission='view',
                 name='emails',
                 context=ITeam)
    def emails_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title

        all_emails = set()

        for p in self.context.players():
            for email in p.all_emails():
                all_emails.add(email)
                # XXX TODO revisit this, probably can do better set arithmetic
        for p in self.context.head_coaches():
            for email in p.emails:
                all_emails.add(email)
        for p in self.context.assistant_coaches():
            for email in p.emails:
                all_emails.add(email)
        for p in self.context.managers():
            for email in p.emails:
                all_emails.add(email)

        joined_comma = ', '.join(sorted(all_emails))

        return dict(
            heading=self.context.title + ' Emails',
            joined_comma=joined_comma
        )


