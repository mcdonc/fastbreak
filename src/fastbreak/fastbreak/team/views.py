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
            dict(title='Tournaments', url='#', active=''),
            dict(title='Actions', url='#', active=''),
            dict(title='Email List', url='#', active='')
        ]

    @view_config(renderer='templates/team_view.pt',
                 permission='view',
                 context=ITeam)
    def team_view(self):
        json_url = self.request.resource_url(self.context,
                                             'players.json')
        return dict(
            heading='Players',
            team=self.context,
            players=self.context.players(),
            json_url=json_url
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