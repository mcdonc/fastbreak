from types import ListType

from persistent.list import PersistentList
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
    def __init__(self, external_id,
                 first_name, last_name, emails,
                 props):
        BaseContent.__init__(self)
        self.external_id = external_id
        self.first_name = first_name
        self.last_name = last_name
        assert isinstance(emails, ListType)
        self.emails = PersistentList(emails)
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

    def tourneys(self):
        these_tourneys = []
        if self.props['lax_clash'] == 'Checked':
            these_tourneys.append('A')
        if self.props['fall_ball_classic'] == 'Checked':
            these_tourneys.append('B')
        if self.props['river_city'] == 'Checked':
            these_tourneys.append('C')

        return these_tourneys

    def all_emails(self):
        """ Get all unique emails for player and all guardians """
        emails = set()
        for e in self.emails:
            if e != '':
                emails.add(e)
        for g in self.guardians():
            for e in g.emails:
                if e != '':
                    emails.add(e)

        return emails
