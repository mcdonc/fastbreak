import colander
from deform import Set
from deform.widget import (
    TextAreaWidget,
    SelectWidget
    )
from deform_bootstrap.widget import ChosenSingleWidget
from deform_bootstrap.widget import ChosenMultipleWidget
from persistent import Persistent

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema

from fastbreak.interfaces import (
    IPlayer,
    ITeam,
    IAdult
    )
from fastbreak.utils import (
    PLAYERTOTEAM,
    PLAYERTOPG,
    PLAYERTOOG,
    PLAYERTOSIGNUP,
    BaseContent,
    dues_choices
    )


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
    return ChosenMultipleWidget(values=values)


@colander.deferred
def one_adult_widget(node, kw):
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


@colander.deferred
def multiple_adult_widget(node, kw):
    request = kw['request']
    search_catalog = request.search_catalog
    count, oids, resolver = search_catalog(interfaces=(IAdult,))
    values = []
    for oid in oids:
        title = resolver(oid).title
        values.append(
            (str(oid), title)
        )
    return ChosenMultipleWidget(values=values)


class PlayerSchema(Schema):
    first_name = colander.SchemaNode(
        colander.String(),
    )
    last_name = colander.SchemaNode(
        colander.String(),
    )
    dues_paid = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    uniform_paid = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    note = colander.SchemaNode(
        colander.String(),
        widget=TextAreaWidget(rows=10, cols=60),
        missing=colander.null
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
    teams = colander.SchemaNode(
        Set(allow_empty=True),
        widget=teams_widget,
        missing=colander.null,
        preparer=lambda users: set(map(int, users)),
        relation=PLAYERTOTEAM
    )
    primary_guardian = colander.SchemaNode(
        colander.Int(),
        widget=one_adult_widget,
        missing=colander.null,
        relation=PLAYERTOPG
    )
    other_guardians = colander.SchemaNode(
        Set(allow_empty=True),
        widget=multiple_adult_widget,
        missing=colander.null,
        preparer=lambda users: set(map(int, users)),
        relation=PLAYERTOOG
    )


class PlayerBasicPropertySheet(PropertySheet):
    schema = PlayerSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        teams = map(str, context.get_relationids(PLAYERTOTEAM))

        # Need the objectid of the primary guardian
        primary_guardians = context.get_relationids(PLAYERTOPG)
        if not primary_guardians:
            primary_guardian = colander.null
        else:
            primary_guardian = primary_guardians[0]

        # Need the objectid of the other guardian
        other_guardians = map(str, context.get_relationids(PLAYERTOOG))

        return dict(
            name=context.__name__,
            first_name=context.first_name,
            last_name=context.last_name,
            dues_paid=context.dues_paid,
            uniform_paid=context.uniform_paid,
            note=context.note,
            nickname=context.nickname,
            email=context.email,
            additional_emails=context.additional_emails,
            mobile_phone=context.mobile_phone,
            uslax=context.uslax,
            is_goalie=context.is_goalie,
            grade=context.grade,
            school=context.school,
            jersey_number=context.jersey_number,
            la_id=context.la_id,
            # References
            teams=teams,
            primary_guardian=primary_guardian,
            other_guardians=other_guardians,
            )

    def set(self, struct):
        context = self.context
        context.first_name = struct['first_name']
        context.last_name = struct['last_name']
        context.dues_paid = struct['dues_paid']
        context.uniform_paid = struct['uniform_paid']
        context.note = struct['note']
        context.nickname = struct['nickname']
        context.email = struct['email']
        context.additional_emails = struct['additional_emails']
        context.mobile_phone = struct['mobile_phone']
        context.uslax = struct['uslax']
        context.is_goalie = struct['is_goalie']
        context.grade = struct['grade']
        context.school = struct['school']
        context.jersey_number = struct['jersey_number']
        context.la_id = struct['la_id']

        context.connect_all(struct)


class DuesSchema(Schema):
    registration = colander.SchemaNode(
        colander.String(),
        widget=SelectWidget(values=dues_choices),
        missing=colander.null
    )
    balance = colander.SchemaNode(
        colander.Int(),
        missing=colander.null
    )
    dues_note = colander.SchemaNode(
        colander.String(),
        widget=TextAreaWidget(rows=10, cols=60),
        missing=colander.null
    )


class PlayerDuesPropertySheet(PropertySheet):
    schema = DuesSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        return dict(
            registration=context.registration,
            balance=context.balance,
            dues_note=context.dues_note
        )

    def set(self, struct):
        context = self.context
        context.registration = struct['registration']
        context.balance = struct['balance']
        context.dues_note = struct['dues_note']


@content(
    IPlayer,
    name='Player',
    icon='icon-align-left',
    add_view='add_player',
    propertysheets=(
        ('Basic', PlayerBasicPropertySheet),
        ('Dues', PlayerDuesPropertySheet)
        ),
    catalog=True,
    )
class Player(BaseContent):
    disconnect_targets = (PLAYERTOTEAM, PLAYERTOPG, PLAYERTOOG)

    def __init__(self, first_name, last_name,
                 note, dues_paid, uniform_paid,
                 nickname, email,
                 additional_emails, mobile_phone, uslax, is_goalie,
                 grade, school, jersey_number, la_id):
        self.first_name = first_name
        self.last_name = last_name
        self.dues_paid = dues_paid
        self.uniform_paid = uniform_paid
        self.note = note
        self.nickname = nickname
        self.email = email
        self.additional_emails = additional_emails
        self.mobile_phone = mobile_phone
        self.uslax = uslax
        self.is_goalie = is_goalie
        self.grade = grade
        self.school = school
        self.jersey_number = jersey_number
        self.la_id = la_id

        # Some stuff from the other property sheet
        self.registration = colander.null
        self.balance = colander.null
        self.dues_note = colander.null

    @property
    def title(self):
        return ' '.join((self.last_name, self.first_name))

    def texts(self): # for indexing
        nickname = self.nickname
        if self.nickname is colander.null:
            nickname = ''
        t = ' '.join([self.first_name, self.last_name, nickname])
        return t

    def connect_all(self, struct):
        # Disconnect old relations, make new relations
        self.disconnect()

        for team_oid in struct['teams']:
            self.connect_role(PLAYERTOTEAM, team_oid)
        self.connect_role(PLAYERTOPG, struct['primary_guardian'])
        for other_guardian_oid in struct['other_guardians']:
            self.connect_role(PLAYERTOOG, other_guardian_oid)

    def connect_team(self, team):
        self.connect_role(PLAYERTOTEAM, team)

    def connect_primary_guardian(self, primary_guardian):
        self.connect_role(PLAYERTOPG, primary_guardian)

    def connect_other_guardian(self, other_guardian):
        self.connect_role(PLAYERTOOG, other_guardian)

    def teams(self):
        return self.get_targets(PLAYERTOTEAM)

    def primary_guardian(self):
        return list(self.get_targets(PLAYERTOPG))[0]

    def all_guardians(self):
        return self.get_targets(PLAYERTOPG) +\
               self.get_targets(PLAYERTOOG)

    def signups(self):
        # Unpack this player's signups into a dict
        all_signups = {}
        for s in self.get_sources(PLAYERTOSIGNUP):
            reg = s.registration()
            all_signups[reg.__name__] = s
        return all_signups

    def player_emails(self):
        """Make a unique list of all email addresses"""
        emails = set()
        if self.email:
            for email in self.email.strip().split(';'):
                emails.add(email.strip())
        if self.additional_emails:
            for email in self.email.strip().split(';'):
                emails.add(email.strip())
        return emails

    def guardians_emails(self):
        emails = set()
        for guardian in self.all_guardians():
            for email in guardian.adult_emails():
                emails.add(email)

        return emails

    def primary_email(self):
        """If player has an email address, use it, else guardian"""

        email = self.email
        if email:
            return email.strip().split(';')[0].strip()
        email = self.additional_emails
        if email:
            return email.strip().split(';')[0].strip()

        # Let's hope the primary guardian has one
        return self.primary_guardian().primary_email()


    def all_emails(self):
        """For a player, return a unique list of split-up email
        addresses for player and primary guardian,
        including additional email address"""

        return self.player_emails() | self.guardians_emails()