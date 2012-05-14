from pyramid.httpexceptions import HTTPFound

from substanced.form import FormView
from substanced.schema import Schema
from substanced.sdi import mgmt_view
from substanced.site import ISite

from .interfaces import (
    IDocument,
    ITeam,
    IProgram
    )
from .resources import (\
    ProgramSchema,
    DocumentSchema,
    TeamSchema,
    DocumentBasicPropertySheet,
    TeamBasicPropertySheet,
    )

def make_name(title):
    # Policy for automatically generating unique names from titles. For
    # now, just lower and replace spaces with dashes

    name = title.replace(' ', '-').lower()
    return name

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


@mgmt_view(
    context=IProgram,
    name='add_document',
    tab_title='Add Document',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddDocumentView(FormView):
    title = 'Add Document'
    schema = DocumentSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = make_name(appstruct['title'])
        document = registry.content.create(IDocument, **appstruct)
        self.context[name] = document
        propsheet = DocumentBasicPropertySheet(document, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(document, '@@properties'))


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
        team = registry.content.create(ITeam, **appstruct)
        self.context[name] = team
        propsheet = TeamBasicPropertySheet(team, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(team, '@@properties'))


@mgmt_view(
    context=ISite,
    name='import_data',
    tab_title='Import Data',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    )
class ImportDataView(FormView):
    title = 'Import Data'
    schema = Schema()
    buttons = ('import',)

    def import_success(self, appstruct):
        root = self.request.root
        registry = self.request.registry

        # First add STORM as a program
        name = u'storm'
        appstruct = dict(title='STORM')
        storm = registry.content.create(IProgram, **appstruct)
        root[name] = storm
        propsheet = TeamBasicPropertySheet(storm, self.request)
        propsheet.set(appstruct)

        # Add some Teams
        teams = (u'Blue', u'Orange', u'White', u'Black', u'Silver')
        for title in teams:
            name = make_name(title)
            appstruct = dict(title=title)
            team = registry.content.create(ITeam, **appstruct)
            storm[name] = team
            propsheet = TeamBasicPropertySheet(team, self.request)
            propsheet.set(appstruct)

        return HTTPFound(self.request.mgmt_path(self.context,
                                                '@@contents'))