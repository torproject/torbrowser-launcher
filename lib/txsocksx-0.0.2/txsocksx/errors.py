from twisted.internet import error
import txsocksx.constants as c

class ParsingError(Exception):
    pass

class InvalidServerReply(Exception):
    pass

class SOCKSError(Exception):
    pass

class MethodsNotAcceptedError(SOCKSError):
    pass

class ConnectionError(SOCKSError):
    pass

class ConnectionLostEarly(SOCKSError, error.ConnectionLost):
    pass

class StateError(Exception):
    """
    There was a problem with the State.
    """
    pass

class NoAcceptableMethods(SOCKSError):
    """
    No Acceptable Methods ( FF )
    """

class ServerFailure(SOCKSError):
    """
    General SOCKS server failure ( 1 )
    """

class ConnectionNotAllowed(SOCKSError):
    """
    Connection not allowed ( 2 )
    """

class NetworkUnreachable(SOCKSError):
    """
    Network unreachable ( 3 )
    """

class HostUnreachable(SOCKSError):
    """
    Host unreachable ( 4 )
    """

class ConnectionRefused(SOCKSError):
    """
    Connection refused ( 5 )
    """

class TTLExpired(SOCKSError):
    """
    TTL expired ( 6 )
    """

class CommandNotSupported(SOCKSError):
    """
    Command Not Supported ( 7 )
    """

class AddressNotSupported(SOCKSError):
    """
    Address type not supported ( 8 )
    """


