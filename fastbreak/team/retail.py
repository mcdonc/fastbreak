from pyramid.url import resource_url
from pyramid.decorator import reify
from pyramid.view import view_config

from substanced.site import ISite

from fastbreak.interfaces import (
    ITeam
    )
from fastbreak.layout import Layout


class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def all_teams(self):
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(ITeam,))
        return [resolver(docid) for docid in docids]


    @view_config(renderer='templates/teams_list.pt',
                 name='teams',
                 context=ISite)
    def teams_list(self):
        teams = []
        for team in self.all_teams:
            teams.append(
                    {'url': resource_url(team,
                                         self.request),
                     'title': team.title,
                     })

        return dict(heading='My Teams', teams=teams)

    @view_config(renderer='templates/team_view.pt',
                 context=ITeam)
    def team_view(self):
        players = []
        for player in self.context.players():
            players.append(
                    {'url': resource_url(player,
                                         self.request),
                     'title': player.title,
                     })

        return dict(
            heading=self.context.title,
            players=players,
            )

