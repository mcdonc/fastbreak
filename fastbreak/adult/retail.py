from pyramid.url import resource_url
from pyramid.view import view_config

from substanced.site import ISite

from fastbreak.interfaces import IAdult
from fastbreak.layout import Layout

class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request


    @view_config(renderer='templates/adults_list.pt',
                 name='adults',
                 context=ISite)
    def adults_list(self):
        return dict(
            heading='Adults', adults=self.find_interface(IAdult))


    @view_config(renderer='templates/adult_view.pt',
                 context=IAdult)
    def adult_view(self):
        return dict(
            heading=self.context.title,
            players=[],
        )
