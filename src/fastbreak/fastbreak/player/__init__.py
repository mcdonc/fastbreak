from persistent.mapping import PersistentMapping

from substanced.content import content
from substanced.folder import Folder

from ..interfaces import IPlayer
from ..utils import (
    BaseContent,
    ROSTER
    )

@content(
    IPlayer,
    name='Player',
    icon='icon-tags',
)
class IPlayer(BaseContent):
    def __init__(self, external_id, first_name, last_name, team_name,
                 props):
        BaseContent.__init__(self)
        self.external_id = external_id
        self.first_name = first_name
        self.last_name = last_name
        self.team_name = team_name
        self.title = last_name + ', ' + first_name

        self.props = PersistentMapping()
        for k, v in props.items():
            self.props[k] = v

    def connect_team_oid(self, team_oid):
        self.connect_role(ROSTER, team_oid)

    def teams(self):
        return self.get_targets(ROSTER)
