from substanced.content import content
from substanced.folder import Folder

from ..interfaces import IPeople

@content(
    IPeople,
    name='People',
    icon='icon-tags',
    )
class People(Folder):
    pass