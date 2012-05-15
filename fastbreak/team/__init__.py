import colander
from deform_bootstrap.widget import ChosenSingleWidget

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema
from substanced.service import find_service

from fastbreak.interfaces import (
    IAdult,
    ITeam
    )
from fastbreak.utils import (
    BaseContent,
    PLAYERTOTEAM,
    HEADCOACHTTOTEAM,
    ASSISTANTCOACHTTOTEAM,
    MANAGERTOTEAM
    )

@colander.deferred
def adult_widget(node, kw):
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


# Teams
class TeamSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )
    head_coach = colander.SchemaNode(
        colander.Int(),
        widget=adult_widget,
        missing=colander.null
    )
    assistant_coach = colander.SchemaNode(
        colander.Int(),
        widget=adult_widget,
        missing=colander.null
    )
    team_manager = colander.SchemaNode(
        colander.Int(),
        widget=adult_widget,
        missing=colander.null
    )


class TeamBasicPropertySheet(PropertySheet):
    schema = TeamSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        head_coach = context.get_relationids(HEADCOACHTTOTEAM)
        if not head_coach:
            head_coach = colander.null
        else:
            head_coach = head_coach[0]

        assistant_coach = context.get_relationids(ASSISTANTCOACHTTOTEAM)
        if not assistant_coach:
            assistant_coach = colander.null
        else:
            assistant_coach = assistant_coach[0]

        team_manager = context.get_relationids(MANAGERTOTEAM)
        if not team_manager:
            team_manager = colander.null
        else:
            team_manager = team_manager[0]

        return dict(
            name=context.__name__,
            title=context.title,
            head_coach=head_coach,
            assistant_coach=assistant_coach,
            team_manager=team_manager
        )

    def set(self, struct):
        context = self.context
        context.title = struct['title']

        # Disconnect old relations, make new relations
        context.disconnect()
        context.connect_head_coach(struct['head_coach'])
        context.connect_assistant_coach(struct['assistant_coach'])
        context.connect_team_manager(struct['team_manager'])


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

class Team(BaseContent):
    disconnect_targets = (HEADCOACHTTOTEAM, ASSISTANTCOACHTTOTEAM,
                          MANAGERTOTEAM)

    def __init__(self, title, head_coach=None,
                 assistant_coach=None, team_manager=None):
        self.title = title
        # Don't store head_coach etc.

    def connect_head_coach(self, head_coach):
        self.connect_role(HEADCOACHTTOTEAM, head_coach)

    def connect_assistant_coach(self, assistant_coach):
        self.connect_role(ASSISTANTCOACHTTOTEAM, assistant_coach)

    def connect_team_manager(self, assistant_coach):
        self.connect_role(MANAGERTOTEAM, assistant_coach)

    def players(self):
        return list(self.get_sources(PLAYERTOTEAM))

    def head_coach(self):
        return list(self.get_targets(HEADCOACHTTOTEAM))

    def assistant_coach(self):
        return list(self.get_targets(ASSISTANTCOACHTTOTEAM))

    def team_manager(self):
        return list(self.get_targets(MANAGERTOTEAM))
