import colander
from persistent import Persistent

from substanced.content import content
from substanced.folder import Folder
from substanced.property import PropertySheet
from substanced.schema import Schema

from fastbreak.interfaces import (
    IRegistration,
    IProgram
    )


class RegistrationSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )
    cost = colander.SchemaNode(
        colander.Int(),
    )


class RegistrationBasicPropertySheet(PropertySheet):
    schema = RegistrationSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        return dict(
            name=context.__name__,
            title=context.title,
            cost=context.cost,

            )

    def set(self, struct):
        context = self.context
        context.title = struct['title']
        context.cost = struct['cost']

@content(
    IRegistration,
    name='Registration',
    context=IProgram,
    icon='icon-align-right',
    add_view='add_registration',
    propertysheets=(
        ('Basic', RegistrationBasicPropertySheet),
        ),
    catalog=True,
    )
class Registration(Folder):

    def __init__(self, title, cost):
        Folder.__init__(self)
        self.title = title
        self.cost = cost

    def texts(self): # for indexing
        return self.title

