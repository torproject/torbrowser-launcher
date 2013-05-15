import math
from parsley import makeGrammar

def calculate(start, pairs):
        result = start
        for op, value in pairs:
            if op == '+':
                result += value
            elif op == '-':
                result -= value
            elif op == '*':
                result *= value
            elif op == '/':
                result /= value
        return result

calcGrammar = """
number = <digit+>:ds -> int(ds)
parens = '(' ws expr:e ws ')' -> e
value = number | parens
ws = ' '*
add = '+' ws expr2:n -> ('+', n)
sub = '-' ws expr2:n -> ('-', n)
mul = '*' ws value:n -> ('*', n)
div = '/' ws value:n -> ('/', n)

addsub = ws (add | sub)
muldiv = ws (mul | div)

expr = expr2:left addsub*:right -> calculate(left, right)
expr2 = value:left muldiv*:right -> calculate(left, right)
"""

Calc = makeGrammar(calcGrammar, {"calculate": calculate}, name="Calc")

calcGrammarEx = """
value = super | constant
constant = 'pi' -> math.pi
         | 'e' -> math.e
"""
CalcEx = makeGrammar(calcGrammarEx, {"math": math}, name="CalcEx",
                     extends=Calc)
