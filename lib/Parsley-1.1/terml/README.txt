TermL is JSON's big brother.
It's described here: http://www.erights.org/data/terml/terml-spec.html

In addition to JSON's dict, list, string, and number types, TermL
supports arbitrary identifiers as tags, with optional parenthesized
arguments. It's a nice representation for ASTs and the like, where you
have a tree of things with a relatively small set of names.

To use this code, do something like this:

>>> from terml.parser import parseTerm
>>> parseTerm('[foo(x), 3, FancyObject("bits", "bobs")]')
Term('[foo(x), 3, FancyObject("bits", "bobs")]')

>>> t = parseTerm('[foo(x), 3, FancyObject("bits", "bobs")]')

>>> t.arglist
[Term('foo(x)'), Term('3'), Term('FancyObject("bits", "bobs")')]

>>> t.functor
Tag('.tuple.')

>>> t.arglist[0]
Term('foo(x)')

>>> t.arglist[0].functor
Tag('foo')


>>> t2 = parseTerm('{foo: 1, "foo": 11, f(o(o, 1): 1}')

{foo: 1, "foo": 11, f(o(o, 1): 1}
                     ^
Parse error at line 1, column 21: expected the token '}'

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "terml/parser.py", line 202, in parseTerm
    return _parseTerm(termString)
  File "terml/parser.py", line 186, in _parseTerm
    result, error = p.apply("term")
  File "/Users/washort/Projects/PyMeta/trunk/pymeta/runtime.py", line 278, in apply
    return self._apply(r, ruleName, args)
  File "/Users/washort/Projects/PyMeta/trunk/pymeta/runtime.py", line 307, in _apply
    [rule(), self.input])
  File "/pymeta_generated_code/pymeta_grammar__TermLParser.py", line 483, in rule_term
  File "/Users/washort/Projects/PyMeta/trunk/pymeta/runtime.py", line 397, in _or
    raise joinErrors(errors)
pymeta.runtime.ParseError: (21, [('expected', 'token', "'}'")])

>>> terml.parser.parseTerm("foo(())")

foo(())
    ^
Parse error at line 1, column 4: expected one of ')', token '[', token '"', token "'", '0', a digit, a letter, '_', '$', '.', '<', ':', token '${', token '$', token '@{', token '@', token '{', '-', ' ', '\t', '\x0c', or '#'

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "terml/parser.py", line 202, in parseTerm
    return _parseTerm(termString)
  File "terml/parser.py", line 192, in _parseTerm
    raise error
pymeta.runtime.ParseError: (4, [('expected', None, ')'), ('expected', 'token', '['), ('expected', 'token', '"'), ('expected', 'token', "'"), ('expected', None, '0'), ('expected', 'digit', None), ('expected', 'letter', None), ('expected', None, '_'), ('expected', None, '$'), ('expected', None, '.'), ('expected', None, '<'), ('expected', None, ':'), ('expected', 'token', '${'), ('expected', 'token', '$'), ('expected', 'token', '@{'), ('expected', 'token', '@'), ('expected', 'token', '{'), ('expected', None, '-'), ('expected', None, ' '), ('expected', None, '\t'), ('expected', None, '\x0c'), ('expected', None, '#')])
