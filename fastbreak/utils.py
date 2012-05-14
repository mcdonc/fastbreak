
# Constants
DOCUMENTTOTEAM = 'document-to-team'
PLAYERTOTEAM = 'player-to-team'
PLAYERTOPRIMARYGUARDIAN = 'player-to-primaryguardian'
PLAYERTOOTHERGUARDIAN = 'player-to-otherguardian'
HEADCOACHTTOTEAM = 'headcoach-to-team'
ASSISTANTCOACHTTOTEAM = 'assistantcoach-to-team'
MANAGERTOTEAM = 'manager-to-team'

def make_name(title):
    # Policy for automatically generating unique names from titles. For
    # now, just lower and replace spaces with dashes

    name = title.replace(' ', '-').lower()
    return name

