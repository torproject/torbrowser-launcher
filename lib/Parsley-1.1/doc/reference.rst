Parsley Reference
-----------------

Basic syntax
~~~~~~~~~~~~
``foo = ....``:
   Define a rule named foo.

``expr1 expr2``:
   Match expr1, and then match expr2 if it succeeds, returning the value of
   expr2. Like Python's ``and``.

``expr1 | expr2``:
  Try to match ``expr1`` --- if it fails, match ``expr2`` instead. Like Python's
  ``or``.

``expr*``:
  Match ``expr`` zero or more times, returning a list of matches.

``expr+``:
  Match ``expr`` one or more times, returning a list of matches.

``expr?``:
  Try to match ``expr``. Returns ``None`` if it fails to match.

``expr{n, m}``:
  Match ``expr`` at least ``n`` times, and no more than ``m`` times.

``expr{n}``:
  Match ``expr`` ``n`` times exactly.

``~expr``:
  Negative lookahead. Fails if the next item in the input matches
  ``expr``. Consumes no input.

``~~expr``:
  Positive lookahead. Fails if the next item in the input does *not*
  match ``expr``. Consumes no input.

``ruleName`` or ``ruleName(arg1 arg2 etc)``:
  Call the rule ``ruleName``, possibly with args.

``'x'``:
  Match the literal character 'x'.

``<expr>``:
  Returns the string consumed by matching ``expr``. Good for tokenizing rules.

``expr:name``:
  Bind the result of expr to the local variable ``name``.

``-> pythonExpression``:
  Evaluate the given Python expression and return its result. Can be
  used inside parentheses too!

``!(pythonExpression)``:
  Invoke a Python expression as an action.

``?(pythonExpression)``:
  Fail if the Python expression is false, Returns True otherwise.

Comments like Python comments are supported as well, starting with #
and extending to the end of the line.


Python API
~~~~~~~~~~
.. automodule:: parsley
   :members:


Built-in Parsley Rules
~~~~~~~~~~~~~~~~~~~~~~

``anything``:
    Matches a single character from the input.

``letter``:
    Matches a single ASCII letter.

``digit``:
    Matches a decimal digit.

``letterOrDigit``:
    Combines the above.

``end``:
    Matches the end of input.

``ws``:
    Matches zero or more spaces, tabs, or newlines.

``exactly(char)``:
   Matches the character `char`.
