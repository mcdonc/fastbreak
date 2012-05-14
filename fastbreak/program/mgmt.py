from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.sdi import mgmt_view
from substanced.site import ISite

from fastbreak.utils import make_name

from fastbreak.interfaces import (
    IProgram
    )

from fastbreak.program import ProgramSchema

@mgmt_view(
    context=ISite,
    name='add_program',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddProgramView(FormView):
    title = 'Add Program'
    schema = ProgramSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        name = make_name(appstruct['title'])
        request = self.request
        program = request.registry.content.create(IProgram,
                                                  **appstruct)
        self.context[name] = program
        loc = request.mgmt_path(self.context, name, '@@properties')
        return HTTPFound(location=loc)

