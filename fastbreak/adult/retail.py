from pyramid.view import view_config

from substanced.site import ISite

from fastbreak.interfaces import IAdult
from fastbreak.layout import Layout

class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request


    @view_config(renderer='templates/adults_list.pt',
                 permission='view',
                 name='adults',
                 context=ISite)
    def adults_list(self):
        return dict(
            heading='Adults', adults=self.find_interface(IAdult))


    @view_config(renderer='templates/adult_view.pt',
                 permission='view',
                 context=IAdult)
    def adult_view(self):
        title = self.context.first_name + ' ' + self.context.last_name

        return dict(
            heading=title,
            players=self.context.players(),
            teams_coached=self.context.teams_managed(),
            teams_managed=self.context.teams_coached(),
            adult=self.context,
            )

