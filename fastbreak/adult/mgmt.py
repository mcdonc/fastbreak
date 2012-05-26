from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.sdi import mgmt_view
from substanced.site import ISite

from fastbreak.utils import make_name

from fastbreak.interfaces import (
    IAdult
    )
from fastbreak.adult import AdultSchema

@mgmt_view(
    context=ISite,
    name='add_adult',
    tab_title='Add Adult',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddAdultView(FormView):
    title = 'Add Adult'
    schema = AdultSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        title = appstruct['first_name'] + ' ' + appstruct['last_name']
        name = make_name(title)
        adult = registry.content.create(IAdult, **appstruct)
        self.context[name] = adult
        return HTTPFound(self.request.mgmt_path(adult, '@@properties'))
