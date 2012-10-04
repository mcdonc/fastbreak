from persistent.mapping import PersistentMapping
from zope.interface import implementer

from substanced.content import content
from substanced.folder import Folder

from ..interfaces import (
    ITeams,
    ITeam
    )
from ..utils import (
    BaseContent,
    ROSTER
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

    def players(self):
        """ Sorted list of players """
        players = list(self.get_sources(ROSTER))
        return sorted(players, key=lambda p: p.title)
