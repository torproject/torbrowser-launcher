from twisted.internet import defer
from txsocksx.errors import SOCKSError

class Anonymous(object):
    """
    ( 0 )
    """
    method = '\x00'
    def negotiate(self, proto):
        self.negotiated = True
        return defer.succeed(None)

class GSSAPI(object):
    """
    ( 1 )
    """
    method = '\x01'
    def negotiate(self, proto):
        raise NotImplemented

class UsernamePasswordAuthFailed(SOCKSError):
    pass

class UsernamePassword(object):
    """
    ( 2 )
    """
    method = '\x02'
    def __init__(self, uname, passwd):
        self.uname = uname
        self.passwd = passwd

    def negotiate(self, proto):
        proto.transport.write(
            self.method
            + chr(len(self.uname)) + self.uname
            + chr(len(self.passwd)) + self.passwd)
        # XXX implement the reading of the response and make sure
        # authentication suceeded
        return defer.succeed(None)

