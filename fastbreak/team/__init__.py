import colander
from persistent import Persistent

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema
from substanced.service import find_service

from fastbreak.interfaces import ITeam
from fastbreak.utils import DOCUMENTTOTEAM

# Teams
class TeamSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )

class TeamBasicPropertySheet(PropertySheet):
    schema = TeamSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context
        return dict(
            name=context.__name__,
            title=context.title
        )

    def set(self, struct):
        context = self.context
        context.title = struct['title']


@content(
    ITeam,
    name='Team',
    icon='icon-align-left',
    add_view='add_team',
    propertysheets=(
        ('Basic', TeamBasicPropertySheet),
        ),
    catalog=True,
    )

class Team(Persistent):
    def __init__(self, title):
        self.title = title

    def texts(self): # for indexing
        return self.title

    def documents(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.sources(self, DOCUMENTTOTEAM)

