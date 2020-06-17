# Twop
An esolang where every function is a binary operator.

# Features
Twop currently includes support for variable definition, binary operator definition, and arithmetic statements.

# Syntax
All statements must be enclosed in either brackets or curly braces. A bracketed statment is a definition of some sort, while a curly brace statement is an arithmetic expression to be printed to the console. To define a variable, just use the '=' operator, as such:
`[a=5]`

To define an operator, the statement must follow the format of 'xOPy:definition'. For example,
`[x$y:3*x+y]`
would define the '$' operator as 3*(arg1)+arg2.

Lastly, arithmetic expressions follow the same syntax and order of operations as basic Python arithmetic and print the result to the console. Currently, addition, subtraction, multiplication, and modulation are supported. User-defined operators are invoked the same way normal ones are. The statement
 `3 $ a + (7 * 2)`
 would output the value 28.
