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

team_blue = dict(
    head_coach=u"Barb DiArcangelo",
    assistant_coach=u'Jess Glazer',
    team_manager=u"Sharon O'Connor",
    families=[
    ])
team_orange = dict(
    head_coach=u'Caitlin Moore',
    assistant_coach=u'No Name',
    team_manager=u'Ashley Stavac',
    families=[
        (u'Stacey Strobl', u'Mike Strobl', u'Child Strobl')
    ])
team_white = dict(
    head_coach=u"Stevie McFadden",
    assistant_coach=u'Kirsten Nease',
    team_manager=u'Martha Grattan',
    families=[
        (u'Jim Hoover', u'Cheri Hoover', u'Child Hoover'),
        (u'Paul Everitt', u'Herveline Everitt', u'Child Everitt'),
        (u'Kristen Buechner', u'Chris Buechner', u'Child Buechner')
    ])
team_black = dict(
    head_coach=u"Morgan Vahue",
    assistant_coach=u'Christine Riedel',
    team_manager=u'Todd Salzman',
    families=[
    ])
team_silver = dict(
    head_coach=u"Val Pate",
    assistant_coach=u'Sandy Nixon',
    team_manager=u'Jean Latta',
    families=[
    ])

sample_data = dict(
    Blue=team_blue, White=team_white, Orange=team_orange,
    Black=team_black, Silver=team_silver
)


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
