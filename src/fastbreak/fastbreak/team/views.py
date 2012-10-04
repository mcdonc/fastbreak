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
        return []

    @view_config(renderer='templates/team_view.pt',
                 permission='view',
                 context=ITeam)
    def team_view(self):
        return dict(
            heading='Players',
            team=self.context,
            players=self.context.players(),
        )
