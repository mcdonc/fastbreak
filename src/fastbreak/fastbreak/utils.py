from types import (
    ListType,
    IntType
    )

import colander

from pyramid.decorator import reify

from substanced.folder import Folder
from substanced.objectmap import find_objectmap

# Constants for roles
ROSTER = 'roster'
GUARDIAN = 'guardian'

def split_emails(emails_string):
    """ Given a string with a semi-colon-delim, split """

    data = set()
    for addr1 in emails_string.strip().split(';'):
        data.add(addr1.strip())

    return list(data)

def nameify(seq):
    return '-'.join(seq).lower()


class BaseContent(Folder):
    title = ''

    @reify
    def objectmap(self):
        return find_objectmap(self)

    @reify
    def oid(self):
        return self.objectmap.objectid_for(self)

    def texts(self): # for indexing
        return self.title

    def get_relationids(self, relation_name):
        return list(self.objectmap.targetids(self, relation_name))

    def get_relations(self, relation_name):
        # Get the objects instead
        return list(self.objectmap.targets(self, relation_name))

    def get_sources(self, relation_name):
        # TODO can we get rid of the list() part?
        return list(self.objectmap.sources(self, relation_name))

    def get_targets(self, relation_name):
        return list(self.objectmap.targets(self, relation_name))

    def disconnect(self):
        for target in self.disconnect_targets:
            for oid in self.get_relationids(target):
                self.objectmap.disconnect(self, oid, target)

    def connect_role(self, role, seq):
        assert isinstance(seq, ListType)
        for oid in seq:
            if oid is not colander.null:
                self.objectmap.connect(self, oid, role)

    def get_by_external_id(self, external_id):
        """ Given an int for the external id, return child """

        assert isinstance(external_id, IntType)
        for v in self.items():
            if v.get('external_id', None) == external_id:
                return v

