from pyramid.view import view_config

from fastbreak.interfaces import IPlayer

class PlayerView(object):
    title = ''
    subnav_items = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

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
