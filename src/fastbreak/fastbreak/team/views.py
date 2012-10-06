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

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def subnav_items(self):
        return []


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

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def subnav_items(self):
        return [
            dict(active='active', title='Players', url='#'),
            dict(title='Cheat Sheet', url='cheat_sheet', active=''),
            dict(title='Tournaments', url='#', active=''),
            dict(title='Actions', url='#', active=''),
            dict(title='Email List', url='emails', active='')
        ]

    @view_config(renderer='templates/team_view.pt',
                 permission='view',
                 context=ITeam)
    def team_view(self):
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

            writer.writerow(dict(
                last_name=player.last_name,
                first_name=player.first_name,
                grade=player.props['grade'],
                school=player.props['school'],
                experience=player.props['years_experience'],
                tourneys='/'.join(player.tourneys()),
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
        results = []
        for i in range(0,len(all_players)-1, 4):
            row = []
            for j in (0,1,2,3):
                try:
                    row.append(all_players[i+j])
                except IndexError:
                    continue
            results.append(row)

        return dict(
            heading=self.context.title + ' Cheat Sheet',
            all_players=results
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

        joined_comma = ', '.join(sorted(all_emails))

        return dict(
            heading=self.context.title + ' Emails',
            joined_comma=joined_comma
        )


