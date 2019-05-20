
Tokens
------

Precompiler takes the source code and transforms it into token of certain types:
1. basic tokens. This include identifiers, signs, comments, whitespaces, etc
2. commands. They start with `#`
3. separators. This include `#\w` and `#\e` , `#\n` `#\t` `#\s` (explained below). A special separator is `$` that is used to separate macro argument from value

Command tokens
--------------

For syntax, the mandatory whitespace (tabs and spaces) is marked with `\w` and newline is marked with `\n`.
Tokens fall into certain cathegories:
1. `__ID__` = identifier
2. `__STR__` = string starting with `"` or `'`.
3. `__PATH__` = path to file. As a general rule all arguments of type `__PATH__` can be given as the value of a macro.
4. `__PY__` = any python valid syntax

### define
Adds a named variable (macro) in the preprocessor. The value of the macro is nothing more than a list of tokens taken from the line of the definition (`__VALUE`):

Syntax:
1. `#define \w __ID__ [\w [_ARGUMENTS $] _VALUE] \n`
3. `_ARGUMENTS` is optional along with the separator `$` separator. If multiple separators `$` are present the first one is selected.
4. `_VALUE` can be anything

Note that if `_ARGUMENTS` are missing (given by `$` separator) then the define value is given by all tokens after the `__ID__` token.

### undefine
Removes the variable from preprocessor. Throws error if variable does not exist.

Syntax:
- `#undef \w __ID__`

### redefine
A combination of `#undef` and `#define`

Syntax (is the same as the `#define`):
- `#redefine ...`

### collapse
Reasgines the define value with it's processed value.

Syntax:
- `#collapse \w __ID__`

Exampled:
```
#define a 1 + 2 + 3 + 4
#define foo a + b
#collapse foo
//foo becomes `1 + 2 + 3 + 4 + b` instead of `a + b`

```

### cwstrip (comments and whitespaces strip)
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
4. `info` will output a comment containing information about the source file


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

### config
Will load a markup file. 

Syntax:
1. `#include \w __PATH__`
2. `#include \w __ID__`

Supported formats:
1. `.ini` Each ini entry will be added as a upper case define with `_CFG_` added. Example ini `[DEFAULT] \n some_value = 10` will add a define `_CFG_SOME_VALUE` with value `10`


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
1. `#inline-run \w __PY__\n`

### run
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

Separators
----------

### forward whitespace
Captures the rest of the whitespaces and returns it as token. When used as define arguments this can be used as a delimiter.

Syntax:
1. `#w \w`

### whitespace
This tokens eat all whitespaces that follow them and result token is one of the following:

1. `#\n` is a newline
2. `#\t` is a tab
3. `#\s` is a space

### empty separator
Will eat all following whitespaces be transformed into a token without any character. This can be used when you want to separate tokens whitout whitespace.

Syntax:
1. `#\e`

As an example `identifier1#\e         Widentifier2` will generate two tokens separated by a blank whitespace token : `identifier1Widentifier2`

Builtin macros
--------------

1. `__FILE__` Return the absolute path to the current preprocessed file as string token
2. `__FILENAME__` Return the name of the current preprocessed file as string token
3. `__FILEROOT__` Return the absolute path of the file folder as string token
4. `__PCVER__` Precompiler internal version as string (ex "0.1.2")
5. `__PCVER_HIGH__` Precompiler internal version as int number (ex 0)
6. `__PCVER_LOW__` Precompiler internal version as float number (ex 1.2)
7. `__LINE__` Current line as number
7. `__NOW_TIME__` Current time as string. Format `%I-%M%p-%b-%d` (note that time is queried when macro is expanded)


Python eval functions
---------------------

1. `defined(macro_name_str)` -> *True/False* > checks if a macro with name `macro_name_str` is defined or not
2. `value(macro_name_str)` -> *Str* > returnes the string value of a macro named `macro_name_str`. Returns None if macro does not exist
3. `tokens(macro_name_str)` -> *[token]* > returnes value of macro named `macro_name_str` in the form of token list. None if macro does not exist


File search paths
-----------------
Any command that takes `__PATH__` as an argument will first process the path by replacing all `{IDENTIFIER}` substrings with content search from (in this order):

1. `IDENTIFIER` in api dictionary in file manager.
2. `IDENTIFIER` in environment variables.

Example:
`#include "{PROJECT_DIR}/engine/math.h"` where `PROJECT_DIR` is an enviroment variable with value `/work`, the result will be `#include "/work/engine/math.h"`

File paths given to `include` or to `#inline-include` are searched in the following order:

1. First the patch is checked if it exists (unprocessed, note that current working directory could also affect this result)
2. folder of the current processed file + include path. This is useful relative to your file searches `"../engine/whatever.h"`
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
#define ADD(A,B,C) $ A + B + C
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
#define ADD(ARG) $ 1 + ARG

ADD(2 + ARG) // <- 'ADD(2 + ARG)' is first expanded into '2 + ARG'
//and because ARG is a define that holds '2 + ARG' -> infinite loop: '1 + 2 + 2 + 2 + 2 + ...'
```

Arguments are also separated by scopes: `()` `[]` `{}`
Example:
```
#define ALL_EQUIVALENT (A,B) $
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
#define CUSTOM_ELSE $ #else

#if False:
	yes
CUSTOM_ELSE
	no
#endif
```





