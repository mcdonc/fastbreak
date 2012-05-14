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
    def head_coach(self):
        hc = self.context.head_coach()
        if hc is not []:
            return dict(
                url=resource_url(hc[0], self.request),
                title=hc[0].title
            )
        else:
            return False

    @reify
    def subnav_items(self):
        context = self.context
        request = self.request
        items = [
            dict(title='Roster',
                 url=resource_url(context, request)),
            dict(title='Tournaments',
                 url=resource_url(context, request, 'tournaments')),
            dict(title='Contact Info',
                 url=resource_url(context, request, 'contact_info')),
            dict(title='Email Team',
                 url=resource_url(context, request, 'email_team')),
            ]
        return items

    @view_config(renderer='templates/teams_list.pt',
                 name='teams',
                 context=ISite)
    def teams_list(self):

        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(ITeam,))
        all_teams = [resolver(docid) for docid in docids]

        teams = []
        for team in all_teams:
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

