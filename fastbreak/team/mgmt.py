from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.sdi import mgmt_view

from fastbreak.interfaces import (
    ITeam,
    IProgram
    )

from fastbreak.team import (
    TeamSchema,
    TeamBasicPropertySheet
)

from fastbreak.utils import make_name

@mgmt_view(
    context=IProgram,
    name='add_team',
    tab_title='Add Team',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddTeamView(FormView):
    title = 'Add Team'
    schema = TeamSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = make_name(appstruct['title'])
        coaches = appstruct.pop('coaches')
        team_managers = appstruct.pop('team_managers')
        team = registry.content.create(ITeam, **appstruct)
        self.context[name] = team
        team.connect_all(dict(coaches=coaches,
                              team_managers=team_managers))
        return HTTPFound(self.request.mgmt_path(team, '@@properties'))
