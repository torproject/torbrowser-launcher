from twisted.protocols import tls
from twisted.internet import interfaces
from zope.interface import implements

class SSLWrapClientEndpoint(object):
    implements(interfaces.IStreamClientEndpoint)

    def __init__(self, contextFactory, wrappedEndpoint):
        self.contextFactory = contextFactory
        self.wrappedEndpoint = wrappedEndpoint

    def connect(self, fac):
        fac = tls.TLSMemoryBIOFactory(self.contextFactory, True, fac)
        return self.wrappedEndpoint.connect(fac)
