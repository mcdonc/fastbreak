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
    PLAYERTOPG,
    PLAYERTOOG
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
    other_guardian = colander.SchemaNode(
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
        teams = context.get_relations(PLAYERTOTEAM)
        if not teams:
            team = colander.null
        else:
            team = teams[0]

        # Need the objectid of the primary guardian
        primary_guardians = context.get_relations(PLAYERTOPG)
        if not primary_guardians:
            primary_guardian = colander.null
        else:
            primary_guardian = primary_guardians[0]

        # Need the objectid of the other guardian
        other_guardians = context.get_relations(PLAYERTOOG)
        if not other_guardians:
            other_guardian = colander.null
        else:
            other_guardian = other_guardians[0]

        return dict(
            name=context.__name__,
            title=context.title,
            team=team,
            primary_guardian=primary_guardian,
            other_guardian=other_guardian
        )

    def set(self, struct):
        context = self.context
        context.title = struct['title']

        # Disconnect old relations, make new relations
        context.disconnect()
        context.connect_team(struct['team'])
        context.connect_primary_guardian(struct['primary_guardian'])
        context.connect_other_guardian(struct['other_guardian'])


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
    def __init__(self, title, team, primary_guardian, other_guardian):
        self.title = title
        # We don't care about storing team

    def texts(self): # for indexing
        return self.title

    def get_relations(self, relation_name):
        objectmap = find_service(self, 'objectmap')
        return list(objectmap.targetids(self, relation_name))

    def connect_team(self, *teams):
        objectmap = find_service(self, 'objectmap')
        for teamid in teams:
            objectmap.connect(self, teamid, PLAYERTOTEAM)

    def connect_primary_guardian(self, *primary_guardian):
        objectmap = find_service(self, 'objectmap')
        for adultid in primary_guardian:
            objectmap.connect(self, adultid, PLAYERTOPG)

    def connect_other_guardian(self, *other_guardian):
        objectmap = find_service(self, 'objectmap')
        for adultid in other_guardian:
            objectmap.connect(self, adultid, PLAYERTOOG)

    def disconnect(self):
        objectmap = find_service(self, 'objectmap')

        teams = self.get_relations(PLAYERTOTEAM)
        for teamid in teams:
            objectmap.disconnect(self, teamid, PLAYERTOTEAM)
        primary_guardian = self.get_relations(PLAYERTOPG)
        for adultid in primary_guardian:
            objectmap.disconnect(self, adultid, PLAYERTOPG)
        other_guardian = self.get_relations(PLAYERTOOG)
        for adultid in other_guardian:
            objectmap.disconnect(self, adultid, PLAYERTOOG)

    def teams(self):
        objectmap = find_service(self, 'objectmap')
        return objectmap.targets(self, PLAYERTOTEAM)
