from persistent.mapping import PersistentMapping

from zope.interface import implementer

from substanced.content import content
from substanced.folder import Folder

from ..interfaces import ICoach

from ..utils import (
    HEADCOACH,
    ASSTCOACH
    )

@content(
    ICoach,
    name='Coach',
    icon='icon-tags'
)
@implementer(ICoach)
class Coach(Folder):
    def __init__(self, external_id, firstname, lastname,
                 team_name, props):
        Folder.__init__(self)
        self.external_id = external_id
        self.firstname = firstname
        self.lastname = lastname
        self.team_name = team_name
        self.title = lastname + ', ' + firstname

        self.props = PersistentMapping()

        for k, v in props.items():
            self.props[k] = v

    def teams(self):
        return self.get_targets([HEADCOACH, ASSTCOACH])
