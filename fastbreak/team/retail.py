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
                 url=resource_url(context, request, 'emails')),
            ]
        return items

    @view_config(renderer='templates/team_view.pt',
                 context=ITeam)
    def team_view(self):
        return dict(
            heading=self.context.title + ' Roster',
            team=self.context,
            players=self.context.players(),
            coaches=self.context.coaches(),
            team_managers=self.context.team_managers(),
            )

    @view_config(renderer='templates/team_tournaments.pt',
                 name='tournaments',
                 context=ITeam)
    def tournaments_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title
        tourney_names = None

        # TODO Generalize this
        if team_name in ('Blue', 'Orange'):
            tourney_names = ('Southern Lacrosse', 'Nations Cup',
                             'Beach Blast Tourney', 'Beach Blast Camp',
                             'Capital Cup')
        elif team_name in ('White', 'Silver'):
            tourney_names = ('Southern Lacrosse', 'Rock the Field',
                             'Beach Blast Tourney', 'Beach Blast Camp')
        elif team_name in ('Black'):
            tourney_names = ('Southern Lacrosse', 'Sun and Surf')

        return dict(
            heading=self.context.title + ' Tournaments',
            players=self.context.players(),
            tourney_names=tourney_names
        )

    @view_config(renderer='templates/team_contacts.pt',
                 name='contact_info',
                 context=ITeam)
    def contacts_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title

        return dict(
            heading=self.context.title + ' Contacts',
            players=self.context.players(),
            )

    @view_config(renderer='templates/team_emails.pt',
                 name='emails',
                 context=ITeam)
    def emails_view(self):
        # Hard-wire the tourney names for each team
        team_name = self.context.title

        all_emails = set()
        players = self.context.players()

        for p in players:
            for email in p.all_emails():
                all_emails.add(email)

        joined_comma = ', '.join(all_emails)

        return dict(
            heading=self.context.title + ' Emails',
            players=players,
            joined_comma=joined_comma
        )