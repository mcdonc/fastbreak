import colander
from deform.widget import (
    SelectWidget,
    TextAreaWidget
    )
from deform_bootstrap.widget import ChosenSingleWidget

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema

from fastbreak.interfaces import (
    IPlayer,
    ISignup,
    IRegistration
    )
from fastbreak.utils import (
    BaseContent,
    PLAYERTOSIGNUP,
    )

status_choices = (
    (0, 'Not Playing'),
    (1, 'Uknown'),
    (2, 'Maybe'),
    (3, 'Playing'),
    )

@colander.deferred
def player_widget(node, kw):
    request = kw['request']
    search_catalog = request.search_catalog
    count, oids, resolver = search_catalog(interfaces=(IPlayer,))
    values = []
    for oid in oids:
        person = resolver(oid)
        title = person.first_name + ' ' + person.last_name
        values.append(
            (str(oid), title)
        )
    return ChosenSingleWidget(values=values)


# Teams
class SignupSchema(Schema):
    status = colander.SchemaNode(
        colander.String(),
        widget=SelectWidget(values=status_choices)
    )
    player = colander.SchemaNode(
        colander.Int(),
        widget=player_widget,
        )
    note = colander.SchemaNode(
        colander.String(),
        widget=TextAreaWidget(rows=10, cols=60),
        missing=colander.null
    )


class SignupBasicPropertySheet(PropertySheet):
    schema = SignupSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        player = context.get_relationids(PLAYERTOSIGNUP)
        if not player:
            player = colander.null
        else:
            player = player[0]

        return dict(
            name=context.__name__,
            status=context.status,
            note=context.note,
            player=player,
            )

    def set(self, struct):
        context = self.context
        context.status = struct['status']
        context.note = struct['note']

        # Disconnect old relations, make new relations
        context.disconnect()
        context.connect_player(struct['player'])


@content(
    ISignup,
    name='Signup',
    icon='icon-align-left',
    add_view='add_signup',
    propertysheets=(
        ('Basic', SignupBasicPropertySheet),
        ),
    catalog=True,
    )

class Signup(BaseContent):
    disconnect_targets = (PLAYERTOSIGNUP,)

    def __init__(self, status, title, note, player=None):
        self.status = status
        self.title = title
        self.note = note
        # Don't store status etc.


    def connect_player(self, player):
        self.connect_role(PLAYERTOSIGNUP, player)

    def player(self):
        return list(self.get_targets(PLAYERTOSIGNUP))
