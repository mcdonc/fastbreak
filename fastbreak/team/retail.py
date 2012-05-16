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

    @view_config(renderer='templates/team_view.pt',
                 context=ITeam)
    def team_view(self):

        head_coach = self.context.head_coach()
        if head_coach:
            head_coach = head_coach[0]
        assistant_coach = self.context.assistant_coach()
        if assistant_coach:
            assistant_coach = assistant_coach[0]
        team_manager = self.context.team_manager()
        if team_manager:
            team_manager = team_manager[0]

        return dict(
            heading=self.context.title,
            team=self.context,
            players=self.context.players(),
            head_coach=head_coach,
            assistant_coach=assistant_coach,
            team_manager=team_manager,
            )

