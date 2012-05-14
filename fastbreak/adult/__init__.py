import colander
from persistent import Persistent

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema

from fastbreak.interfaces import (
    IAdult
    )


class AdultSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )


class AdultBasicPropertySheet(PropertySheet):
    schema = AdultSchema()

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
    IAdult,
    name='Adult',
    icon='icon-align-left',
    add_view='add_adult',
    propertysheets=(
        ('Basic', AdultBasicPropertySheet),
        ),
    catalog=True,
    )
class Adult(Persistent):
    def __init__(self, title):
        self.title = title

    def texts(self): # for indexing
        return self.title

