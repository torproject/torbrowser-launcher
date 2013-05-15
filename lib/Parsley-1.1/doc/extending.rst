==================================
Extending Grammars and Inheritance
==================================

:warning: Unfinished

Another feature taken from OMeta is *grammar inheritance*. We can
write a grammar with rules that override ones in a parent. If we load
the grammar from our calculator tutorial as ``Calc``, we can extend it
with some constants::

    from parsley import makeGrammar
    import math
    import calc
    calcGrammarEx = """
    value = super | constant
    constant = 'pi' -> math.pi
             | 'e' -> math.e
    """
    CalcEx = makeGrammar(calcGrammar, {"math": math}, extends=calc.Calc)


Invoking the rule ``super`` calls the rule ``value`` in Calc. If it
fails to match, our new ``value`` rule attempts to match a constant
name.
