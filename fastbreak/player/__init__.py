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
    IAdult
    )
from fastbreak.utils import (
    PLAYERTOTEAM,
    PLAYERTOPRIMARYGUARDIAN
    )


@colander.deferred
def team_widget(node, kw):
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


@colander.deferred
def guardian_widget(node, kw):
    request = kw['request']
    search_catalog = request.search_catalog
    count, oids, resolver = search_catalog(interfaces=(IAdult,))
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
        widget=team_widget,
        missing=colander.null
    )
    primary_guardian = colander.SchemaNode(
        colander.Int(),
        widget=guardian_widget,
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

        # Need the objectid of the primary guardian
        primary_guardians = list(context.get_primary_guardianids())
        if not primary_guardians:
            primary_guardian = colander.null
        else:
            primary_guardian = primary_guardians[0]

        return dict(
            name=context.__name__,
            title=context.title,
            team=team,
            primary_guardian=primary_guardian
        )

    def set(self, struct):
        context = self.context
        context.title = struct['title']

        # Disconnect old relations, make new relations
        context.disconnect()
        context.connect_team(struct['team'])
        context.connect_primary_guardian(struct['primary_guardian'])


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
    def __init__(self, title, team, primary_guardian):
        self.title = title
        # We don't care about storing team

    def texts(self): # for indexing
        return self.title

    def get_teamids(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.targetids(self, PLAYERTOTEAM)

    def get_primary_guardianids(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.targetids(self, PLAYERTOPRIMARYGUARDIAN)

    def connect_team(self, *teams):
        objectmap = find_service(self, 'objectmap')
        for teamid in teams:
            objectmap.connect(self, teamid, PLAYERTOTEAM)

    def connect_primary_guardian(self, *primary_guardian):
        objectmap = find_service(self, 'objectmap')
        for adultid in primary_guardian:
            objectmap.connect(self, adultid, PLAYERTOPRIMARYGUARDIAN)

    def disconnect(self):
        teams = self.get_teamids()
        primary_guardian = self.get_primary_guardianids()
        objectmap = find_service(self, 'objectmap')
        for teamid in teams:
            objectmap.disconnect(self, teamid, PLAYERTOTEAM)
        for adultid in primary_guardian:
            objectmap.disconnect(self, adultid,
                                 PLAYERTOPRIMARYGUARDIAN)

    def teams(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.targets(self, PLAYERTOTEAM)
