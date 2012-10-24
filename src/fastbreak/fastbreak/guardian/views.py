from pyramid.view import view_config

from fastbreak.interfaces import IGuardian

class GuardianView(object):
    title = ''
    subnav_items = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/guardian_view.pt',
                 permission='view',
                 context=IGuardian
    )
    def guardian_view(self):
        context = self.context
        heading = context.first_name + ' ' + context.last_name
        return dict(
            heading=heading,
            all_players=self.context.players()
        )
