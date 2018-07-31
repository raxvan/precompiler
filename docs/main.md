
Builtin Commands
----------------

For syntax, the mandatory whitespace (tabs and spaces) is marked with `\w` and newline is marked with `\n`.
Tokens fall into certain cathegories:
1. `__ID__` = identifier
2. `__STR__` = string starting with `"` or `'`.
3. `__PATH__` = path to file. As a general rule all arguments of type `__PATH__` can be given as the value of a macro.
4. `__PY__` = any python valid syntax

### define
Adds a named variable (macro) in the preprocessor. The value of the macro is nothing more than a list of tokens taken from the line of the definition (`__VALUE`):

Syntax:
1. `#define \w __ID__ [\w [_ARGUMENTS #] _VALUE] \n`
3. `_ARGUMENTS` is optional along with the separator `#`
4. `_VALUE` can be anything


### undefine
Removes the variable from preprocessor. Throws error if variable does not exist.

Syntax:
- `#undef \w __ID__`

### redefine
A combination of `#undef` and `#define`

Syntax (is the same as the `#define`):
- `#redefine ...`

### colapse
Reasgines the define value with it's processed value.

Syntax:
- `#colapse \w __ID__`

Exampled:
```
#define a 1 + 2 + 3 + 4
#define foo a + b
#colapse foo
//foo becomes `1 + 2 + 3 + 4 + b` instead of `a + b`

```

### cwstrip
Takes a macro and removes all whitespaces and comment tokens from it's value.

Syntax:
- `#cwstrip \t __ID__`

### source
Changes behavior for `#include` and processing of the current file.

Syntax:
- `#source \w __ID__`

Possible values for `__ID__` where identifier can be:
1. `break` will stop precompiling the rest of the tokens of the exsiting file.
2. `once` will skip all includes of this file if the files was already included or inlined
3. `dup` will enable inclusion of this file multiple times (to bypass `SourceOnceByDefault` option)


### error
Stops execution and throws an error.

Syntax:
1. `#error \w __STR__`
2. `#error \w __ID__`

### include
Loads a file content to the top of the stack of tokens to be processed.

Syntax:
1. `#include \w __PATH__`
2. `#include \w __ID__`

### inline-include
Loads the file directly into the output, without processing it.

Syntax:
1. `#inline-include \w __PATH__`
2. `#inline-include \w __ID__`

### inline
Outputs content without processing it.

Syntax:
1. `#inline \w __STR__` will output the unboxed string
2. `#inline \w __ID__` will output define content as it is.

### inline-run
Runs python **eval** function and the output is not processed.

Syntax:
1. `#inline-run \w __STR__` -> The string is unboxed first and then passed to eval
2. `#inline-run \w __ID__` -> The deifne value is passed directly

### run python code wtih evaluation
Runs python **eval** function and the output is processed.

Syntax:
1. `#run \w __PY__\n`


### if/elif statement

Syntax:
```
#if \w __PY__ (: or \n)
	tokens ...
[#elif \w __PY__ (: or \n)
	tokens ...
[#else]
	tokens ...
#endif
```
The condition is a python expression that must return *True/False*. The last characters `:` or `\n` can be any of those.

Example:
1. `#if defined("TEST") \n ...branch`
2. `#if defined("TEST"): same line branch`

### nop
Directly ignored by the lexer, it's allow separation between tokens without whitespaces

Syntax:
1. `#-`
2. `#.`
3. `#>`

As an example `identifier1#-identifier2` will generate two tokens without whitespaces

### endl
Adds a newline to the output.

Syntax:
- `#endl`

Builtin defines
---------------
(TODO)

1. `__FILE__` Return the current preprocessed file
2. `__FILE_OUT__` Returns the ouput file
3. `__STR_BOX__` Will collapse all tokens and box string
4. `__WSIZE__` Will colapse all tokens and return the number of tokens (including whitespaces)
5. `__SIZE__` same as `__WSIZE__` but excluding whitespaces
6. `__VERSION__` Precompiler version

Python eval functions
--------------------
(TODO)

1. `defined(str)`



File search paths
-----------------
Any command that takes `__PATH__` as an argument will first process the path by replacing all `{IDENTIFIER}` substrings with content search from (in this order):

1. Upper case of `IDENTIFIER` from environment variables
2. Lowe case `IDENTIFIER` api defined map in file manager.
3. Lower case `IDENTIFIER` environment variables.

Example:
`#include "{PROJECT_DIR}/engine/math.h"` where `PROJECT_DIR` is an enviroment variable with value `/work`, the result will be `#include "/work/engine/math.h"`

File paths given to `include` or to `#inline-include` are searched in the following order:

1. First the patch is checked if it exists (unprocessed, note that current working directory could also affect this result)
2. File that includes folder + include path. This is useful relative to your file searches `"../engine/whatever.h"`
3. All file manager search paths (provided in file manager) + include path

Order of evaluation and defines
-------------------------------
The precompiler processes source files in the form of tokens with "generic" type given by the lexer interface. The default output assembler writes the tokens back to a file. The transfer of tokens from lexer to assembler is made by the precompiler which evaluates them one by one from the first to the last. The input and output have different states and some commands affects this states.
Regular tokens (whitespace , characters, strings, comments, etc) are passed directly to the assembler and **#commands** are evaluated.

If the **`__ID__`** token that is being processed matches the name of a **#define** then the define content is pushed **at the beginning of the processing queue**. Example:
```
//source code
#define foo 1
#define bar 2
var x = foo + bar
```
```
//after preprocessing:


var x = 1 + 2
```

**Be carefull not to create infinite loops**:
```
#define BAR u BAR
fu BAR // <- expands to infinity: 'fu u u u u u u u'
```



Defines with arguments
----------------------

Example:
```
//source
#define ADD(A,B,C) # A + B + C
var x = ADD(index,1,offset)
```
```
//after processing

var x = index + 1 + offset
```
Arguments are a list of tokens (in this case `(A,B,C)`) that are taken from input tokens after the expanded define. Arguments are matched against the expected argument and the tokens that don't match are fed into identifiers that will be used later on as argument (in the example arguments are A, B and C).
For example `(A)` will math any content delimited by `(` `)`.

The tokens that are given for arguments are stored in a temporary define with the name of the argument name.

**Be carefull not to create infinite loops with argument names**:
```
#define ADD(ARG) # 1 + ARG

ADD(2 + ARG) // <- 'ADD(2 + ARG)' is first expanded into '2 + ARG'
//and because ARG is a define that holds '2 + ARG' -> infinite loop: '1 + 2 + 2 + 2 + 2 + ...'
```

Arguments are also separated by scopes: `()` `[]` `{}`
Example:
```
#define ALL_EQUIVALENT (A,B)
ALL_EQUIVALENT((1,b),c) //expands into nothing
ALL_EQUIVALENT([1,b],c) //expands into nothing
ALL_EQUIVALENT({1,b},c) //expands into nothing

for:
ALL_EQUIVALENT({1,2},c)
argument A is `{1,2}`
argument B is `c`
```


Conditional commands and their limitations
------------------------------------------

This onditional commands are always evaluated:
- ```#if```
- ```#ifdef```
- ```#ifndef```
- ```#else```
- ```#elif```
- ```#endif```

The rest of the tokens and commands are ignored if they are on a *false* branch. In the following example there have be no output tokens bacause the define is not expanded in the false branch:

```
#define CUSTOM_ELSE # #else

#if False:
	yes
CUSTOM_ELSE
	no
#endif
```





