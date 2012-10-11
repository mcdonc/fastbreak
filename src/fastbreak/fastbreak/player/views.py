from pyramid.view import view_config

from substanced.file import IFile

from fastbreak.interfaces import IPlayer

@view_config(
    context=IFile,
    permission='view',
)
def view_file(context, request):
    return context.get_response(request=request)


class PlayerView(object):
    title = ''

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def subnav_items(self):
        return []


    @view_config(renderer='templates/player_view.pt',
                 permission='view',
                 context=IPlayer
    )
    def player_view(self):
        context = self.context
        heading = context.first_name + ' ' + context.last_name
        return dict(
            heading=heading,
            all_guardians=self.context.guardians(),
            teams=self.context.teams()
        )
