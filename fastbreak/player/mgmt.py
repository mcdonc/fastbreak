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
        title = appstruct['first_name'] + ' ' + appstruct['last_name']
        name = make_name(title)
        teams = appstruct.pop('teams')
        primary_guardian = appstruct.pop('primary_guardian')
        other_guardians = appstruct.pop('other_guardians')
        player = registry.content.create(IPlayer, **appstruct)
        self.context[name] = player
        player.connect_all(dict(
            teams=teams, primary_guardian=primary_guardian,
            other_guardians=other_guardians
        ))
        return HTTPFound(self.request.mgmt_path(player, '@@properties'))


@mgmt_view(
    context=IPlayer,
    name='update_dues',
    tab_title='Update Dues',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class UpdateDuesView(FormView):
    title = 'Edit Dues'
    schema = PlayerSchema()
    buttons = ('update',)

    def add_success(self, appstruct):
        registry = self.request.registry
        title = appstruct['first_name'] + ' ' + appstruct['last_name']
        name = make_name(title)
        player = registry.content.create(IPlayer, **appstruct)
        self.context[name] = player
        propsheet = PlayerBasicPropertySheet(player, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(player, '@@properties'))
