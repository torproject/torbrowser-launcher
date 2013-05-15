from parsley import makeGrammar
jsonGrammar = r"""
ws = (' ' | '\r' | '\n' | '\t')*
object = ws '{' members:m ws '}' ws -> dict(m)
members = (pair:first (ws ',' pair)*:rest -> [first] + rest) | -> []
pair = ws string:k ws ':' value:v -> (k, v)
array = '[' elements:xs ws ']' -> xs
elements = (value:first (ws ',' value)*:rest -> [first] + rest) | -> []
value = ws (string | number | object | array
           | 'true'  -> True
           | 'false' -> False
           | 'null'  -> None)
string = '"' (escapedChar | ~'"' anything)*:c '"' -> ''.join(c)
escapedChar = '\\' (('"' -> '"')    |('\\' -> '\\')
                   |('/' -> '/')    |('b' -> '\b')
                   |('f' -> '\f')   |('n' -> '\n')
                   |('r' -> '\r')   |('t' -> '\t')
                   |('\'' -> '\'')  | escapedUnicode)
hexdigit = :x ?(x in '0123456789abcdefABCDEF') -> x
escapedUnicode = 'u' <hexdigit{4}>:hs -> unichr(int(hs, 16))
number = ('-' | -> ''):sign (intPart:ds (floatPart(sign ds)
                            | -> int(sign + ds)))
digit = :x ?(x in '0123456789') -> x
digits = <digit*>
digit1_9 = :x ?(x in '123456789') -> x
intPart = (digit1_9:first digits:rest -> first + rest) | digit
floatPart :sign :ds = <('.' digits exponent?) | exponent>:tail
                    -> float(sign + ds + tail)
exponent = ('e' | 'E') ('+' | '-')? digits
"""
JSONParser = makeGrammar(jsonGrammar, {})
