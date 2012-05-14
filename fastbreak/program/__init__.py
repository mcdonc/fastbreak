import colander
from persistent import Persistent

from substanced.content import content
from substanced.folder import Folder
from substanced.property import PropertySheet
from substanced.schema import Schema

from fastbreak.interfaces import IProgram

class ProgramSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )

class ProgramBasicPropertySheet(PropertySheet):
    schema = ProgramSchema()

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
    IProgram,
    name='Program',
    icon='icon-align-left',
    add_view='add_program',
    propertysheets=(
        ('Basic', ProgramBasicPropertySheet),
        ),
    catalog=True,
    )
class Program(Folder):
    def __init__(self, title):
        Folder.__init__(self)
        self.title = title
