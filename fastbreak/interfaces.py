from zope.interface import Interface

class IDocument(Interface):
    pass

class ITeam(Interface):
    pass

class IProgram(Interface):
    """A group of teams and events in an organization"""
    pass

class IPlayer(Interface):
    """A player on multiples teams and multiple programs"""
    pass

class IAdult(Interface):
    """An adult who is a guardian, coach, team manager. """
    pass