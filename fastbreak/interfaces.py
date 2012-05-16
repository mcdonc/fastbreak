from zope.interface import Interface

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

class IRegistration(Interface):
    """Something an IPlayer can sign up for and pay for"""
    pass

class ISignup(Interface):
    """A commitment by a particular IPlayer to a particular
    IRegsistration"""
    pass

class IPayment(Interface):
    """Payment made by an IPlayer for an ISignup"""
    pass