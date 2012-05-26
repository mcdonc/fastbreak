import colander
from persistent import Persistent

from substanced.service import find_service

# Constants
PLAYERTOTEAM = 'player-to-team'
PLAYERTOPG = 'player-to-primaryguardian'
PLAYERTOOG = 'player-to-otherguardian'
COACHTTOTEAM = 'coach-to-team'
MANAGERTOTEAM = 'manager-to-team'
PLAYERTOSIGNUP = 'player-to-signup'

# TODO XXX Hard-coding the list of dues choices
dues_choices = (
    (765, 'Fall/Full Season 2012: $765'),
    (300, 'Fall Season 2012 $300'),
    (550, 'Full Season 2012: $550'),
    (300, 'Short Season Blue/Orange/White 2012: $300'),
    (320, 'Short Season Silver 2012: $320'),
    (270, 'Short Season Black 2012: $270'),
    )


def make_name(title):
    # Policy for automatically generating unique names from titles. For
    # now, just lower and replace spaces with dashes

    name = title.replace(' ', '-').lower()
    return name

# Base class for content
class BaseContent(Persistent):
    title = ''

    def texts(self): # for indexing
        return self.title

    def get_relationids(self, relation_name):
        objectmap = find_service(self, 'objectmap')
        return list(objectmap.targetids(self, relation_name))

    def get_relations(self, relation_name):
        # Get the objects instead
        objectmap = find_service(self, 'objectmap')
        return list(objectmap.targets(self, relation_name))

    def get_sources(self, relation_name):
        objectmap = find_service(self, 'objectmap')
        # TODO can we get rid of the list() part?
        return list(objectmap.sources(self, relation_name))

    def get_targets(self, relation_name):
        objectmap = find_service(self, 'objectmap')
        return list(objectmap.targets(self, relation_name))

    def disconnect(self):
        objectmap = find_service(self, 'objectmap')

        for target in self.disconnect_targets:
            for oid in self.get_relationids(target):
                objectmap.disconnect(self, oid, target)

    def connect_role(self, role, *seq):
        objectmap = find_service(self, 'objectmap')
        for oid in seq:
            if oid is not colander.null:
                objectmap.connect(self, oid, role)

    def nickname_or_first_name(self):
        if self.nickname and self.nickname != '':
            return self.nickname
        else:
            return first_name