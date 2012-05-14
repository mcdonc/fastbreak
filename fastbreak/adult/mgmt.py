from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.sdi import mgmt_view
from substanced.site import ISite

from fastbreak.utils import make_name

from fastbreak.interfaces import (
    IAdult
    )
from fastbreak.adult import (
    AdultSchema,
    AdultBasicPropertySheet
    )

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
        name = make_name(appstruct['title'])
        adult = registry.content.create(IAdult, **appstruct)
        self.context[name] = adult
        propsheet = AdultBasicPropertySheet(adult, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(adult, '@@properties'))
