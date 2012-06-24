from pyramid.security import Allow

from substanced.catalog import Catalog
from substanced.catalog.indexes import (
    FieldIndex,
    TextIndex,
    KeywordIndex,
    )
from substanced.catalog.discriminators import (
    get_textrepr,
    get_title,
    get_interfaces,
    )
from substanced.site import Site as _Site


class Site(_Site):
    def __init__(self,  *arg, **kw):
        _Site.__init__(self,  *arg, **kw)

        # The retail view is also protected
        self.__acl__.append(
            (Allow, 'admininstrators', 'view')
        )
        self.title = 'New World Sports Dashboard'

        # Setup catalog
        catalog = Catalog()
        catalog['name'] = FieldIndex('__name__')
        catalog['title'] = FieldIndex(get_title)
        catalog['interfaces'] = KeywordIndex(get_interfaces)
        catalog['texts'] = TextIndex(get_textrepr)
        catalog['la_id'] = FieldIndex('la_id')
        self.add_service('catalog', catalog)