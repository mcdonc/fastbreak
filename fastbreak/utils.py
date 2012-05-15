import colander
from persistent import Persistent

from substanced.service import find_service

# Constants
PLAYERTOTEAM = 'player-to-team'
PLAYERTOPG = 'player-to-primaryguardian'
PLAYERTOOG = 'player-to-otherguardian'
HEADCOACHTTOTEAM = 'headcoach-to-team'
ASSISTANTCOACHTTOTEAM = 'assistantcoach-to-team'
MANAGERTOTEAM = 'manager-to-team'

def make_name(title):
    # Policy for automatically generating unique names from titles. For
    # now, just lower and replace spaces with dashes

    name = title.replace(' ', '-').lower()
    return name

# Base class for content
class BaseContent(Persistent):
    disconnect_targets = (HEADCOACHTTOTEAM,)
    title = ''

    def texts(self): # for indexing
        return self.title

    def get_relationids(self, relation_name):
        objectmap = find_service(self, 'objectmap')
        return list(objectmap.targetids(self, relation_name))

    def get_sources(self, relation_name):
        objectmap = find_service(self, 'objectmap')
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
