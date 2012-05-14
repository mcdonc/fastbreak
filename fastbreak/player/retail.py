from pyramid.url import resource_url
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
        players = []

        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(IPlayer,))
        all_players = [resolver(docid) for docid in docids]
        for player in all_players:
            players.append(
                    {'url': resource_url(player,
                                         self.request),
                     'title': player.title,
                     })

        return dict(heading='Players', players=players)


    @view_config(renderer='templates/player_view.pt',
                 context=IPlayer)
    def player_view(self):
        return dict(
            heading=self.context.title,
            teams=self.context.teams()
        )

