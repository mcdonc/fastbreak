from pyramid.view import view_config

from substanced.site import ISite

from .layout import Layout


class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/siteroot_view.pt',
                 context=ISite)
    def siteroot_view(self):
        return dict(heading='Welcome to My Site')
