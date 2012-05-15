from pyramid.view import view_config

from substanced.site import ISite

from fastbreak.interfaces import IPlayer
from fastbreak.layout import Layout

class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/players_list.pt',
                 name='players',
                 context=ISite)
    def players_list(self):

        return dict(
            heading='Players', players=self.find_interface(IPlayer))


    @view_config(renderer='templates/player_view.pt',
                 context=IPlayer)
    def player_view(self):
        title = self.context.first_name + ' ' + self.context.last_name
        teams = []
        for team in self.context.teams():
            teams.append(
                    {'url': resource_url(team, self.request),
                     'title': team.title,
                     })

        return dict(
            heading=title,
            teams=teams,
            player=self.context,
            )

