from pyramid.view import view_config

from substanced.file import IFile
from substanced.interfaces import IRoot

from .interfaces import (
    IPlayer,
    ICoach,
    IAssistantCoach,
    IGuardian
    )

@view_config(
    context=IFile,
    permission='view',
    )
def view_file(context, request):
    return context.get_response(request=request)

@view_config(name="griddemo", renderer="templates/demo76.pt")
def griddemo_view(context, request):
    return dict(heading="Grid Demo")


class SiteView(object):
    title = ''
    subnav_items = [
        dict(title='Teams', suffix='teams'),
        dict(title='Players', suffix='players'),
        dict(title='Guardians', suffix='guardians'),
        dict(title='Coaches', suffix='coaches'),
        dict(title='Admin', suffix='teams'),
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request


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

    def _get_people(self, iface):
        v = self.context['people'].values()
        players = [p for p in v if iface.providedBy(p)]
        return sorted(players, key=lambda p: p.title)

    @view_config(renderer='templates/players_view.pt',
                 name='players',
                 permission='view',
                 context=IRoot)
    def players_view(self):
        return dict(
            heading='Players',
            players=self._get_people(IPlayer),
        )

    @view_config(renderer='templates/guardians_view.pt',
                 name='guardians',
                 permission='view',
                 context=IRoot)
    def guardians_view(self):
        return dict(
            heading='Guardians',
            guardians=self._get_people(IGuardian),
            )

    @view_config(renderer='templates/coaches_view.pt',
                 name='coaches',
                 permission='view',
                 context=IRoot)
    def coaches_view(self):
        return dict(
            heading='Coaches',
            coaches=self._get_people(ICoach),
            )
