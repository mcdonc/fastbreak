import colander
import deform
from deform_bootstrap.widget import ChosenMultipleWidget

from substanced.content import content
from substanced.property import PropertySheet
from substanced.schema import Schema

from fastbreak.interfaces import (
    IAdult,
    ITeam
    )
from fastbreak.utils import (
    BaseContent,
    PLAYERTOTEAM,
    COACHTTOTEAM,
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
    return ChosenMultipleWidget(values=values)


# Teams
class TeamSchema(Schema):
    title = colander.SchemaNode(
        colander.String(),
    )
    coaches = colander.SchemaNode(
        deform.Set(allow_empty=True),
        widget=adult_widget,
        missing=colander.null,
        preparer=lambda users: set(map(int, users)),
        )
    team_managers = colander.SchemaNode(
        deform.Set(allow_empty=True),
        widget=adult_widget,
        missing=colander.null,
        preparer=lambda users: set(map(int, users)),
        )


class TeamBasicPropertySheet(PropertySheet):
    schema = TeamSchema()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        context = self.context

        coaches = map(str, context.get_relationids(COACHTTOTEAM))
        team_managers = map(str, context.get_relationids(MANAGERTOTEAM))

        return dict(
            name=context.__name__,
            title=context.title,
            coaches=coaches,
            team_managers=team_managers
        )


    def set(self, struct):
        context = self.context
        context.title = struct['title']

        context.connect_all(struct)


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
    disconnect_targets = (COACHTTOTEAM, MANAGERTOTEAM)

    def __init__(self, title):
        self.title = title

    def connect_all(self, struct):
        # Disconnect old relations, make new relations
        self.disconnect()

        for coach_oid in struct['coaches']:
            self.connect_role(COACHTTOTEAM, coach_oid)
        for team_manager_oid in struct['team_managers']:
            self.connect_role(MANAGERTOTEAM, team_manager_oid)

    def players(self):
        return list(self.get_sources(PLAYERTOTEAM))

    def coaches(self):
        return self.get_targets(COACHTTOTEAM)

    def team_managers(self):
        return self.get_targets(MANAGERTOTEAM)