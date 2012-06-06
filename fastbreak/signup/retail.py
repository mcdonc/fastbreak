from pyramid.view import view_config

from substanced.site import ISite

from fastbreak.interfaces import ISignup
from fastbreak.layout import Layout

class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/signups_list.pt',
                 permission='view',
                 name='signups',
                 context=ISite)
    def signups_list(self):
        for p in self.find_interface(ISignup):
            p.all_emails()

        return dict(
            heading='Signups',
            players=self.find_interface(ISignup))


    @view_config(renderer='templates/signup_view.pt',
                 permission='view',
                 context=ISignup)
    def signup_view(self):
        return dict(
            heading=self.context.title,
            player=self.context,
            all_guardians=self.context.all_guardians(),
            teams=self.context.teams(),
            )

