# Quick Reference

*Style guide, encoding, keywords, and appendix*

## Style Guide

These coding conventions are not enforced by the compiler, but they are shipped in
this documentation along with the compiler in order to provide a point of
reference, should anyone wish to point to an authority on agreed upon Zig
coding style.

### Avoid Redundancy in Names

Avoid these words in type names:

- Value
- Data
- Context
- Manager
- State
- utils, misc, or somebody's initials

Everything is a value, all types are data, everything is context, all logic manages state.
Nothing is communicated by using a word that applies to all types.

Temptation to use "utilities", "miscellaneous", or somebody's initials
is a failure to categorize, or more commonly, overcategorization. Such
declarations can live at the root of a module that needs them with no
namespace needed.

### Avoid Redundant Names in Fully-Qualified Namespaces

Every declaration is assigned a **fully qualified
namespace** by the compiler, creating a tree structure. Choose names based
on the fully-qualified namespace, and avoid redundant name segments.

**`redundant_fqn.zig`:**

```zig
const std = @import("std");

pub const json = struct {
    pub const JsonValue = union(enum) {
        number: f64,
        boolean: bool,
        // ...
    };
};

pub fn main() void {
    std.debug.print("{s}\n", .{@typeName(json.JsonValue)});
}

```

**Shell:**

```shell
$ zig build-exe redundant_fqn.zig
$ ./redundant_fqn
redundant_fqn.json.JsonValue

```

In this example, "json" is repeated in the fully-qualified namespace. The solution
is to delete `Json` from `JsonValue`. In this example we have
an empty struct named `json` but remember that files also act
as part of the fully-qualified namespace.

This example is an exception to the rule specified in [Avoid Redundancy in Names](#Avoid-Redundancy-in-Names).
The meaning of the type has been reduced to its core: it is a json value. The name
cannot be any more specific without being incorrect.

### Refrain from Underscore Prefixes

In some programming languages, it is common to prefix identifiers with
underscores `_like_this` to avoid keyword
collisions, name collisions, or indicate additional metadata associated with usage of the
identifier, such as: privacy, existence of complex data invariants, exclusion from
semantic versioning, or context-specific type reflection meaning.

In Zig, there are no private fields, and this style guide recommends
against pretending otherwise. Instead, fields should be named carefully
based on their semantics and documentation should indicate how to use
fields without violating data invariants. If a field is not subject to
the same semantic versioning rules as everything else, the exception
should be noted in the [Doc Comments](#Doc-Comments).

As for [type reflection](#typeInfo), it is less error prone and
more maintainable to use the type system than to make field names
meaningful.

Regarding name collisions, an underscore is insufficient to explain
the difference between the two otherwise identical names. If there's no
danger in getting them mixed up, then this guide recommends more verbose
names at outer scopes and more abbreviated names at inner scopes.

Finally, keyword collisions are better avoided via
[String Identifier Syntax](#String-Identifier-Syntax).

### Whitespace

- 4 space indentation
- Open braces on same line, unless you need to wrap.
- If a list of things is longer than 2, put each item on its own line and
  exercise the ability to put an extra comma at the end.
- Line length: aim for 100; use common sense.

### Names

Roughly speaking: `camelCaseFunctionName`, `TitleCaseTypeName`,
`snake_case_variable_name`. More precisely:

- If `x` is a `struct` with 0 fields and is never meant to be instantiated
  then `x` is considered to be a "namespace" and should be `snake_case`.
- If `x` is a `type` or `type` alias
  then `x` should be `TitleCase`.
- If `x` is callable, and `x`'s return type is
  `type`, then `x` should be `TitleCase`.
- If `x` is otherwise callable, then `x` should
  be `camelCase`.
- Otherwise, `x` should be `snake_case`.

Acronyms, initialisms, proper nouns, or any other word that has capitalization
rules in written English are subject to naming conventions just like any other
word. Even acronyms that are only 2 letters long are subject to these
conventions.

File names fall into two categories: types and namespaces. If the file
(implicitly a struct) has top level fields, it should be named like any
other struct with fields using `TitleCase`. Otherwise,
it should use `snake_case`. Directory names should be
`snake_case`.

These are general rules of thumb; if it makes sense to do something different,
do what makes sense. For example, if there is an established convention such as
`ENOENT`, follow the established convention.

### Examples

**`style_example.zig`:**

```zig
const namespace_name = @import("dir_name/file_name.zig");
const TypeName = @import("dir_name/TypeName.zig");
var global_var: i32 = undefined;
const const_name = 42;
const PrimitiveTypeAlias = f32;

const StructName = struct {
    field: i32,
};
const StructAlias = StructName;

fn functionName(param_name: TypeName) void {
    var functionPointer = functionName;
    functionPointer();
    functionPointer = otherFunction;
    functionPointer();
}
const functionAlias = functionName;

fn ListTemplateFunction(comptime ChildType: type, comptime fixed_size: usize) type {
    return List(ChildType, fixed_size);
}

fn ShortList(comptime T: type, comptime n: usize) type {
    return struct {
        field_name: [n]T,
        fn methodName() void {}
    };
}

// The word XML loses its casing when used in Zig identifiers.
const xml_document =
    \\<?xml version="1.0" encoding="UTF-8"?>
    \\<document>
    \\</document>
;
const XmlParser = struct {
    field: i32,
};

// The initials BE (Big Endian) are just another word in Zig identifier names.
fn readU32Be() u32 {}

```

See the [Zig Standard Library](02-zig-standard-library.md#Zig-Standard-Library) for more examples.

### Doc Comment Guidance

- Omit any information that is redundant based on the name of the thing being documented.
- Duplicating information onto multiple similar functions is encouraged because it helps IDEs and other tools provide better help text.
- Use the word **assume** to indicate invariants that cause *unchecked* [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior) when violated.
- Use the word **assert** to indicate invariants that cause *safety-checked* [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior) when violated.

---

## Source Encoding

Zig source code is encoded in UTF-8. An invalid UTF-8 byte sequence results in a compile error.

Throughout all zig source code (including in comments), some code points are never allowed:

- Ascii control characters, except for U+000a (LF), U+000d (CR), and U+0009 (HT): U+0000 - U+0008, U+000b - U+000c, U+000e - U+0001f, U+007f.
- Non-Ascii Unicode line endings: U+0085 (NEL), U+2028 (LS), U+2029 (PS).

LF (byte value 0x0a, code point U+000a, `'\n'`) is the line terminator in Zig source code.
This byte value terminates every line of zig source code except the last line of the file.
It is recommended that non-empty source files end with an empty line, which means the last byte would be 0x0a (LF).

Each LF may be immediately preceded by a single CR (byte value 0x0d, code point U+000d, `'\r'`)
to form a Windows style line ending, but this is discouraged. Note that in multiline strings, CRLF sequences will
be encoded as LF when compiled into a zig program.
A CR in any other context is not allowed.

HT hard tabs (byte value 0x09, code point U+0009, `'\t'`) are interchangeable with
SP spaces (byte value 0x20, code point U+0020, `' '`) as a token separator,
but use of hard tabs is discouraged. See [Grammar](#Grammar).

For compatibility with other tools, the compiler ignores a UTF-8-encoded byte order mark (U+FEFF)
if it is the first Unicode code point in the source text. A byte order mark is not allowed anywhere else in the source.

Note that running `zig fmt` on a source file will implement all recommendations mentioned here.

Note that a tool reading Zig source code can make assumptions if the source code is assumed to be correct Zig code.
For example, when identifying the ends of lines, a tool can use a naive search such as `/\n/`,
or an [advanced](https://msdn.microsoft.com/en-us/library/dd409797.aspx)
search such as `/\r\n?|[\n\u0085\u2028\u2029]/`, and in either case line endings will be correctly identified.
For another example, when identifying the whitespace before the first token on a line,
a tool can either use a naive search such as `/[ \t]/`,
or an [advanced](https://tc39.es/ecma262/#sec-characterclassescape) search such as `/\s/`,
and in either case whitespace will be correctly identified.

---

## Keyword Reference

| Keyword | Description |
| --- | --- |
| `addrspace` | The `addrspace` keyword.  - TODO add documentation for addrspace |
| `align` | `align` can be used to specify the alignment of a pointer. It can also be used after a variable or function declaration to specify the alignment of pointers to that variable or function.  - See also [Alignment](#Alignment) |
| `allowzero` | The pointer attribute `allowzero` allows a pointer to have address zero.  - See also [allowzero](#allowzero) |
| `and` | The boolean operator `and`.  - See also [Operators](11-operators.md#Operators) |
| `anyframe` | `anyframe` can be used as a type for variables which hold pointers to function frames.  - See also [Async Functions](37-async-functions.md#Async-Functions) |
| `anytype` | Function parameters can be declared with `anytype` in place of the type. The type will be inferred where the function is called.  - See also [Function Parameter Type Inference](#Function-Parameter-Type-Inference) |
| `asm` | `asm` begins an inline assembly expression. This allows for directly controlling the machine code generated on compilation.  - See also [Assembly](35-assembly.md#Assembly) |
| `break` | `break` can be used with a block label to return a value from the block. It can also be used to exit a loop before iteration completes naturally.  - See also [Blocks](20-blocks.md#Blocks), [while](22-while.md#while), [for](23-for.md#for) |
| `callconv` | `callconv` can be used to specify the calling convention in a function type.  - See also [Functions](28-functions.md#Functions) |
| `catch` | `catch` can be used to evaluate an expression if the expression before it evaluates to an error. The expression after the `catch` can optionally capture the error value.  - See also [catch](#catch), [Operators](11-operators.md#Operators) |
| `comptime` | `comptime` before a declaration can be used to label variables or function parameters as known at compile time. It can also be used to guarantee an expression is run at compile time.  - See also [comptime](34-comptime.md#comptime) |
| `const` | `const` declares a variable that can not be modified. Used as a pointer attribute, it denotes the value referenced by the pointer cannot be modified.  - See also [Variables](08-variables.md#Variables) |
| `continue` | `continue` can be used in a loop to jump back to the beginning of the loop.  - See also [while](22-while.md#while), [for](23-for.md#for) |
| `defer` | `defer` will execute an expression when control flow leaves the current block.  - See also [defer](25-defer.md#defer) |
| `else` | `else` can be used to provide an alternate branch for `if`, `switch`, `while`, and `for` expressions.  - If used after an if expression, the else branch will be executed if the test value returns false, null, or an error. - If used within a switch expression, the else branch will be executed if the test value matches no other cases. - If used after a loop expression, the else branch will be executed if the loop finishes without breaking. - See also [if](24-if.md#if), [switch](21-switch.md#switch), [while](22-while.md#while), [for](23-for.md#for) |
| `enum` | `enum` defines an enum type.  - See also [enum](17-enum.md#enum) |
| `errdefer` | `errdefer` will execute an expression when control flow leaves the current block if the function returns an error, the errdefer expression can capture the unwrapped value.  - See also [errdefer](#errdefer) |
| `error` | `error` defines an error type.  - See also [Errors](29-errors.md#Errors) |
| `export` | `export` makes a function or variable externally visible in the generated object file. Exported functions default to the C calling convention.  - See also [Functions](28-functions.md#Functions) |
| `extern` | `extern` can be used to declare a function or variable that will be resolved at link time, when linking statically or at runtime, when linking dynamically.  - See also [Functions](28-functions.md#Functions) |
| `fn` | `fn` declares a function.  - See also [Functions](28-functions.md#Functions) |
| `for` | A `for` expression can be used to iterate over the elements of a slice, array, or tuple.  - See also [for](23-for.md#for) |
| `if` | An `if` expression can test boolean expressions, optional values, or error unions. For optional values or error unions, the if expression can capture the unwrapped value.  - See also [if](24-if.md#if) |
| `inline` | `inline` can be used to label a loop expression such that it will be unrolled at compile time. It can also be used to force a function to be inlined at all call sites.  - See also [inline while](#inline-while), [inline for](#inline-for), [Functions](28-functions.md#Functions) |
| `linksection` | The `linksection` keyword can be used to specify what section the function or global variable will be put into (e.g. `.text`). |
| `noalias` | The `noalias` keyword.  - TODO add documentation for noalias |
| `noinline` | `noinline` disallows function to be inlined in all call sites.  - See also [Functions](28-functions.md#Functions) |
| `nosuspend` | The `nosuspend` keyword can be used in front of a block, statement or expression, to mark a scope where no suspension points are reached. In particular, inside a `nosuspend` scope:  - Using the `suspend` keyword results in a compile error. - Using `await` on a function frame which hasn't completed yet results in safety-checked [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior). - Calling an async function may result in safety-checked [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior), because it's equivalent to `await async some_async_fn()`, which contains an `await`.  Code inside a `nosuspend` scope does not cause the enclosing function to become an [async function](37-async-functions.md#Async-Functions).  - See also [Async Functions](37-async-functions.md#Async-Functions) |
| `opaque` | `opaque` defines an opaque type.  - See also [opaque](19-opaque.md#opaque) |
| `or` | The boolean operator `or`.  - See also [Operators](11-operators.md#Operators) |
| `orelse` | `orelse` can be used to evaluate an expression if the expression before it evaluates to null.  - See also [Optionals](30-optionals.md#Optionals), [Operators](11-operators.md#Operators) |
| `packed` | The `packed` keyword before a struct definition changes the struct's in-memory layout to the guaranteed `packed` layout.  - See also [packed struct](#packed-struct) |
| `pub` | The `pub` in front of a top level declaration makes the declaration available to reference from a different file than the one it is declared in.  - See also [import](#import) |
| `resume` | `resume` will continue execution of a function frame after the point the function was suspended. |
| `return` | `return` exits a function with a value.  - See also [Functions](28-functions.md#Functions) |
| `struct` | `struct` defines a struct.  - See also [struct](16-struct.md#struct) |
| `suspend` | `suspend` will cause control flow to return to the call site or resumer of the function. `suspend` can also be used before a block within a function, to allow the function access to its frame before control flow returns to the call site. |
| `switch` | A `switch` expression can be used to test values of a common type. `switch` cases can capture field values of a [Tagged union](#Tagged-union).  - See also [switch](21-switch.md#switch) |
| `test` | The `test` keyword can be used to denote a top-level block of code used to make sure behavior meets expectations.  - See also [Zig Test](07-zig-test.md#Zig-Test) |
| `threadlocal` | `threadlocal` can be used to specify a variable as thread-local.  - See also [Thread Local Variables](#Thread-Local-Variables) |
| `try` | `try` evaluates an error union expression. If it is an error, it returns from the current function with the same error. Otherwise, the expression results in the unwrapped value.  - See also [try](#try) |
| `union` | `union` defines a union.  - See also [union](18-union.md#union) |
| `unreachable` | `unreachable` can be used to assert that control flow will never happen upon a particular location. Depending on the build mode, `unreachable` may emit a panic.  - Emits a panic in `Debug` and `ReleaseSafe` mode, or when using `zig test`. - Does not emit a panic in `ReleaseFast` and `ReleaseSmall` mode. - See also [unreachable](26-unreachable.md#unreachable) |
| `var` | `var` declares a variable that may be modified.  - See also [Variables](08-variables.md#Variables) |
| `volatile` | `volatile` can be used to denote loads or stores of a pointer have side effects. It can also modify an inline assembly expression to denote it has side effects.  - See also [volatile](#volatile), [Assembly](35-assembly.md#Assembly) |
| `while` | A `while` expression can be used to repeatedly test a boolean, optional, or error union expression, and cease looping when that expression evaluates to false, null, or an error, respectively.  - See also [while](22-while.md#while) |

---

## Appendix

### Containers

A *container* in Zig is any syntactical construct that acts as a namespace to hold [variable](46-c.md#Container-Level-Variables) and [function](28-functions.md#Functions) declarations.
Containers are also type definitions which can be instantiated.
[Structs](16-struct.md#struct), [enums](17-enum.md#enum), [unions](18-union.md#union), [opaques](19-opaque.md#opaque), and even Zig source files themselves are containers.

Although containers (except Zig source files) use curly braces to surround their definition, they should not be confused with [blocks](20-blocks.md#Blocks) or functions.
Containers do not contain statements.

### Grammar

**grammar.peg:**

```peg
Root <- skip ContainerMembers eof

# *** Top level ***
ContainerMembers <- container_doc_comment? ContainerDeclaration* (ContainerField COMMA)* (ContainerField / ContainerDeclaration*)

ContainerDeclaration <- TestDecl / ComptimeDecl / doc_comment? KEYWORD_pub? Decl

TestDecl <- KEYWORD_test (STRINGLITERALSINGLE / IDENTIFIER)? Block

ComptimeDecl <- KEYWORD_comptime Block

Decl
    <- (KEYWORD_export / KEYWORD_inline / KEYWORD_noinline)? FnProto (SEMICOLON / Block)
     / KEYWORD_extern STRINGLITERALSINGLE? FnProto SEMICOLON
     / (KEYWORD_export / KEYWORD_extern STRINGLITERALSINGLE?)? KEYWORD_threadlocal? GlobalVarDecl

FnProto <- KEYWORD_fn IDENTIFIER? LPAREN ParamDeclList RPAREN ByteAlign? AddrSpace? LinkSection? CallConv? EXCLAMATIONMARK? TypeExpr !ExprSuffix

VarDeclProto <- (KEYWORD_const / KEYWORD_var) IDENTIFIER (COLON TypeExpr)? ByteAlign? AddrSpace? LinkSection?

GlobalVarDecl <- VarDeclProto (EQUAL Expr)? SEMICOLON

ContainerField <- doc_comment? (KEYWORD_comptime / !KEYWORD_comptime) !KEYWORD_fn (IDENTIFIER COLON / !(IDENTIFIER COLON))? TypeExpr ByteAlign? (EQUAL Expr)?

# *** Block Level ***
BlockStatement
    <- Statement
     / KEYWORD_defer BlockExprStatement
     / KEYWORD_errdefer Payload? BlockExprStatement
     / !ExprStatement (KEYWORD_comptime !BlockExpr)? VarAssignStatement

Statement
    <- ExprStatement
     / KEYWORD_suspend BlockExprStatement
     / !ExprStatement (KEYWORD_comptime !BlockExpr)? AssignExpr SEMICOLON

ExprStatement
    <- IfStatement
     / LabeledStatement
     / KEYWORD_nosuspend BlockExprStatement
     / KEYWORD_comptime BlockExpr

IfStatement
    <- IfPrefix BlockExpr ( KEYWORD_else Payload? Statement )?
     / IfPrefix !BlockExpr AssignExpr ( SEMICOLON / KEYWORD_else Payload? Statement )

LabeledStatement <- BlockLabel? (Block / LoopStatement / SwitchExpr)

LoopStatement <- KEYWORD_inline? (ForStatement / WhileStatement)

ForStatement
    <- ForPrefix BlockExpr ( KEYWORD_else Statement / !KEYWORD_else )
     / ForPrefix !BlockExpr AssignExpr ( SEMICOLON / KEYWORD_else Statement )

WhileStatement
    <- WhilePrefix BlockExpr ( KEYWORD_else Payload? Statement )?
     / WhilePrefix !BlockExpr AssignExpr ( SEMICOLON / KEYWORD_else Payload? Statement )

BlockExprStatement
    <- BlockExpr
     / !BlockExpr AssignExpr SEMICOLON

BlockExpr <- BlockLabel? Block

# An assignment or a destructure whose LHS are all lvalue expressions or variable declarations.
VarAssignStatement <- (VarDeclProto / Expr) (COMMA (VarDeclProto / Expr))* EQUAL Expr SEMICOLON

# *** Expression Level ***

# An assignment or a destructure whose LHS are all lvalue expressions.
AssignExpr <- Expr (AssignOp Expr / (COMMA Expr)+ EQUAL Expr)?

SingleAssignExpr <- Expr (AssignOp Expr)?

Expr <- BoolOrExpr

BoolOrExpr <- BoolAndExpr (KEYWORD_or BoolAndExpr)*

BoolAndExpr <- CompareExpr (KEYWORD_and CompareExpr)*

CompareExpr <- BitwiseExpr (CompareOp BitwiseExpr)?

BitwiseExpr <- BitShiftExpr (BitwiseOp BitShiftExpr)*

BitShiftExpr <- AdditionExpr (BitShiftOp AdditionExpr)*

AdditionExpr <- MultiplyExpr (AdditionOp MultiplyExpr)*

MultiplyExpr <- PrefixExpr (MultiplyOp PrefixExpr)*

PrefixExpr <- PrefixOp* PrimaryExpr

PrimaryExpr
    <- AsmExpr
     / IfExpr
     / KEYWORD_break (BreakLabel / !BreakLabel) (Expr !ExprSuffix / !SinglePtrTypeStart)
     / KEYWORD_comptime Expr !ExprSuffix
     / KEYWORD_nosuspend Expr !ExprSuffix
     / KEYWORD_continue (BreakLabel / !BreakLabel) (Expr !ExprSuffix / !SinglePtrTypeStart)
     / KEYWORD_resume Expr !ExprSuffix
     / KEYWORD_return (Expr !ExprSuffix / !SinglePtrTypeStart)
     / BlockLabel? LoopExpr
     / Block
     / CurlySuffixExpr

IfExpr <- IfPrefix Expr (KEYWORD_else Payload? Expr)? !ExprSuffix

Block <- LBRACE BlockStatement* RBRACE

LoopExpr <- KEYWORD_inline? (ForExpr / WhileExpr)

ForExpr <- ForPrefix Expr (KEYWORD_else Expr / !KEYWORD_else) !ExprSuffix

WhileExpr <- WhilePrefix Expr (KEYWORD_else Payload? Expr)? !ExprSuffix

CurlySuffixExpr <- TypeExpr InitList?

InitList
    <- LBRACE FieldInit (COMMA FieldInit)* COMMA? RBRACE
     / LBRACE Expr (COMMA Expr)* COMMA? RBRACE
     / LBRACE RBRACE

TypeExpr <- PrefixTypeOp* ErrorUnionExpr

ErrorUnionExpr <- SuffixExpr (EXCLAMATIONMARK TypeExpr)?

SuffixExpr
    <- PrimaryTypeExpr (SuffixOp / FnCallArguments)*

PrimaryTypeExpr
    <- BUILTINIDENTIFIER FnCallArguments
     / CHAR_LITERAL
     / ContainerDecl
     / DOT IDENTIFIER
     / DOT InitList
     / ErrorSetDecl
     / FLOAT
     / FnProto
     / GroupedExpr
     / LabeledTypeExpr
     / IDENTIFIER !(COLON LabelableExpr)
     / IfTypeExpr
     / INTEGER
     / KEYWORD_comptime TypeExpr !ExprSuffix
     / KEYWORD_error DOT IDENTIFIER
     / KEYWORD_anyframe
     / KEYWORD_unreachable
     / STRINGLITERAL

ContainerDecl <- (KEYWORD_extern / KEYWORD_packed)? ContainerDeclAuto

ErrorSetDecl <- KEYWORD_error LBRACE IdentifierList RBRACE

GroupedExpr <- LPAREN Expr RPAREN

IfTypeExpr <- IfPrefix TypeExpr (KEYWORD_else Payload? TypeExpr)? !ExprSuffix

LabeledTypeExpr
    <- BlockLabel Block
     / BlockLabel? LoopTypeExpr
     / BlockLabel? SwitchExpr

LoopTypeExpr <- KEYWORD_inline? (ForTypeExpr / WhileTypeExpr)

ForTypeExpr <- ForPrefix TypeExpr (KEYWORD_else TypeExpr / !KEYWORD_else) !ExprSuffix

WhileTypeExpr <- WhilePrefix TypeExpr (KEYWORD_else Payload? TypeExpr)? !ExprSuffix

SwitchExpr <- KEYWORD_switch LPAREN Expr RPAREN LBRACE SwitchProngList RBRACE

# *** Assembly ***
AsmExpr <- KEYWORD_asm KEYWORD_volatile? LPAREN Expr AsmOutput? RPAREN

AsmOutput <- COLON AsmOutputList AsmInput?

AsmOutputItem <- LBRACKET IDENTIFIER RBRACKET STRINGLITERALSINGLE LPAREN (MINUSRARROW TypeExpr / IDENTIFIER) RPAREN

AsmInput <- COLON AsmInputList AsmClobbers?

AsmInputItem <- LBRACKET IDENTIFIER RBRACKET STRINGLITERALSINGLE LPAREN Expr RPAREN

AsmClobbers <- COLON Expr

# *** Helper grammar ***
BreakLabel <- COLON IDENTIFIER

BlockLabel <- IDENTIFIER COLON

FieldInit <- DOT IDENTIFIER EQUAL Expr

WhileContinueExpr <- COLON LPAREN AssignExpr RPAREN

LinkSection <- KEYWORD_linksection LPAREN Expr RPAREN

AddrSpace <- KEYWORD_addrspace LPAREN Expr RPAREN

# Fn specific
CallConv <- KEYWORD_callconv LPAREN Expr RPAREN

ParamDecl <- doc_comment? (KEYWORD_noalias / KEYWORD_comptime / !KEYWORD_comptime) (IDENTIFIER COLON / !(IDENTIFIER_COLON)) ParamType

ParamType
    <- KEYWORD_anytype
     / TypeExpr

# Control flow prefixes
IfPrefix <- KEYWORD_if LPAREN Expr RPAREN PtrPayload?

WhilePrefix <- KEYWORD_while LPAREN Expr RPAREN PtrPayload? WhileContinueExpr?

ForPrefix <- KEYWORD_for LPAREN ForArgumentsList RPAREN PtrListPayload

# Payloads
Payload <- PIPE IDENTIFIER PIPE

PtrPayload <- PIPE ASTERISK? IDENTIFIER PIPE

PtrIndexPayload <- PIPE ASTERISK? IDENTIFIER (COMMA IDENTIFIER)? PIPE

PtrListPayload <- PIPE ASTERISK? IDENTIFIER (COMMA ASTERISK? IDENTIFIER)* COMMA? PIPE

# Switch specific
SwitchProng <- KEYWORD_inline? SwitchCase EQUALRARROW PtrIndexPayload? SingleAssignExpr

SwitchCase
    <- SwitchItem (COMMA SwitchItem)* COMMA?
     / KEYWORD_else

SwitchItem <- Expr (DOT3 Expr)?

# For specific
ForArgumentsList <- ForItem (COMMA ForItem)* COMMA?

ForItem <- Expr (DOT2 Expr?)?

# Operators
AssignOp
    <- ASTERISKEQUAL
     / ASTERISKPIPEEQUAL
     / SLASHEQUAL
     / PERCENTEQUAL
     / PLUSEQUAL
     / PLUSPIPEEQUAL
     / MINUSEQUAL
     / MINUSPIPEEQUAL
     / LARROW2EQUAL
     / LARROW2PIPEEQUAL
     / RARROW2EQUAL
     / AMPERSANDEQUAL
     / CARETEQUAL
     / PIPEEQUAL
     / ASTERISKPERCENTEQUAL
     / PLUSPERCENTEQUAL
     / MINUSPERCENTEQUAL
     / EQUAL

CompareOp
    <- EQUALEQUAL
     / EXCLAMATIONMARKEQUAL
     / LARROW
     / RARROW
     / LARROWEQUAL
     / RARROWEQUAL

BitwiseOp
    <- AMPERSAND
     / CARET
     / PIPE
     / KEYWORD_orelse
     / KEYWORD_catch Payload?

BitShiftOp
    <- LARROW2
     / RARROW2
     / LARROW2PIPE

AdditionOp
    <- PLUS
     / MINUS
     / PLUS2
     / PLUSPERCENT
     / MINUSPERCENT
     / PLUSPIPE
     / MINUSPIPE

MultiplyOp
    <- PIPE2
     / ASTERISK
     / SLASH
     / PERCENT
     / ASTERISK2
     / ASTERISKPERCENT
     / ASTERISKPIPE

PrefixOp
    <- EXCLAMATIONMARK
     / MINUS
     / TILDE
     / MINUSPERCENT
     / AMPERSAND
     / KEYWORD_try

PrefixTypeOp
    <- QUESTIONMARK
     / KEYWORD_anyframe MINUSRARROW
     / (ManyPtrTypeStart / SliceTypeStart) KEYWORD_allowzero? ByteAlign? AddrSpace? KEYWORD_const? KEYWORD_volatile?
     / SinglePtrTypeStart KEYWORD_allowzero? BitAlign? AddrSpace? KEYWORD_const? KEYWORD_volatile?
     / ArrayTypeStart

SuffixOp
    <- LBRACKET Expr (DOT2 (Expr? (COLON Expr)?)?)? RBRACKET
     / DOT IDENTIFIER
     / DOTASTERISK
     / DOTQUESTIONMARK

FnCallArguments <- LPAREN ExprList RPAREN

ExprSuffix
    <- KEYWORD_or
     / KEYWORD_and
     / CompareOp
     / BitwiseOp
     / BitShiftOp
     / AdditionOp
     / MultiplyOp
     / EXCLAMATIONMARK
     / SuffixOp
     / FnCallArguments

LabelableExpr
    <- Block
     / SwitchExpr
     / LoopExpr

# Ptr specific
SliceTypeStart <- LBRACKET (COLON Expr)? RBRACKET

SinglePtrTypeStart <- ASTERISK / ASTERISK2

ManyPtrTypeStart <- LBRACKET ASTERISK (LETTERC / COLON Expr)? RBRACKET

ArrayTypeStart <- LBRACKET Expr !(ASTERISK / ASTERISK2) (COLON Expr)? RBRACKET

# ContainerDecl specific
ContainerDeclAuto <- ContainerDeclType LBRACE ContainerMembers RBRACE

ContainerDeclType
    <- KEYWORD_struct (LPAREN Expr RPAREN)?
     / KEYWORD_opaque
     / KEYWORD_enum (LPAREN Expr RPAREN)?
     / KEYWORD_union (LPAREN (KEYWORD_enum (LPAREN Expr RPAREN)? / !KEYWORD_enum Expr) RPAREN)?

# Alignment
ByteAlign <- KEYWORD_align LPAREN Expr RPAREN

BitAlign <- KEYWORD_align LPAREN Expr (COLON Expr COLON Expr)? RPAREN

# Lists
IdentifierList <- (doc_comment? IDENTIFIER COMMA)* (doc_comment? IDENTIFIER)?

SwitchProngList <- (SwitchProng COMMA)* SwitchProng?

AsmOutputList <- (AsmOutputItem COMMA)* AsmOutputItem?

AsmInputList <- (AsmInputItem COMMA)* AsmInputItem?

ParamDeclList <- (ParamDecl COMMA)* (ParamDecl / DOT3 COMMA?)?

ExprList <- (Expr COMMA)* Expr?

# *** Tokens ***
eof <- !.
bin <- [01]
bin_ <- '_'? bin
oct <- [0-7]
oct_ <- '_'? oct
hex <- [0-9a-fA-F]
hex_ <- '_'? hex
dec <- [0-9]
dec_ <- '_'? dec

bin_int <- bin bin_*
oct_int <- oct oct_*
dec_int <- dec dec_*
hex_int <- hex hex_*

ox80_oxBF <- [\200-\277]
oxF4 <- '\364'
ox80_ox8F <- [\200-\217]
oxF1_oxF3 <- [\361-\363]
oxF0 <- '\360'
ox90_0xBF <- [\220-\277]
oxEE_oxEF <- [\356-\357]
oxED <- '\355'
ox80_ox9F <- [\200-\237]
oxE1_oxEC <- [\341-\354]
oxE0 <- '\340'
oxA0_oxBF <- [\240-\277]
oxC2_oxDF <- [\302-\337]

# From https://lemire.me/blog/2018/05/09/how-quickly-can-you-check-that-a-string-is-valid-unicode-utf-8/
# First Byte      Second Byte     Third Byte      Fourth Byte
# [0x00,0x7F]
# [0xC2,0xDF]     [0x80,0xBF]
#    0xE0         [0xA0,0xBF]     [0x80,0xBF]
# [0xE1,0xEC]     [0x80,0xBF]     [0x80,0xBF]
#    0xED         [0x80,0x9F]     [0x80,0xBF]
# [0xEE,0xEF]     [0x80,0xBF]     [0x80,0xBF]
#    0xF0         [0x90,0xBF]     [0x80,0xBF]     [0x80,0xBF]
# [0xF1,0xF3]     [0x80,0xBF]     [0x80,0xBF]     [0x80,0xBF]
#    0xF4         [0x80,0x8F]     [0x80,0xBF]     [0x80,0xBF]

multibyte_utf8 <-
       oxF4      ox80_ox8F ox80_oxBF ox80_oxBF
     / oxF1_oxF3 ox80_oxBF ox80_oxBF ox80_oxBF
     / oxF0      ox90_0xBF ox80_oxBF ox80_oxBF
     / oxEE_oxEF ox80_oxBF ox80_oxBF
     / oxED      ox80_ox9F ox80_oxBF
     / oxE1_oxEC ox80_oxBF ox80_oxBF
     / oxE0      oxA0_oxBF ox80_oxBF
     / oxC2_oxDF ox80_oxBF

non_control_ascii <- [\040-\176]
non_control_utf8 <- [\040-\377]

char_escape
    <- "\\x" hex hex
     / "\\u{" hex+ "}"
     / "\\" [nr\\t'"]
char_char
    <- multibyte_utf8
     / char_escape
     / ![\\'\n] non_control_ascii

string_char
    <- multibyte_utf8
     / char_escape
     / ![\\"\n] non_control_ascii

container_doc_comment <- ('//!' non_control_utf8* [ \n]* skip)+
doc_comment <- ('///' non_control_utf8* [ \n]* skip)+
line_comment <- '//' ![!/] non_control_utf8* / '////' non_control_utf8*
line_string <- '\\\\' non_control_utf8* [ \n]*
skip <- ([ \n] / line_comment)*

CHAR_LITERAL <- ['] char_char ['] skip
FLOAT
    <- '0x' hex_int '.' hex_int ([pP] [-+]? dec_int)? skip
     /      dec_int '.' dec_int ([eE] [-+]? dec_int)? skip
     / '0x' hex_int [pP] [-+]? dec_int skip
     /      dec_int [eE] [-+]? dec_int skip
INTEGER
    <- '0b' bin_int skip
     / '0o' oct_int skip
     / '0x' hex_int skip
     /      dec_int   skip
STRINGLITERALSINGLE <- ["] string_char* ["] skip
STRINGLITERAL
    <- STRINGLITERALSINGLE
     / (line_string                 skip)+
IDENTIFIER
    <- !keyword [A-Za-z_] [A-Za-z0-9_]* skip
     / '@' STRINGLITERALSINGLE
BUILTINIDENTIFIER <- '@'[A-Za-z_][A-Za-z0-9_]* skip


AMPERSAND            <- '&'      ![=]      skip
AMPERSANDEQUAL       <- '&='               skip
ASTERISK             <- '*'      ![*%=|]   skip
ASTERISK2            <- '**'               skip
ASTERISKEQUAL        <- '*='               skip
ASTERISKPERCENT      <- '*%'     ![=]      skip
ASTERISKPERCENTEQUAL <- '*%='              skip
ASTERISKPIPE         <- '*|'     ![=]      skip
ASTERISKPIPEEQUAL    <- '*|='              skip
CARET                <- '^'      ![=]      skip
CARETEQUAL           <- '^='               skip
COLON                <- ':'                skip
COMMA                <- ','                skip
DOT                  <- '.'      ![*.?]    skip
DOT2                 <- '..'     ![.]      skip
DOT3                 <- '...'              skip
DOTASTERISK          <- '.*'               skip
DOTQUESTIONMARK      <- '.?'               skip
EQUAL                <- '='      ![>=]     skip
EQUALEQUAL           <- '=='               skip
EQUALRARROW          <- '=>'               skip
EXCLAMATIONMARK      <- '!'      ![=]      skip
EXCLAMATIONMARKEQUAL <- '!='               skip
LARROW               <- '<'      ![<=]     skip
LARROW2              <- '<<'     ![=|]     skip
LARROW2EQUAL         <- '<<='              skip
LARROW2PIPE          <- '<<|'    ![=]      skip
LARROW2PIPEEQUAL     <- '<<|='             skip
LARROWEQUAL          <- '<='               skip
LBRACE               <- '{'                skip
LBRACKET             <- '['                skip
LPAREN               <- '('                skip
MINUS                <- '-'      ![%=>|]   skip
MINUSEQUAL           <- '-='               skip
MINUSPERCENT         <- '-%'     ![=]      skip
MINUSPERCENTEQUAL    <- '-%='              skip
MINUSPIPE            <- '-|'     ![=]      skip
MINUSPIPEEQUAL       <- '-|='              skip
MINUSRARROW          <- '->'               skip
PERCENT              <- '%'      ![=]      skip
PERCENTEQUAL         <- '%='               skip
PIPE                 <- '|'      ![|=]     skip
PIPE2                <- '||'               skip
PIPEEQUAL            <- '|='               skip
PLUS                 <- '+'      ![%+=|]   skip
PLUS2                <- '++'               skip
PLUSEQUAL            <- '+='               skip
PLUSPERCENT          <- '+%'     ![=]      skip
PLUSPERCENTEQUAL     <- '+%='              skip
PLUSPIPE             <- '+|'     ![=]      skip
PLUSPIPEEQUAL        <- '+|='              skip
LETTERC              <- 'c'                skip
QUESTIONMARK         <- '?'                skip
RARROW               <- '>'      ![>=]     skip
RARROW2              <- '>>'     ![=]      skip
RARROW2EQUAL         <- '>>='              skip
RARROWEQUAL          <- '>='               skip
RBRACE               <- '}'                skip
RBRACKET             <- ']'                skip
RPAREN               <- ')'                skip
SEMICOLON            <- ';'                skip
SLASH                <- '/'      ![=]      skip
SLASHEQUAL           <- '/='               skip
TILDE                <- '~'                skip

end_of_word <- ![a-zA-Z0-9_] skip
KEYWORD_addrspace   <- 'addrspace'   end_of_word
KEYWORD_align       <- 'align'       end_of_word
KEYWORD_allowzero   <- 'allowzero'   end_of_word
KEYWORD_and         <- 'and'         end_of_word
KEYWORD_anyframe    <- 'anyframe'    end_of_word
KEYWORD_anytype     <- 'anytype'     end_of_word
KEYWORD_asm         <- 'asm'         end_of_word
KEYWORD_break       <- 'break'       end_of_word
KEYWORD_callconv    <- 'callconv'    end_of_word
KEYWORD_catch       <- 'catch'       end_of_word
KEYWORD_comptime    <- 'comptime'    end_of_word
KEYWORD_const       <- 'const'       end_of_word
KEYWORD_continue    <- 'continue'    end_of_word
KEYWORD_defer       <- 'defer'       end_of_word
KEYWORD_else        <- 'else'        end_of_word
KEYWORD_enum        <- 'enum'        end_of_word
KEYWORD_errdefer    <- 'errdefer'    end_of_word
KEYWORD_error       <- 'error'       end_of_word
KEYWORD_export      <- 'export'      end_of_word
KEYWORD_extern      <- 'extern'      end_of_word
KEYWORD_fn          <- 'fn'          end_of_word
KEYWORD_for         <- 'for'         end_of_word
KEYWORD_if          <- 'if'          end_of_word
KEYWORD_inline      <- 'inline'      end_of_word
KEYWORD_noalias     <- 'noalias'     end_of_word
KEYWORD_nosuspend   <- 'nosuspend'   end_of_word
KEYWORD_noinline    <- 'noinline'    end_of_word
KEYWORD_opaque      <- 'opaque'      end_of_word
KEYWORD_or          <- 'or'          end_of_word
KEYWORD_orelse      <- 'orelse'      end_of_word
KEYWORD_packed      <- 'packed'      end_of_word
KEYWORD_pub         <- 'pub'         end_of_word
KEYWORD_resume      <- 'resume'      end_of_word
KEYWORD_return      <- 'return'      end_of_word
KEYWORD_linksection <- 'linksection' end_of_word
KEYWORD_struct      <- 'struct'      end_of_word
KEYWORD_suspend     <- 'suspend'     end_of_word
KEYWORD_switch      <- 'switch'      end_of_word
KEYWORD_test        <- 'test'        end_of_word
KEYWORD_threadlocal <- 'threadlocal' end_of_word
KEYWORD_try         <- 'try'         end_of_word
KEYWORD_union       <- 'union'       end_of_word
KEYWORD_unreachable <- 'unreachable' end_of_word
KEYWORD_var         <- 'var'         end_of_word
KEYWORD_volatile    <- 'volatile'    end_of_word
KEYWORD_while       <- 'while'       end_of_word

keyword <- KEYWORD_addrspace / KEYWORD_align / KEYWORD_allowzero / KEYWORD_and
         / KEYWORD_anyframe / KEYWORD_anytype / KEYWORD_asm
         / KEYWORD_break / KEYWORD_callconv / KEYWORD_catch
         / KEYWORD_comptime / KEYWORD_const / KEYWORD_continue / KEYWORD_defer
         / KEYWORD_else / KEYWORD_enum / KEYWORD_errdefer / KEYWORD_error / KEYWORD_export
         / KEYWORD_extern / KEYWORD_fn / KEYWORD_for / KEYWORD_if
         / KEYWORD_inline / KEYWORD_noalias / KEYWORD_nosuspend / KEYWORD_noinline
         / KEYWORD_opaque / KEYWORD_or / KEYWORD_orelse / KEYWORD_packed
         / KEYWORD_pub / KEYWORD_resume / KEYWORD_return / KEYWORD_linksection
         / KEYWORD_struct / KEYWORD_suspend / KEYWORD_switch / KEYWORD_test
         / KEYWORD_threadlocal / KEYWORD_try / KEYWORD_union / KEYWORD_unreachable
         / KEYWORD_var / KEYWORD_volatile / KEYWORD_while

```

### Zen

- Communicate intent precisely.
- Edge cases matter.
- Favor reading code over writing code.
- Only one obvious way to do things.
- Runtime crashes are better than bugs.
- Compile errors are better than runtime crashes.
- Incremental improvements.
- Avoid local maximums.
- Reduce the amount one must remember.
- Focus on code rather than style.
- Resource allocation may fail; resource deallocation must succeed.
- Memory is a resource.
- Together we serve the users.
