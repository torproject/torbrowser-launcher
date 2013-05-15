import parsley
import struct

from txsocksx import errors, auth

socks_grammar = r"""
# XXX probably move these to another grammar and inherit from it
byte = anything:byte -> ord(byte)
short = byte:high byte:low -> (high << 8) | low
hexdigit = :x ?(x in '0123456789abcdefABCDEF') -> x

byteToIntStr = anything:b
    -> str(ord(b))

# IPV4, IPV6 Address in binary form
IPV4AddrBytes = byte{4}:quads
    -> '.'.join(str(q) for q in quads)
# XXX properly parse IPV6
IPV6AddrBytes = <byte{16}>

# IPV6 Address in the form 'X:X:X::X::X'
# IPV4 Address in the form '0.0.0.0'
IPV4AddrStr = <(digit{1, 3} '.'){4}>
IPV6AddrStr = <(hexdigit{0, 4} ':'){7} hexdigit{1, 4}>

# XXX notes
# letterOrDigitOrHyphen = letterOrDigit | '-'
# domainLabel = <(letter letterOrDigitOrHyphen{0, 61} letterOrDigit)>
# domainName =
#    < (domainLabel '.'?)* >

# XXX make this stricter
DomainName = letterOrDigit | '-' | '.'

SOCKSDomainName =
    byte:len <DomainName{len}>

# Below are SOCKS specific messages
ver = ('\x05' -> 5)
      | ('\x04' -> 4)

rsv = <'\x00'>

SOCKSAddress = ('\x01' IPV4AddrBytes:addr
                    -> addr)

                | ('\x03' SOCKSDomainName:domain
                    -> domain)

                | ('\x04' IPV6AddrBytes:addr
                    -> addr)

hostToSOCKSAddress =
                ( IPV4AddrStr:addr
                    -> '\x01' + addr )

                | ( <DomainName*>:addr
                    -> '\x03' + chr(len(addr)) + addr )

                | ( IPV6AddrStr:addr
                    -> '\x04' + addr )



port = short:p -> int(p)

# The Client version identified/method selection message
clientVersionMethod =
    ver:v anything:nmethods anything{1, 255}:methods
    -> (v, nmethods, methods)

methods = ('\x00' -> a.Anonymous)
          | ('\x01' -> a.GSSAPI)
          | ('\x02' -> a.UsernamePassword)
          | ('\xFF' -> e.NoAcceptableMethods)

# The Server version identified/method selection message
serverVersionMethod =
    ver:v methods:m -> (v, m)

cmd = ('\x01' -> 1)
      | ('\x02' -> 2)
      | ('\x03' -> 3)

clientRequest =
    ver cmd:command byte SOCKSAddress:address port:port
        -> (command, address, port)

rep = ('\x00' -> 0)
      | ('\x01' -> e.ServerFailure)
      | ('\x02' -> e.ConnectionNotAllowed)
      | ('\x03' -> e.NetworkUnreachable)
      | ('\x04' -> e.HostUnreachable)
      | ('\x05' -> e.ConnectionRefused)
      | ('\x06' -> e.TTLExpired)
      | ('\x07' -> e.CommandNotSupported)
      | ('\x08' -> e.AddressNotSupported)

serverReply =
    ver rep:reply byte SOCKSAddress:address port:port
    -> (reply, address, port)
"""

SOCKSGrammar = parsley.makeGrammar(socks_grammar,
        {"e": errors, "a": auth}
)

# XXX how do I do the equivalent of the above and generate the grammar to a
# file?
# parsley.moduleFromGrammar(socks_grammar, 'SOCKSGrammar',
#         object, {"e": error, "a": auth})

