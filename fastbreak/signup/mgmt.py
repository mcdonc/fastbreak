from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.sdi import mgmt_view
from substanced.service import find_service

from fastbreak.utils import make_name

from fastbreak.interfaces import (\
    IProgram,
    IRegistration,
    ISignup,
    )
from fastbreak.signup import (
    SignupSchema,
    SignupBasicPropertySheet
    )

@mgmt_view(
    context=IRegistration,
    name='add_signup',
    tab_title='Add Signup',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
@mgmt_view(
    context=IProgram,
    name='add_signup',
    tab_title='Add Signup',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddSignupView(FormView):
    title = 'Add Signup'
    schema = SignupSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        context = self.context

        # We need to find the person for the oid to make a name
        objectmap = find_service(self.context, 'objectmap')
        player = objectmap.object_for(appstruct['player'], context)
        title = player.first_name + ' ' + player.last_name
        appstruct['title'] = title

        name = make_name(title)
        reg = registry.content.create(ISignup, **appstruct)
        self.context[name] = reg
        propsheet = SignupBasicPropertySheet(reg, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(reg, '@@properties'))
