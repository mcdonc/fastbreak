from pyramid.view import view_config

from substanced.interfaces import IRoot

@view_config(name="griddemo", renderer="templates/demo76.pt")
def griddemo_view(request):
    return {}

class SiteView(object):
    title = ''

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def subnav_items(self):
        request = self.request
        root = request.root
        return [
            dict(
                title='Teams',
                url=request.resource_url(root, 'teams')
            ),
            dict(
                title='Players',
                url=request.resource_url(root, 'teams')
            ),
            dict(
                title='Parents',
                url=request.resource_url(root, 'teams')
            ),
            dict(
                title='Admin',
                url=request.resource_url(root, 'teams')
            ),
        ]


    @view_config(renderer='templates/site_view.pt',
                 permission='view',
                 context=IRoot)
    def site_view(self):
        return dict(
            heading='STORM Dashboard',
            teams=self.context.values()
        )
