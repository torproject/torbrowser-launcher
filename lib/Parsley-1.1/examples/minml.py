"""
A grammar for parsing a tiny HTML-like language, plus a transformer for it.
"""
from parsley import makeGrammar, term, makeTerm as t
from itertools import chain

tinyHTMLGrammar = """

name = <letterOrDigit+>

tag = ('<' spaces name:n spaces attribute*:attrs '>'
         html:c
         '<' '/' token(n) spaces '>'
             -> t.Element(n.lower(), dict(attrs), c))

html = (text | tag)*

text = <(~('<') anything)+>

attribute = spaces name:k token('=') quotedString:v -> (k, v)

quotedString = (('"' | '\''):q <(~exactly(q) anything)*>:xs exactly(q)
                     -> xs

"""
TinyHTML = makeGrammar(tinyHTMLGrammar, globals(), name="TinyHTML")

testSource = "<html><title>Yes</title><body><h1>Man, HTML is <i>great</i>.</h1><p>How could you even <b>think</b> otherwise?</p><img src='HIPPO.JPG'></img><a href='http://twistedmatrix.com'>A Good Website</a></body></html>"
