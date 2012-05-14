from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.sdi import mgmt_view
from substanced.site import ISite

from fastbreak.utils import make_name

from fastbreak.interfaces import (
    IPlayer
    )
from fastbreak.player import (\
    PlayerSchema,
    PlayerBasicPropertySheet
    )

@mgmt_view(
    context=ISite,
    name='add_player',
    tab_title='Add Player',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddPlayerView(FormView):
    title = 'Add Player'
    schema = PlayerSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = make_name(appstruct['title'])
        player = registry.content.create(IPlayer, **appstruct)
        self.context[name] = player
        propsheet = PlayerBasicPropertySheet(player, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(player, '@@properties'))
