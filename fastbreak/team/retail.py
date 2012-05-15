from pyramid.url import resource_url
from pyramid.decorator import reify
from pyramid.view import view_config

from substanced.site import ISite

from fastbreak.interfaces import ITeam
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
    def assistant_coach(self):
        ac = self.context.assistant_coach()
        if ac is not []:
            return dict(
                url=resource_url(ac[0], self.request),
                title=ac[0].title
            )
        else:
            return False

    @reify
    def team_manager(self):
        tm = self.context.team_manager()
        if tm is not []:
            return dict(
                url=resource_url(tm[0], self.request),
                title=tm[0].title
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

    def player_data(self, player):
        return dict(
            last_name=player.last_name,
            first_name=player.first_name,
            url=resource_url(player, self.request)
        )

    @view_config(renderer='templates/team_view.pt',
                 context=ITeam)
    def team_view(self):
        players = []
        for player in self.context.players():
            players.append(self.player_data(player))

        return dict(
            heading=self.context.title,
            players=players,
            )

