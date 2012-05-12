import colander
from pyramid.httpexceptions import HTTPFound

from substanced.site import ISite
from substanced.sdi import mgmt_view
from substanced.form import FormView

from .interfaces import (
    IDocument,
    ITopic
)
from .resources import (
    DocumentSchema,
    TopicSchema,
    DocumentBasicPropertySheet,
    TopicBasicPropertySheet,
)

name = colander.SchemaNode(
    colander.String(),
    )

@mgmt_view(
    context=ISite,
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
        name = appstruct['title']
        document = registry.content.create(IDocument, **appstruct)
        self.context[name] = document
        propsheet = DocumentBasicPropertySheet(document, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(document, '@@properties'))

@mgmt_view(
    context=ISite,
    name='add_topic',
    tab_title='Add Topic',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddTopicView(FormView):
    title = 'Add Topic'
    schema = TopicSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct['title']
        topic = registry.content.create(ITopic, **appstruct)
        self.context[name] = topic
        propsheet = TopicBasicPropertySheet(topic, self.request)
        propsheet.set(appstruct)
        return HTTPFound(self.request.mgmt_path(topic, '@@properties'))

