import colander
from deform_bootstrap.widget import ChosenSingleWidget
from persistent import Persistent

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema
from substanced.service import find_service

from fastbreak.interfaces import (
    IPlayer,
    ITeam,
    )
from fastbreak.utils import PLAYERTOTEAM


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


class PlayerSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )
    team = colander.SchemaNode(
        colander.Int(),
        widget=teams_widget,
        missing=colander.null
    )


class PlayerBasicPropertySheet(PropertySheet):
    schema = PlayerSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        # Need the objectid of the first referenced team
        teams = list(context.get_teamids())
        if not teams:
            team = colander.null
        else:
            team = teams[0]

        return dict(
            name=context.__name__,
            title=context.title,
            team=team
        )

    def set(self, struct):
        context = self.context
        context.title = struct['title']

        # Disconnect old relations, make new relations
        context.disconnect()
        context.connect(struct['team'])


@content(
    IPlayer,
    name='Player',
    icon='icon-align-left',
    add_view='add_player',
    propertysheets=(
        ('Basic', PlayerBasicPropertySheet),
        ),
    catalog=True,
    )
class Player(Persistent):
    def __init__(self, title, team):
        self.title = title
        # We don't care about storing team

    def texts(self): # for indexing
        return self.title

    def get_teamids(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.targetids(self, PLAYERTOTEAM)

    def connect(self, *teams):
        objectmap = find_service(self, 'objectmap')
        for teamid in teams:
            objectmap.connect(self, teamid, PLAYERTOTEAM)

    def disconnect(self):
        teams = self.get_teamids()
        objectmap = find_service(self, 'objectmap')
        for teamid in teams:
            objectmap.disconnect(self, teamid, PLAYERTOTEAM)

    def teams(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.targets(self, PLAYERTOTEAM)
