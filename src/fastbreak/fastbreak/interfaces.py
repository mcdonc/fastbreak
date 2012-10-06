from zope.interface import Interface

class ITeams(Interface):
    """ Interface for folder holding Team resources """

class ITeam(Interface):
    """ Interface for a Team """

#

class IPeople(Interface):
    """ Interface for a folder holding coaches, guardians, players """

class IPlayer(Interface):
    """ Interface for a Player """

class ICoach(Interface):
    """ Interface for a Coach """

class IGuardian(Interface):
    """ Interface for a Guardian """

#

class ITournaments(Interface):
    """ Interface for a folder holding Tournament resources  """

class ITournament(Interface):
    """ Interface for a Tournament """


