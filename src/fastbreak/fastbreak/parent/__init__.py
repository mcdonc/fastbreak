from persistent.mapping import PersistentMapping

from substanced.content import content
from substanced.folder import Folder

from ..interfaces import IParent

@content(
    IParent,
    name='Parent',
    icon='icon-tags',
    )
class Parent(Folder):
    def __init__(self, external_id, firstname, lastname, props):
        Folder.__init__(self)
        self.external_id = external_id
        self.title = title
        self.props = PersistentMapping()

        for k,v in props.items():
            self.props[k] = v
