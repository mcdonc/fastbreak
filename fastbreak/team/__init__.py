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
def team_widget(node, kw):
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
        widget=team_widget,
        missing=colander.null
    )


class TeamBasicPropertySheet(PropertySheet):
    schema = TeamSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        # Need the objectid of the first referenced team
        head_coach = context.get_relationids(HEADCOACHTTOTEAM)
        if not head_coach:
            head_coach = colander.null
        else:
            head_coach = head_coach[0]
        return dict(
            name=context.__name__,
            title=context.title,
            head_coach=head_coach
        )

    def set(self, struct):
        context = self.context
        context.title = struct['title']

        # Disconnect old relations, make new relations
        context.disconnect()
        context.connect_head_coach(struct['head_coach'])


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
    disconnect_targets = (HEADCOACHTTOTEAM,)

    def __init__(self, title, head_coach=None):
        self.title = title
        # Don't store head_coach etc.

    def connect_head_coach(self, *head_coach):
        objectmap = find_service(self, 'objectmap')
        for head_coachid in head_coach:
            if head_coachid is not colander.null:
                objectmap.connect(self, head_coachid, HEADCOACHTTOTEAM)

    def players(self):
        return list(self.get_sources(PLAYERTOTEAM))

    def head_coach(self):
        return list(self.get_targets(HEADCOACHTTOTEAM))

