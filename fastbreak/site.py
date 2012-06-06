# Custom Substance D Site, so I can apply an ACL

from substanced.site import Site as _Site
from pyramid.security import Allow


class Site(_Site):
    def __init__(self, initial_username, initial_email, initial_password):
        _Site.__init__(self, initial_username, initial_email,
                       initial_password)

        self.__acl__.append(
            (Allow, 'admininstrators', 'view')
        )
        self.title = 'New World Sports Dashboard'

