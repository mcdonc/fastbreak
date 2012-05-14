import colander
import deform.widget
from deform_bootstrap.widget import ChosenSingleWidget
from persistent import Persistent

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema
from substanced.service import find_service

from fastbreak.interfaces import (
    IDocument,
    ITeam,
    )
from fastbreak.utils import DOCUMENTTOTEAM


@colander.deferred
def teams_widget(node, kw):
    request = kw['request']
    search_catalog = request.search_catalog
    count, oids, resolver = search_catalog(interfaces=(ITeam,))
    values = []
    for oid in oids:
        title = resolver(oid).title
        values.append(
            (str(oid), title)
        )
    return ChosenSingleWidget(values=values)


class DocumentSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget(),
    )
    team = colander.SchemaNode(
        colander.Int(),
        widget=teams_widget,
        missing=colander.null
    )


class DocumentBasicPropertySheet(PropertySheet):
    schema = DocumentSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        # Need the objectid of the first referenced team
        teams = context.get_relations(DOCUMENTTOTEAM)
        if not teams:
            team = colander.null
        else:
            team = teams[0]

        return dict(
            name=context.__name__,
            title=context.title,
            body=context.body,
            team=team
        )

    def set(self, struct):
        context = self.context
        context.title = struct['title']
        context.body = struct['body']

        # Disconnect old relations, make new relations
        context.disconnect()
        context.connect(struct['team'])


@content(
    IDocument,
    name='Document',
    icon='icon-align-left',
    add_view='add_document',
    propertysheets=(
        ('Basic', DocumentBasicPropertySheet),
        ),
    catalog=True,
    )
class Document(Persistent):
    def __init__(self, title, body, team):
        self.title = title
        self.body = body
        self.team = team

    def texts(self): # for indexing
        return self.title, self.body

    def get_relations(self, relation_name):
        objectmap = find_service(self, 'objectmap')
        return list(objectmap.targetids(self, relation_name))

    def connect(self, *teams):
        objectmap = find_service(self, 'objectmap')
        for teamid in teams:
            objectmap.connect(self, teamid, DOCUMENTTOTEAM)

    def disconnect(self):
        teams = self.get_relations(DOCUMENTTOTEAM)
        objectmap = find_service(self, 'objectmap')
        for teamid in teams:
            objectmap.disconnect(self, teamid, DOCUMENTTOTEAM)

    def teams(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.targets(self, DOCUMENTTOTEAM)
