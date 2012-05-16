from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.sdi import mgmt_view

from fastbreak.utils import make_name

from fastbreak.interfaces import (
    IRegistration,
    IProgram,
)
from fastbreak.registration import (
    RegistrationSchema,
    RegistrationBasicPropertySheet
    )

@mgmt_view(
    context=IProgram,
    name='add_registration',
    tab_title='Add Registration',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddRegistrationView(FormView):
    title = 'Add Registration'
    schema = RegistrationSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = make_name(appstruct['title'])
        reg = registry.content.create(IRegistration, **appstruct)
        self.context[name] = reg
        propsheet = RegistrationBasicPropertySheet(reg, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(reg, '@@properties'))
