from types import ListType

from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

from zope.interface import implementer

from substanced.content import content

from ..interfaces import IPlayer
from ..utils import (
    BaseContent,
    ROSTER,
    GUARDIAN,
    ATTENDING
    )

@content(
    IPlayer,
    name='Player',
    icon='icon-tags',
)
@implementer(IPlayer)
class IPlayer(BaseContent):
    def __init__(self, external_id,
                 first_name, last_name, emails,
                 jersey_number, grade, position,
                 school, experience,
                 props):
        BaseContent.__init__(self)
        self.external_id = external_id
        self.first_name = first_name
        self.last_name = last_name
        assert isinstance(emails, ListType)
        self.emails = PersistentList(emails)
        self.jersey_number = jersey_number
        self.grade = grade
        self.position = position
        self.school = school
        self.experience = experience
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

    def connect_tournament_oids(self, tournament_oids):
        self.connect_role(ATTENDING, tournament_oids)

    def tournaments(self):
        return self.get_targets(ATTENDING)

    def teams(self):
        return self.get_targets(ROSTER)

    def guardians(self):
        return self.get_targets(GUARDIAN)

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
