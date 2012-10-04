from substanced.content import content
from substanced.folder import Folder

from ..interfaces import (
    ITournaments,
    ITournament
    )

@content(
    ITournaments,
    name='Tournaments',
    icon='icon-tags',
    )
class Tournaments(Folder):
    pass

@content(
    ITournament,
    name='Tournament',
    icon='icon-tags',
    )
class Tournament(Folder):
    pass