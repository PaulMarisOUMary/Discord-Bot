# Python conventions

Those conventions follows a part of the model provided by: [PEP-0008](https://peps.python.org/pep-0008).

## Magic numbers

You should avoid "magic numbers", declaring those numbers in variables.
```python
# Correct
accuracy = 0.99
if result < accuracy: ...

# Wrong
if result < 0.99: ...
```

## Methods names

Use the function naming rules: lowercase with words separated by underscores as necessary to improve readability.
Use one leading underscore only for non-public methods and instance variables.
Example: `__my_super_method`
```python
# Correct
def my_super_method(): ...

def __my_super_private_method(): ...

# Wrong
def MySuperMethod(): ...
```

## Class names

Class names should normally use the CapWords convention.
```python
# Correct
class MyClass(object):
    def __init__(self, attri):
        self.attri = attri

# Wrong
class myClass(object):
    def __init__(self, attri):
        self.attri = attri
```

## Variables name

Variables are written in lowercase with words separated by underscores as necessary to improve readability. Less recommended, you can also use camelCase.
Constants are written in all capital letters with underscores separating words.
```python
# Correct
variable = "text"
MY_CONSTANT = "text"
my_super_variable = "text"
mySuperVariable = "text"

# Wrong
variable="text"
My_Constant ="text"
mysupervariable= "text"
my_super_variable="text"
```

## Using variable(s) with string(s)

You should use format strings to use variables in strings. Doing the following:
```python
# Correct
string = f"Hey, {myVariable} is my string !"

# Wrong
string = "Hey, " + str(myvariable) + " is my string !"
```

## String & Character

Characters should be defined in single quotes.
Strings should be defined in double quotes.
```python
# Correct
character = 'a'
string = "This is a string, not a character"

# Wrong
character = "a"
string = 'This is a string, not a character'
```

## Operator

```python
# Correct:
# easy to match operators with operands
income = (gross_wages
          + taxable_interest
          + (dividends - qualified_dividends)
          - ira_deduction
          - student_loan_interest)

# Wrong:
# operators sit far away from their operands
income = (gross_wages +
          taxable_interest +
          (dividends - qualified_dividends) -
          ira_deduction -
          student_loan_interest)
```

## Imports

```python
# Correct:
import os
import sys

# Wrong:
import sys, os
```

## Indentation

Python disallows mixing tabs and spaces for indentation.

## Whitespace in Expressions and Statements

### Brackets or braces
```python
# Correct:
spam(ham[1], {eggs: 2})

# Wrong:
spam( ham[ 1 ], { eggs: 2 } )
```

```python
# Correct:
foo = (0,)

# Wrong:
bar = (0, )
```

```python
# Correct:
spam(1)

# Wrong:
spam (1)
```

### Comma
```python
# Correct:
if x == 4: print(x, y); x, y = y, x

# Wrong:
if x == 4 : print(x , y) ; x , y = y , x
```

### Assignmment
```python
# Correct:
x = 1
y = 2
long_variable = 3

# Wrong:
x             = 1
y             = 2
long_variable = 3
```

### Return hint
```python
# Correct
def func() -> NoReturn: ...

# Wrong
def func()->NoReturn : ...
```

### Parameter hint
```python
# Correct
def func(arg1: str, arg2: int) -> str: ...

# Wrong
def func(arg1 : str, arg2:int) -> str: ...
```