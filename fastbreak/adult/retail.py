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
        adults = []

        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(IAdult,))
        all_adults = [resolver(docid) for docid in docids]
        for adult in all_adults:
            adults.append(
                    {'url': resource_url(adult,
                                         self.request),
                     'title': adult.title,
                     })

        return dict(heading='Adults', adults=adults)


    @view_config(renderer='templates/adult_view.pt',
                 context=IAdult)
    def adult_view(self):
        return dict(
            heading=self.context.title,
            players=[],
        )
