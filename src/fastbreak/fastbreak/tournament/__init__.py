from persistent.mapping import PersistentMapping
from zope.interface import implementer

from substanced.content import content
from substanced.folder import Folder

from ..interfaces import (
    ITournaments,
    ITournament
    )

from ..utils import (
    BaseContent,
    ATTENDING
    )

@content(
    ITournaments,
    name='Tournament',
    icon='icon-tags',
)
@implementer(ITournaments)
class Tournaments(Folder):
    def __init__(self):
        Folder.__init__(self)
        self.title = 'Tournaments'


@content(
    ITournament,
    name='Tournament',
    icon='icon-tags',
)
@implementer(ITournament)
class Tournament(BaseContent):
    props = None

    def __init__(self, external_id, title, position, props=None):
        BaseContent.__init__(self)
        self.external_id = external_id
        self.title = title
        self.position = position

        if props:
            self.props = PersistentMapping()
            for k, v in props.items():
                self.props[k] = v

    def players(self):
        """ Sorted list of players attending tournament """
        players = list(self.get_sources(ATTENDING))
        return sorted(players, key=lambda p: p.title)


