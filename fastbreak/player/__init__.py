import colander
from deform.widget import TextAreaWidget
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
    PLAYERTOOG,
    BaseContent
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
    first_name = colander.SchemaNode(
        colander.String(),
    )
    last_name = colander.SchemaNode(
        colander.String(),
    )
    nickname = colander.SchemaNode(
        colander.String(),
        missing=colander.null,
        )
    email = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    additional_emails = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    mobile_phone = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    note = colander.SchemaNode(
        colander.String(),
        widget=TextAreaWidget(rows=10, cols=60),
        missing=colander.null
    )
    uslax = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    is_goalie = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=colander.null,
        )
    grade = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    school = colander.SchemaNode(
        colander.String(),
        missing=colander.null
    )
    jersey_number = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    la_id = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    # References
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
        teams = context.get_relationids(PLAYERTOTEAM)
        if not teams:
            team = colander.null
        else:
            team = teams[0]

        # Need the objectid of the primary guardian
        primary_guardians = context.get_relationids(PLAYERTOPG)
        if not primary_guardians:
            primary_guardian = colander.null
        else:
            primary_guardian = primary_guardians[0]

        # Need the objectid of the other guardian
        other_guardians = context.get_relationids(PLAYERTOOG)
        if not other_guardians:
            other_guardian = colander.null
        else:
            other_guardian = other_guardians[0]

        return dict(
            name=context.__name__,
            first_name=context.first_name,
            last_name=context.last_name,
            nickname=context.nickname,
            email=context.email,
            additional_emails=context.additional_emails,
            mobile_phone=context.mobile_phone,
            note=context.note,
            uslax=context.uslax,
            is_goalie=context.is_goalie,
            grade=context.grade,
            school=context.school,
            jersey_number=context.jersey_number,
            la_id=context.la_id,
            # References
            team=team,
            primary_guardian=primary_guardian,
            other_guardian=other_guardian,
            )

    def set(self, struct):
        context = self.context
        context.first_name = struct['first_name']
        context.last_name = struct['last_name']
        context.nickname = struct['nickname']
        context.email = struct['email']
        context.additional_emails = struct['additional_emails']
        context.mobile_phone = struct['mobile_phone']
        context.note = struct['note']
        context.uslax = struct['uslax']
        context.is_goalie = struct['is_goalie']
        context.grade = struct['grade']
        context.school = struct['school']
        context.jersey_number = struct['jersey_number']
        context.la_id = struct['la_id']

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
class Player(BaseContent):

    disconnect_targets = (PLAYERTOTEAM, PLAYERTOPG, PLAYERTOOG)

    def __init__(self, first_name, last_name, nickname, email,
                     additional_emails, mobile_phone, uslax, is_goalie,
                     grade, school, jersey_number,
                     # References
                     team, primary_guardian, other_guardian,
                     note, la_id
        ):
            self.first_name = first_name
            self.last_name = last_name
            self.nickname = nickname
            self.email = email
            self.additional_emails = additional_emails
            self.mobile_phone = mobile_phone
            self.uslax = uslax
            self.is_goalie = is_goalie
            self.grade = grade
            self.school = school
            self.jersey_number = jersey_number
            self.note = note
            self.la_id = la_id
            # We don't care about storing team

    @property
    def title(self):
        return ' '.join((self.last_name, self.first_name))

    def texts(self): # for indexing
        nickname = self.nickname
        if self.nickname is colander.null:
            nickname = ''
        t = ' '.join([self.first_name, self.last_name, nickname])
        return t

    def connect_team(self, team):
        self.connect_role(PLAYERTOTEAM, team)

    def connect_primary_guardian(self, primary_guardian):
        self.connect_role(PLAYERTOPG, primary_guardian)

    def connect_other_guardian(self, other_guardian):
        self.connect_role(PLAYERTOOG, other_guardian)

    def teams(self):
        return list(self.get_targets(PLAYERTOTEAM))
