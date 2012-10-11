from persistent.mapping import PersistentMapping
from zope.interface import implementer

from substanced.content import content
from substanced.folder import Folder

from ..interfaces import (
    ITeams,
    ITeam,
    IPlayer,
    ICoach,
    ITeamManager
    )
from ..utils import (
    BaseContent,
    ROSTER,
    HEADCOACH,
    ASSTCOACH,
    MANAGER
    )

@content(
    ITeams,
    name='Teams',
    icon='icon-tags',
)
@implementer(ITeams)
class Teams(Folder):
    def __init__(self):
        Folder.__init__(self)
        self.title = 'Teams'


@content(
    ITeam,
    name='Team',
    icon='icon-tags',
)
@implementer(ITeam)
class Team(BaseContent):
    props = None

    def __init__(self, external_id, title, props=None):
        BaseContent.__init__(self)
        self.external_id = external_id
        self.title = title

        if props:
            self.props = PersistentMapping()
            for k, v in props.items():
                self.props[k] = v

    def head_coaches(self):
        """ Sorted list of players """
        coaches = list(self.get_sources(HEADCOACH))
        return sorted(coaches, key=lambda p: p.title)

    def assistant_coaches(self):
        """ Sorted list of players """
        coaches = list(self.get_sources(ASSTCOACH))
        return sorted(coaches, key=lambda p: p.title)

    def managers(self):
        """ Sorted list of players """
        managers = list(self.get_sources(MANAGER))
        return sorted(managers, key=lambda p: p.title)

    def players(self):
        """ Sorted list of players """
        players = list(self.get_sources(ROSTER))
        return sorted(players, key=lambda p: p.title)

