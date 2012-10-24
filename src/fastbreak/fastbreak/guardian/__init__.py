from types import ListType

from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

from zope.interface import implementer

from substanced.content import content

from ..interfaces import IGuardian

from ..utils import (
    BaseContent,
    GUARDIAN
    )

@content(
    IGuardian,
    name='Guardian',
    icon='icon-tags'
)
@implementer(IGuardian)
class Guardian(BaseContent):
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

    def players(self):
        return self.get_sources(GUARDIAN)
