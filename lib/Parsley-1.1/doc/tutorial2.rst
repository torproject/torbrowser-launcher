=================================================
Parsley Tutorial Part II: Parsing Structured Data
=================================================

Now that you are familiar with the basics of Parsley syntax, let's
look at a more realistic example: a JSON parser.

The JSON spec on http://json.org/ describes the format, and we can
adapt its description to a parser. We'll write the Parsley rules in
the same order as the grammar rules in the right sidebar on the JSON
site, starting with the top-level rule, 'object'.
::

    object = ws '{' members:m ws '}' -> dict(m)

Parsley defines a builtin rule ``ws`` which consumes any spaces, tabs,
or newlines it can.

Since JSON objects are represented in Python as dicts, and ``dict``
takes a list of pairs, we need a rule to collect name/value pairs
inside an object expression.
::

    members = (pair:first (ws ',' pair)*:rest -> [first] + rest)
              | -> []

This handles the three cases for object contents: one, multiple, or
zero pairs. A name/value pair is separated by a colon. We use the
builtin rule ``spaces`` to consume any whitespace after the colon::

    pair = ws string:k ws ':' value:v -> (k, v)

Arrays, similarly, are sequences of array elements, and are
represented as Python lists.
::

    array = '[' elements:xs ws ']' -> xs
    elements = (value:first (ws ',' value)*:rest -> [first] + rest) | -> []

Values can be any JSON expression.
::

    value = ws (string | number | object | array
               | 'true'  -> True
               | 'false' -> False
               | 'null'  -> None)


Strings are sequences of zero or more characters between double
quotes. Of course, we need to deal with escaped characters as
well. This rule introduces the operator ``~``, which does negative
lookahead; if the expression following it succeeds, its parse will
fail. If the expression fails, the rest of the parse continues. Either
way, no input will be consumed.
::

    string = '"' (escapedChar | ~'"' anything)*:c '"' -> ''.join(c)

This is a common pattern, so let's examine it step by step. This will
match leading whitespace and then a double quote character. It then
matches zero or more characters. If it's not an ``escapedChar`` (which
will start with a backslash), we check to see if it's a double quote,
in which case we want to end the loop. If it's not a double quote, we
match it using the rule ``anything``, which accepts a single character
of any kind, and continue. Finally, we match the ending double quote
and return the characters in the string. We cannot use the ``<>``
syntax in this case because we don't want a literal slice of the input
-- we want escape sequences to be replaced with the character they
represent.

It's very common to use ``~`` for "match until" situations where you
want to keep parsing only until an end marker is found. Similarly,
``~~`` is positive lookahead: it succeed if its expression succeeds
but not consume any input.

The ``escapedChar`` rule should not be too surprising: we match a
backslash then whatever escape code is given.

::

    escapedChar = '\\' (('"' -> '"')    |('\\' -> '\\')
                       |('/' -> '/')    |('b' -> '\b')
                       |('f' -> '\f')   |('n' -> '\n')
                       |('r' -> '\r')   |('t' -> '\t')
                       |('\'' -> '\'')  | escapedUnicode)

Unicode escapes (of the form ``\u2603``) require matching four hex
digits, so we use the repetition operator ``{}``, which works like +
or * except taking either a ``{min, max}`` pair or simply a
``{number}`` indicating the exact number of repetitions.
::

    hexdigit = :x ?(x in '0123456789abcdefABCDEF') -> x
    escapedUnicode = 'u' <hexdigit{4}>:hs -> unichr(int(hs, 16))

With strings out of the way, we advance to numbers, both integer and
floating-point.

::

    number = spaces ('-' | -> ''):sign (intPart:ds (floatPart(sign ds)
                                                   | -> int(sign + ds)))

Here we vary from the json.org description a little and move sign
handling up into the ``number`` rule. We match either an ``intPart``
followed by a ``floatPart`` or just an ``intPart`` by itself.
::

    digit = :x ?(x in '0123456789') -> x
    digits = <digit*>
    digit1_9 = :x ?(x in '123456789') -> x

    intPart = (digit1_9:first digits:rest -> first + rest) | digit
    floatPart :sign :ds = <('.' digits exponent?) | exponent>:tail
			 -> float(sign + ds + tail)
    exponent = ('e' | 'E') ('+' | '-')? digits

In JSON, multi-digit numbers cannot start with 0 (since that is
Javascript's syntax for octal numbers), so ``intPart`` uses ``digit1_9``
to exclude it in the first position.

The ``floatPart`` rule takes two parameters, ``sign`` and ``ds``. Our
``number`` rule passes values for these when it invokes ``floatPart``,
letting us avoid duplication of work within the rule. Note that
pattern matching on arguments to rules works the same as on the string
input to the parser. In this case, we provide no pattern, just a name:
``:ds`` is the same as ``anything:ds``.

(Also note that our float rule cheats a little: it does not really
parse floating-point numbers, it merely recognizes them and passes
them to Python's ``float`` builtin to actually produce the value.)

The full version of this parser and its test cases can be found in the
``examples`` directory in the Parsley distribution.
