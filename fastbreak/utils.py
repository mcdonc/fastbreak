# Constants
DOCUMENTTOTEAM = 'document-to-team'
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

white_familes = [
    (u'Jim Hoover', u'Cheri Hoover', u'Peanut Hoover'),
    (u'Paul Everitt', u'Herveline Everitt', u'Morgan Everitt'),
    (u'Kristen Buechner', u'Chris Buechner', u'Kennedy Buechner')
]
orange_families = [
    (u'Stacey Strobl', u'Mike Strobl', u'Olivia Strobl')
]

sample_data = dict(
    Blue=[], White=white_families, Orange=orange_familes,
    Black=[], Silver=[]
)