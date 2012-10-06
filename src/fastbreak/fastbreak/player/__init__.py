from persistent.mapping import PersistentMapping

from substanced.content import content

from ..interfaces import IPlayer
from ..utils import (
    BaseContent,
    ROSTER,
    GUARDIAN
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

    def connect_team_oids(self, team_oids):
        self.connect_role(ROSTER, team_oids)

    def teams(self):
        return self.get_targets(ROSTER)

    def connect_guardian_oids(self, guardian_oids):
        self.connect_role(GUARDIAN, guardian_oids)

    def guardians(self):
        return self.get_targets(GUARDIAN)
