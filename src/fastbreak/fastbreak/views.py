from pyramid.view import view_config

from substanced.interfaces import IRoot

@view_config(name="griddemo", renderer="templates/demo76.pt")
def griddemo_view(context, request):
    return dict(heading="Grid Demo")


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
                title='Guardians',
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
            heading='Fastbreak',
            teams=self.context.values()
        )


    @view_config(renderer='templates/exception_view.pt',
                 context=Exception)
    def exception_view(self):
        request = self.request
        request.layout_manager.use_layout('simple')
        context = self.context
        msg_fmt = '%s: %s'
        msg = msg_fmt % (str(type(context)), context.message)

        return dict(
            heading='Oops An Error',
            msg=msg
        )
