# Functions and Error Handling

*Function design, error handling patterns, and type conversions*

## Functions

**`test_functions.zig`:**

```zig
const std = @import("std");
const builtin = @import("builtin");
const native_arch = builtin.cpu.arch;
const expectEqual = std.testing.expectEqual;

// Functions are declared like this
fn add(a: i8, b: i8) i8 {
    if (a == 0) {
        return b;
    }

    return a + b;
}

// The export specifier makes a function externally visible in the generated
// object file, and makes it use the C ABI.
export fn sub(a: i8, b: i8) i8 {
    return a - b;
}

// The extern specifier is used to declare a function that will be resolved
// at link time, when linking statically, or at runtime, when linking
// dynamically. The quoted identifier after the extern keyword specifies
// the library that has the function. (e.g. "c" -> libc.so)
// The callconv specifier changes the calling convention of the function.
extern "kernel32" fn ExitProcess(exit_code: u32) callconv(.winapi) noreturn;
extern "c" fn atan2(a: f64, b: f64) f64;

// The @branchHint builtin can be used to tell the optimizer that a function is rarely called ("cold").
fn abort() noreturn {
    @branchHint(.cold);
    while (true) {}
}

// The naked calling convention makes a function not have any function prologue or epilogue.
// This can be useful when integrating with assembly.
fn _start() callconv(.naked) noreturn {
    abort();
}

// The inline calling convention forces a function to be inlined at all call sites.
// If the function cannot be inlined, it is a compile-time error.
inline fn shiftLeftOne(a: u32) u32 {
    return a << 1;
}

// The pub specifier allows the function to be visible when importing.
// Another file can use @import and call sub2
pub fn sub2(a: i8, b: i8) i8 {
    return a - b;
}

// Function pointers are prefixed with `*const `.
const Call2Op = *const fn (a: i8, b: i8) i8;
fn doOp(fnCall: Call2Op, op1: i8, op2: i8) i8 {
    return fnCall(op1, op2);
}

test "function" {
    try expectEqual(11, doOp(add, 5, 6));
    try expectEqual(-1, doOp(sub2, 5, 6));
}

```

**Shell:**

```shell
$ zig test test_functions.zig
1/1 test_functions.test.function...OK
All 1 tests passed.

```

There is a difference between a function *body* and a function *pointer*.
Function bodies are [comptime](34-comptime.md#comptime)-only types while function [Pointers](14-pointers.md#Pointers) may be
runtime-known.

### Pass-by-value Parameters

Primitive types such as [Integers](09-integers.md#Integers) and [Floats](10-floats.md#Floats) passed as parameters
are copied, and then the copy is available in the function body. This is called "passing by value".
Copying a primitive type is essentially free and typically involves nothing more than
setting a register.

Structs, unions, and arrays can sometimes be more efficiently passed as a reference, since a copy
could be arbitrarily expensive depending on the size. When these types are passed
as parameters, Zig may choose to copy and pass by value, or pass by reference, whichever way
Zig decides will be faster. This is made possible, in part, by the fact that parameters are immutable.

**`test_pass_by_reference_or_value.zig`:**

```zig
const Point = struct {
    x: i32,
    y: i32,
};

fn foo(point: Point) i32 {
    // Here, `point` could be a reference, or a copy. The function body
    // can ignore the difference and treat it as a value. Be very careful
    // taking the address of the parameter - it should be treated as if
    // the address will become invalid when the function returns.
    return point.x + point.y;
}

const expectEqual = @import("std").testing.expectEqual;

test "pass struct to function" {
    try expectEqual(3, foo(Point{ .x = 1, .y = 2 }));
}

```

**Shell:**

```shell
$ zig test test_pass_by_reference_or_value.zig
1/1 test_pass_by_reference_or_value.test.pass struct to function...OK
All 1 tests passed.

```

For extern functions, Zig follows the C ABI for passing structs and unions by value.

### Function Parameter Type Inference

Function parameters can be declared with `anytype` in place of the type.
In this case the parameter types will be inferred when the function is called.
Use [@TypeOf](#TypeOf) and [@typeInfo](#typeInfo) to get information about the inferred type.

**`test_fn_type_inference.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;

fn addFortyTwo(x: anytype) @TypeOf(x) {
    return x + 42;
}

test "fn type inference" {
    try expectEqual(43, addFortyTwo(1));
    try expectEqual(comptime_int, @TypeOf(addFortyTwo(1)));
    const y: i64 = 2;
    try expectEqual(44, addFortyTwo(y));
    try expectEqual(i64, @TypeOf(addFortyTwo(y)));
}

```

**Shell:**

```shell
$ zig test test_fn_type_inference.zig
1/1 test_fn_type_inference.test.fn type inference...OK
All 1 tests passed.

```

### inline fn

Adding the `inline` keyword to a function definition makes that
function become *semantically inlined* at the callsite. This is
not a hint to be possibly observed by optimization passes, but has
implications on the types and values involved in the function call.

Unlike normal function calls, arguments at an inline function callsite which are
compile-time known are treated as [Compile Time Parameters](46-c.md#Compile-Time-Parameters). This can potentially
propagate all the way to the return value:

**`inline_call.zig`:**

```zig
const std = @import("std");

pub fn main() void {
    if (foo(1200, 34) != 1234) {
        @compileError("bad");
    }
}

inline fn foo(a: i32, b: i32) i32 {
    std.debug.print("runtime a = {} b = {}", .{ a, b });
    return a + b;
}

```

**Shell:**

```shell
$ zig build-exe inline_call.zig
$ ./inline_call
runtime a = 1200 b = 34

```

If `inline` is removed, the test fails with the compile error
instead of passing.

It is generally better to let the compiler decide when to inline a
function, except for these scenarios:

- To change how many stack frames are in the call stack, for debugging purposes.
- To force comptime-ness of the arguments to propagate to the return value of the function, as in the above example.
- Real world performance measurements demand it.

Note that `inline` actually *restricts*
what the compiler is allowed to do. This can harm binary size,
compilation speed, and even runtime performance.

### Function Reflection

**`test_fn_reflection.zig`:**

```zig
const std = @import("std");
const math = std.math;
const testing = std.testing;

test "fn reflection" {
    try testing.expectEqual(bool, @typeInfo(@TypeOf(testing.expect)).@"fn".params[0].type.?);
    try testing.expectEqual(testing.TmpDir, @typeInfo(@TypeOf(testing.tmpDir)).@"fn".return_type.?);

    try testing.expect(@typeInfo(@TypeOf(math.Log2Int)).@"fn".is_generic);
}

```

**Shell:**

```shell
$ zig test test_fn_reflection.zig
1/1 test_fn_reflection.test.fn reflection...OK
All 1 tests passed.

```

---

## Errors

### Error Set Type

An error set is like an [enum](17-enum.md#enum).
However, each error name across the entire compilation gets assigned an unsigned integer
greater than 0. You are allowed to declare the same error name more than once, and if you do, it
gets assigned the same integer value.

The error set type defaults to a `u16`, though if the maximum number of distinct
error values is provided via the `--error-limit [num]` command line parameter an integer type
with the minimum number of bits required to represent all of the error values will be used.

You can [coerce](#Type-Coercion) an error from a subset to a superset:

**`test_coerce_error_subset_to_superset.zig`:**

```zig
const std = @import("std");

const FileOpenError = error{
    AccessDenied,
    OutOfMemory,
    FileNotFound,
};

const AllocationError = error{
    OutOfMemory,
};

test "coerce subset to superset" {
    const err = foo(AllocationError.OutOfMemory);
    try std.testing.expectEqual(FileOpenError.OutOfMemory, err);
}

fn foo(err: AllocationError) FileOpenError {
    return err;
}

```

**Shell:**

```shell
$ zig test test_coerce_error_subset_to_superset.zig
1/1 test_coerce_error_subset_to_superset.test.coerce subset to superset...OK
All 1 tests passed.

```

But you cannot [coerce](#Type-Coercion) an error from a superset to a subset:

**`test_coerce_error_superset_to_subset.zig`:**

```zig
const FileOpenError = error{
    AccessDenied,
    OutOfMemory,
    FileNotFound,
};

const AllocationError = error{
    OutOfMemory,
};

test "coerce superset to subset" {
    foo(FileOpenError.OutOfMemory) catch {};
}

fn foo(err: FileOpenError) AllocationError {
    return err;
}

```

**Shell:**

```shell
$ zig test test_coerce_error_superset_to_subset.zig
/home/ci/work/zig-bootstrap/zig/doc/langref/test_coerce_error_superset_to_subset.zig:16:12: error: expected type 'error{OutOfMemory}', found 'error{AccessDenied,FileNotFound,OutOfMemory}'
    return err;
           ^~~
/home/ci/work/zig-bootstrap/zig/doc/langref/test_coerce_error_superset_to_subset.zig:16:12: note: 'error.AccessDenied' not a member of destination error set
/home/ci/work/zig-bootstrap/zig/doc/langref/test_coerce_error_superset_to_subset.zig:16:12: note: 'error.FileNotFound' not a member of destination error set
/home/ci/work/zig-bootstrap/zig/doc/langref/test_coerce_error_superset_to_subset.zig:15:28: note: function return type declared here
fn foo(err: FileOpenError) AllocationError {
                           ^~~~~~~~~~~~~~~
referenced by:
    test.coerce superset to subset: /home/ci/work/zig-bootstrap/zig/doc/langref/test_coerce_error_superset_to_subset.zig:12:8


```

There is a shortcut for declaring an error set with only 1 value, and then getting that value:

**`single_value_error_set_shortcut.zig`:**

```zig
const err = error.FileNotFound;

```

This is equivalent to:

**`single_value_error_set.zig`:**

```zig
const err = (error{FileNotFound}).FileNotFound;

```

This becomes useful when using [Inferred Error Sets](#Inferred-Error-Sets).

#### The Global Error Set

`anyerror` refers to the global error set.
This is the error set that contains all errors in the entire compilation unit, i.e. it is the union of all other error sets.

You can [coerce](#Type-Coercion) any error set to the global one, and you can explicitly
cast an error of the global error set to a non-global one. This inserts a language-level
assert to make sure the error value is in fact in the destination error set.

The global error set should generally be avoided because it prevents the
compiler from knowing what errors are possible at compile-time. Knowing
the error set at compile-time is better for generated documentation and
helpful error messages, such as forgetting a possible error value in a [switch](21-switch.md#switch).

### Error Union Type

An error set type and normal type can be combined with the `!`
binary operator to form an error union type. You are likely to use an
error union type more often than an error set type by itself.

Here is a function to parse a string into a 64-bit integer:

**`error_union_parsing_u64.zig`:**

```zig
const std = @import("std");
const maxInt = std.math.maxInt;

pub fn parseU64(buf: []const u8, radix: u8) !u64 {
    var x: u64 = 0;

    for (buf) |c| {
        const digit = charToDigit(c);

        if (digit >= radix) {
            return error.InvalidChar;
        }

        // x *= radix
        var ov = @mulWithOverflow(x, radix);
        if (ov[1] != 0) return error.OverFlow;

        // x += digit
        ov = @addWithOverflow(ov[0], digit);
        if (ov[1] != 0) return error.OverFlow;
        x = ov[0];
    }

    return x;
}

fn charToDigit(c: u8) u8 {
    return switch (c) {
        '0'...'9' => c - '0',
        'A'...'Z' => c - 'A' + 10,
        'a'...'z' => c - 'a' + 10,
        else => maxInt(u8),
    };
}

test "parse u64" {
    const result = try parseU64("1234", 10);
    try std.testing.expectEqual(1234, result);
}

```

**Shell:**

```shell
$ zig test error_union_parsing_u64.zig
1/1 error_union_parsing_u64.test.parse u64...OK
All 1 tests passed.

```

Notice the return type is `!u64`. This means that the function
either returns an unsigned 64 bit integer, or an error. We left off the error set
to the left of the `!`, so the error set is inferred.

Within the function definition, you can see some return statements that return
an error, and at the bottom a return statement that returns a `u64`.
Both types [coerce](#Type-Coercion) to `anyerror!u64`.

What it looks like to use this function varies depending on what you're
trying to do. One of the following:

- You want to provide a default value if it returned an error.
- If it returned an error then you want to return the same error.
- You know with complete certainty it will not return an error, so want to unconditionally unwrap it.
- You want to take a different action for each possible error.

#### catch

If you want to provide a default value, you can use the `catch` binary operator:

**`catch.zig`:**

```zig
const parseU64 = @import("error_union_parsing_u64.zig").parseU64;

fn doAThing(str: []u8) void {
    const number = parseU64(str, 10) catch 13;
    _ = number; // ...
}

```

In this code, `number` will be equal to the successfully parsed string, or
a default value of 13. The type of the right hand side of the binary `catch` operator must
match the unwrapped error union type, or be of type `noreturn`.

If you want to provide a default value with
`catch` after performing some logic, you
can combine `catch` with named [Blocks](20-blocks.md#Blocks):

**`handle_error_with_catch_block.zig`:**

```zig
const parseU64 = @import("error_union_parsing_u64.zig").parseU64;

fn doAThing(str: []u8) void {
    const number = parseU64(str, 10) catch blk: {
        // do things
        break :blk 13;
    };
    _ = number; // number is now initialized
}

```

#### try

Let's say you wanted to return the error if you got one, otherwise continue with the
function logic:

**`catch_err_return.zig`:**

```zig
const parseU64 = @import("error_union_parsing_u64.zig").parseU64;

fn doAThing(str: []u8) !void {
    const number = parseU64(str, 10) catch |err| return err;
    _ = number; // ...
}

```

There is a shortcut for this. The `try` expression:

**`try.zig`:**

```zig
const parseU64 = @import("error_union_parsing_u64.zig").parseU64;

fn doAThing(str: []u8) !void {
    const number = try parseU64(str, 10);
    _ = number; // ...
}

```

`try` evaluates an error union expression. If it is an error, it returns
from the current function with the same error. Otherwise, the expression results in
the unwrapped value.

Maybe you know with complete certainty that an expression will never be an error.
In this case you can do this:

`const number = parseU64("1234", 10) catch unreachable;`

Here we know for sure that "1234" will parse successfully. So we put the
`unreachable` value on the right hand side.
`unreachable` invokes safety-checked [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior), so
in [Debug](#Debug) and [ReleaseSafe](#ReleaseSafe), triggers a safety panic by default. So, while
we're debugging the application, if there *was* a surprise error here, the application
would crash appropriately.

You may want to take a different action for every situation. For that, we combine
the [if](24-if.md#if) and [switch](21-switch.md#switch) expression:

**`handle_all_error_scenarios.zig`:**

```zig
fn doAThing(str: []u8) void {
    if (parseU64(str, 10)) |number| {
        doSomethingWithNumber(number);
    } else |err| switch (err) {
        error.Overflow => {
            // handle overflow...
        },
        // we promise that InvalidChar won't happen (or crash in debug mode if it does)
        error.InvalidChar => unreachable,
    }
}

```

Finally, you may want to handle only some errors. For that, you can capture the unhandled
errors in the `else` case, which now contains a narrower error set:

**`handle_some_error_scenarios.zig`:**

```zig
fn doAnotherThing(str: []u8) error{InvalidChar}!void {
    if (parseU64(str, 10)) |number| {
        doSomethingWithNumber(number);
    } else |err| switch (err) {
        error.Overflow => {
            // handle overflow...
        },
        else => |leftover_err| return leftover_err,
    }
}

```

You must use the variable capture syntax. If you don't need the
variable, you can capture with `_` and avoid the
`switch`.

**`handle_no_error_scenarios.zig`:**

```zig
fn doADifferentThing(str: []u8) void {
    if (parseU64(str, 10)) |number| {
        doSomethingWithNumber(number);
    } else |_| {
        // do as you'd like
    }
}

```

#### errdefer

The other component to error handling is defer statements.
In addition to an unconditional [defer](25-defer.md#defer), Zig has `errdefer`,
which evaluates the deferred expression on block exit path if and only if
the function returned with an error from the block.

Example:

**`errdefer_example.zig`:**

```zig
fn createFoo(param: i32) !Foo {
    const foo = try tryToAllocateFoo();
    // now we have allocated foo. we need to free it if the function fails.
    // but we want to return it if the function succeeds.
    errdefer deallocateFoo(foo);

    const tmp_buf = allocateTmpBuffer() orelse return error.OutOfMemory;
    // tmp_buf is truly a temporary resource, and we for sure want to clean it up
    // before this block leaves scope
    defer deallocateTmpBuffer(tmp_buf);

    if (param > 1337) return error.InvalidParam;

    // here the errdefer will not run since we're returning success from the function.
    // but the defer will run!
    return foo;
}

```

The neat thing about this is that you get robust error handling without
the verbosity and cognitive overhead of trying to make sure every exit path
is covered. The deallocation code is always directly following the allocation code.

The `errdefer` statement can optionally capture the error:

**`test_errdefer_capture.zig`:**

```zig
const std = @import("std");

fn captureError(captured: *?anyerror) !void {
    errdefer |err| {
        captured.* = err;
    }
    return error.GeneralFailure;
}

test "errdefer capture" {
    var captured: ?anyerror = null;

    if (captureError(&captured)) unreachable else |err| {
        try std.testing.expectEqual(error.GeneralFailure, captured.?);
        try std.testing.expectEqual(error.GeneralFailure, err);
    }
}

```

**Shell:**

```shell
$ zig test test_errdefer_capture.zig
1/1 test_errdefer_capture.test.errdefer capture...OK
All 1 tests passed.

```

A couple of other tidbits about error handling:

- These primitives give enough expressiveness that it's completely practical
  to have failing to check for an error be a compile error. If you really want
  to ignore the error, you can add `catch unreachable` and
  get the added benefit of crashing in Debug and ReleaseSafe modes if your assumption was wrong.
- Since Zig understands error types, it can pre-weight branches in favor of
  errors not occurring. Just a small optimization benefit that is not available
  in other languages.

See also:

- [defer](25-defer.md#defer)
- [if](24-if.md#if)
- [switch](21-switch.md#switch)

An error union is created with the `!` binary operator.
You can use compile-time reflection to access the child type of an error union:

**`test_error_union.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;

test "error union" {
    var foo: anyerror!i32 = undefined;

    // Coerce from child type of an error union:
    foo = 1234;

    // Coerce from an error set:
    foo = error.SomeError;

    // Use compile-time reflection to access the payload type of an error union:
    try comptime expectEqual(i32, @typeInfo(@TypeOf(foo)).error_union.payload);

    // Use compile-time reflection to access the error set type of an error union:
    try comptime expectEqual(anyerror, @typeInfo(@TypeOf(foo)).error_union.error_set);
}

```

**Shell:**

```shell
$ zig test test_error_union.zig
1/1 test_error_union.test.error union...OK
All 1 tests passed.

```

#### Merging Error Sets

Use the `||` operator to merge two error sets together. The resulting
error set contains the errors of both error sets. Doc comments from the left-hand
side override doc comments from the right-hand side. In this example, the doc
comments for `C.PathNotFound` is `A doc comment`.

This is especially useful for functions which return different error sets depending
on [comptime](34-comptime.md#comptime) branches. For example, the Zig standard library uses
`LinuxFileOpenError || WindowsFileOpenError` for the error set of opening
files.

**`test_merging_error_sets.zig`:**

```zig
const A = error{
    NotDir,

    /// A doc comment
    PathNotFound,
};
const B = error{
    OutOfMemory,

    /// B doc comment
    PathNotFound,
};

const C = A || B;

fn foo() C!void {
    return error.NotDir;
}

test "merge error sets" {
    if (foo()) {
        @panic("unexpected");
    } else |err| switch (err) {
        error.OutOfMemory => @panic("unexpected"),
        error.PathNotFound => @panic("unexpected"),
        error.NotDir => {},
    }
}

```

**Shell:**

```shell
$ zig test test_merging_error_sets.zig
1/1 test_merging_error_sets.test.merge error sets...OK
All 1 tests passed.

```

#### Inferred Error Sets

Because many functions in Zig return a possible error, Zig supports inferring the error set.
To infer the error set for a function, prepend the `!` operator to the functionâs return type, like `!T`:

**`test_inferred_error_sets.zig`:**

```zig
// With an inferred error set
pub fn add_inferred(comptime T: type, a: T, b: T) !T {
    const ov = @addWithOverflow(a, b);
    if (ov[1] != 0) return error.Overflow;
    return ov[0];
}

// With an explicit error set
pub fn add_explicit(comptime T: type, a: T, b: T) Error!T {
    const ov = @addWithOverflow(a, b);
    if (ov[1] != 0) return error.Overflow;
    return ov[0];
}

const Error = error{
    Overflow,
};

const std = @import("std");

test "inferred error set" {
    if (add_inferred(u8, 255, 1)) |_| unreachable else |err| switch (err) {
        error.Overflow => {}, // ok
    }
}

```

**Shell:**

```shell
$ zig test test_inferred_error_sets.zig
1/1 test_inferred_error_sets.test.inferred error set...OK
All 1 tests passed.

```

When a function has an inferred error set, that function becomes generic and thus it becomes
trickier to do certain things with it, such as obtain a function pointer, or have an error
set that is consistent across different build targets. Additionally, inferred error sets
are incompatible with recursion.

In these situations, it is recommended to use an explicit error set. You can generally start
with an empty error set and let compile errors guide you toward completing the set.

These limitations may be overcome in a future version of Zig.

### Error Return Traces

Error Return Traces show all the points in the code that an error was returned to the calling function. This makes it practical to use [try](#try) everywhere and then still be able to know what happened if an error ends up bubbling all the way out of your application.

**`error_return_trace.zig`:**

```zig
pub fn main() !void {
    try foo(12);
}

fn foo(x: i32) !void {
    if (x >= 5) {
        try bar();
    } else {
        try bang2();
    }
}

fn bar() !void {
    if (baz()) {
        try quux();
    } else |err| switch (err) {
        error.FileNotFound => try hello(),
    }
}

fn baz() !void {
    try bang1();
}

fn quux() !void {
    try bang2();
}

fn hello() !void {
    try bang2();
}

fn bang1() !void {
    return error.FileNotFound;
}

fn bang2() !void {
    return error.PermissionDenied;
}

```

**Shell:**

```shell
$ zig build-exe error_return_trace.zig
$ ./error_return_trace
error: PermissionDenied
/home/ci/work/zig-bootstrap/zig/doc/langref/error_return_trace.zig:34:5: 0x11d9c8c in bang1 (error_return_trace.zig)
    return error.FileNotFound;
    ^
/home/ci/work/zig-bootstrap/zig/doc/langref/error_return_trace.zig:22:5: 0x11d9cec in baz (error_return_trace.zig)
    try bang1();
    ^
/home/ci/work/zig-bootstrap/zig/doc/langref/error_return_trace.zig:38:5: 0x11d9d2c in bang2 (error_return_trace.zig)
    return error.PermissionDenied;
    ^
/home/ci/work/zig-bootstrap/zig/doc/langref/error_return_trace.zig:30:5: 0x11d9e0c in hello (error_return_trace.zig)
    try bang2();
    ^
/home/ci/work/zig-bootstrap/zig/doc/langref/error_return_trace.zig:17:31: 0x11d9f1a in bar (error_return_trace.zig)
        error.FileNotFound => try hello(),
                              ^
/home/ci/work/zig-bootstrap/zig/doc/langref/error_return_trace.zig:7:9: 0x11d9ffa in foo (error_return_trace.zig)
        try bar();
        ^
/home/ci/work/zig-bootstrap/zig/doc/langref/error_return_trace.zig:2:5: 0x11da101 in main (error_return_trace.zig)
    try foo(12);
    ^

```

Look closely at this example. This is no stack trace.

You can see that the final error bubbled up was `PermissionDenied`,
but the original error that started this whole thing was `FileNotFound`. In the `bar` function, the code handles the original error code,
and then returns another one, from the switch statement. Error Return Traces make this clear, whereas a stack trace would look like this:

**`stack_trace.zig`:**

```zig
pub fn main() void {
    foo(12);
}

fn foo(x: i32) void {
    if (x >= 5) {
        bar();
    } else {
        bang2();
    }
}

fn bar() void {
    if (baz()) {
        quux();
    } else {
        hello();
    }
}

fn baz() bool {
    return bang1();
}

fn quux() void {
    bang2();
}

fn hello() void {
    bang2();
}

fn bang1() bool {
    return false;
}

fn bang2() void {
    @panic("PermissionDenied");
}

```

**Shell:**

```shell
$ zig build-exe stack_trace.zig
$ ./stack_trace
thread 3971929 panic: PermissionDenied
/home/ci/work/zig-bootstrap/zig/doc/langref/stack_trace.zig:38:5: 0x11daf6a in bang2 (stack_trace.zig)
    @panic("PermissionDenied");
    ^
/home/ci/work/zig-bootstrap/zig/doc/langref/stack_trace.zig:30:10: 0x11dafec in hello (stack_trace.zig)
    bang2();
         ^
/home/ci/work/zig-bootstrap/zig/doc/langref/stack_trace.zig:17:14: 0x11dafa3 in bar (stack_trace.zig)
        hello();
             ^
/home/ci/work/zig-bootstrap/zig/doc/langref/stack_trace.zig:7:12: 0x11da988 in foo (stack_trace.zig)
        bar();
           ^
/home/ci/work/zig-bootstrap/zig/doc/langref/stack_trace.zig:2:8: 0x11da8f1 in main (stack_trace.zig)
    foo(12);
       ^
/home/ci/work/zig-bootstrap/out/host/lib/zig/std/start.zig:685:59: 0x11da211 in callMain (std.zig)
    if (fn_info.params.len == 0) return wrapMain(root.main());
                                                          ^
/home/ci/work/zig-bootstrap/out/host/lib/zig/std/start.zig:190:5: 0x11d9c71 in _start (std.zig)
    asm volatile (switch (native_arch) {
    ^
(process terminated by signal)

```

Here, the stack trace does not explain how the control
flow in `bar` got to the `hello()` call.
One would have to open a debugger or further instrument the application
in order to find out. The error return trace, on the other hand,
shows exactly how the error bubbled up.

This debugging feature makes it easier to iterate quickly on code that
robustly handles all error conditions. This means that Zig developers
will naturally find themselves writing correct, robust code in order
to increase their development pace.

Error Return Traces are enabled by default in [Debug](#Debug) builds and disabled by default in [ReleaseFast](#ReleaseFast), [ReleaseSafe](#ReleaseSafe) and [ReleaseSmall](#ReleaseSmall) builds.

There are a few ways to activate this error return tracing feature:

- Return an error from main
- An error makes its way to `catch unreachable` and you have not overridden the default panic handler
- Use [errorReturnTrace](#errorReturnTrace) to access the current return trace. You can use `std.debug.dumpStackTrace` to print it. This function returns comptime-known [null](#null) when building without error return tracing support.

#### Implementation Details

To analyze performance cost, there are two cases:

- when no errors are returned
- when returning errors

For the case when no errors are returned, the cost is a single memory write operation, only in the first non-failable function in the call graph that calls a failable function, i.e. when a function returning `void` calls a function returning `error`.
This is to initialize this struct in the stack memory:

**`stack_trace_struct.zig`:**

```zig
pub const StackTrace = struct {
    index: usize,
    instruction_addresses: [N]usize,
};

```

Here, N is the maximum function call depth as determined by call graph analysis. Recursion is ignored and counts for 2.

A pointer to `StackTrace` is passed as a secret parameter to every function that can return an error, but it's always the first parameter, so it can likely sit in a register and stay there.

That's it for the path when no errors occur. It's practically free in terms of performance.

When generating the code for a function that returns an error, just before the `return` statement (only for the `return` statements that return errors), Zig generates a call to this function:

**`zig_return_error_fn.zig`:**

```zig
// marked as "no-inline" in LLVM IR
fn __zig_return_error(stack_trace: *StackTrace) void {
    stack_trace.instruction_addresses[stack_trace.index] = @returnAddress();
    stack_trace.index = (stack_trace.index + 1) % N;
}

```

The cost is 2 math operations plus some memory reads and writes. The memory accessed is constrained and should remain cached for the duration of the error return bubbling.

As for code size cost, 1 function call before a return statement is no big deal. Even so,
I have [a plan](https://github.com/ziglang/zig/issues/690) to make the call to
`__zig_return_error` a tail call, which brings the code size cost down to actually zero. What is a return statement in code without error return tracing can become a jump instruction in code with error return tracing.

---

## Optionals

One area that Zig provides safety without compromising efficiency or
readability is with the optional type.

The question mark symbolizes the optional type. You can convert a type to an optional
type by putting a question mark in front of it, like this:

**`optional_integer.zig`:**

```zig
// normal integer
const normal_int: i32 = 1234;

// optional integer
const optional_int: ?i32 = 5678;

```

Now the variable `optional_int` could be an `i32`, or `null`.

Instead of integers, let's talk about pointers. Null references are the source of many runtime
exceptions, and even stand accused of being
[the worst mistake of computer science](https://www.lucidchart.com/techblog/2015/08/31/the-worst-mistake-of-computer-science/).

Zig does not have them.

Instead, you can use an optional pointer. This secretly compiles down to a normal pointer,
since we know we can use 0 as the null value for the optional type. But the compiler
can check your work and make sure you don't assign null to something that can't be null.

Typically the downside of not having null is that it makes the code more verbose to
write. But, let's compare some equivalent C code and Zig code.

Task: call malloc, if the result is null, return null.

C code

**call_malloc_in_c.c:**

```c
// malloc prototype included for reference
void *malloc(size_t size);

struct Foo *do_a_thing(void) {
    char *ptr = malloc(1234);
    if (!ptr) return NULL;
    // ...
}

```

Zig code

**`call_malloc_from_zig.zig`:**

```zig
// malloc prototype included for reference
extern fn malloc(size: usize) ?[*]u8;

fn doAThing() ?*Foo {
    const ptr = malloc(1234) orelse return null;
    _ = ptr; // ...
}

```

Here, Zig is at least as convenient, if not more, than C. And, the type of "ptr"
is `[*]u8` *not* `?[*]u8`. The `orelse` keyword
unwrapped the optional type and therefore `ptr` is guaranteed to be non-null everywhere
it is used in the function.

The other form of checking against NULL you might see looks like this:

**checking_null_in_c.c:**

```c
void do_a_thing(struct Foo *foo) {
    // do some stuff

    if (foo) {
        do_something_with_foo(foo);
    }

    // do some stuff
}

```

In Zig you can accomplish the same thing:

**`checking_null_in_zig.zig`:**

```zig
const Foo = struct {};
fn doSomethingWithFoo(foo: *Foo) void {
    _ = foo;
}

fn doAThing(optional_foo: ?*Foo) void {
    // do some stuff

    if (optional_foo) |foo| {
        doSomethingWithFoo(foo);
    }

    // do some stuff
}

```

Once again, the notable thing here is that inside the if block,
`foo` is no longer an optional pointer, it is a pointer, which
cannot be null.

One benefit to this is that functions which take pointers as arguments can
be annotated with the "nonnull" attribute - `__attribute__((nonnull))` in
[GCC](https://gcc.gnu.org/onlinedocs/gcc-4.0.0/gcc/Function-Attributes.html).
The optimizer can sometimes make better decisions knowing that pointer arguments
cannot be null.

### Optional Type

An optional is created by putting `?` in front of a type. You can use compile-time
reflection to access the child type of an optional:

**`test_optional_type.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;

test "optional type" {
    // Declare an optional and coerce from null:
    var foo: ?i32 = null;

    // Coerce from child type of an optional
    foo = 1234;

    // Use compile-time reflection to access the child type of the optional:
    try comptime expectEqual(i32, @typeInfo(@TypeOf(foo)).optional.child);
}

```

**Shell:**

```shell
$ zig test test_optional_type.zig
1/1 test_optional_type.test.optional type...OK
All 1 tests passed.

```

### null

Just like [undefined](#undefined), `null` has its own type, and the only way to use it is to
cast it to a different type:

**`null.zig`:**

```zig
const optional_value: ?i32 = null;

```

### Optional Pointers

An optional pointer is guaranteed to be the same size as a pointer. The `null` of
the optional is guaranteed to be address 0.

**`test_optional_pointer.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;

test "optional pointers" {
    // Pointers cannot be null. If you want a null pointer, use the optional
    // prefix `?` to make the pointer type optional.
    var ptr: ?*i32 = null;

    var x: i32 = 1;
    ptr = &x;

    try expectEqual(1, ptr.?.*);

    // Optional pointers are the same size as normal pointers, because pointer
    // value 0 is used as the null value.
    try expectEqual(@sizeOf(?*i32), @sizeOf(*i32));
}

```

**Shell:**

```shell
$ zig test test_optional_pointer.zig
1/1 test_optional_pointer.test.optional pointers...OK
All 1 tests passed.

```

See also:

- [while with Optionals](22-while.md#while-with-Optionals)
- [if with Optionals](24-if.md#if-with-Optionals)

---

## Casting

A **type cast** converts a value of one type to another.
Zig has [Type Coercion](#Type-Coercion) for conversions that are known to be completely safe and unambiguous,
and [Explicit Casts](#Explicit-Casts) for conversions that one would not want to happen on accident.
There is also a third kind of type conversion called [Peer Type Resolution](#Peer-Type-Resolution) for
the case when a result type must be decided given multiple operand types.

### Type Coercion

Type coercion occurs when one type is expected, but different type is provided:

**`test_type_coercion.zig`:**

```zig
test "type coercion - variable declaration" {
    const a: u8 = 1;
    const b: u16 = a;
    _ = b;
}

test "type coercion - function call" {
    const a: u8 = 1;
    foo(a);
}

fn foo(b: u16) void {
    _ = b;
}

test "type coercion - @as builtin" {
    const a: u8 = 1;
    const b = @as(u16, a);
    _ = b;
}

```

**Shell:**

```shell
$ zig test test_type_coercion.zig
1/3 test_type_coercion.test.type coercion - variable declaration...OK
2/3 test_type_coercion.test.type coercion - function call...OK
3/3 test_type_coercion.test.type coercion - @as builtin...OK
All 3 tests passed.

```

Type coercions are only allowed when it is completely unambiguous how to get from one type to another,
and the transformation is guaranteed to be safe. There is one exception, which is [C Pointers](46-c.md#C-Pointers).

#### Type Coercion: Stricter Qualification

Values which have the same representation at runtime can be cast to increase the strictness
of the qualifiers, no matter how nested the qualifiers are:

- `const` - non-const to const is allowed
- `volatile` - non-volatile to volatile is allowed
- `align` - bigger to smaller alignment is allowed
- [error sets](#Error-Set-Type) to supersets is allowed

These casts are no-ops at runtime since the value representation does not change.

**`test_no_op_casts.zig`:**

```zig
test "type coercion - const qualification" {
    var a: i32 = 1;
    const b: *i32 = &a;
    foo(b);
}

fn foo(_: *const i32) void {}

```

**Shell:**

```shell
$ zig test test_no_op_casts.zig
1/1 test_no_op_casts.test.type coercion - const qualification...OK
All 1 tests passed.

```

In addition, pointers coerce to const optional pointers:

**`test_pointer_coerce_const_optional.zig`:**

```zig
const std = @import("std");
const expectEqualStrings = std.testing.expectEqualStrings;
const mem = std.mem;

test "cast *[1][*:0]const u8 to []const ?[*:0]const u8" {
    const window_name = [1][*:0]const u8{"window name"};
    const x: []const ?[*:0]const u8 = &window_name;
    try expectEqualStrings("window name", mem.span(x[0].?));
}

```

**Shell:**

```shell
$ zig test test_pointer_coerce_const_optional.zig
1/1 test_pointer_coerce_const_optional.test.cast *[1][*:0]const u8 to []const ?[*:0]const u8...OK
All 1 tests passed.

```

#### Type Coercion: Integer and Float Widening

[Integers](09-integers.md#Integers) coerce to integer types which can represent every value of the old type, and likewise
[Floats](10-floats.md#Floats) coerce to float types which can represent every value of the old type.

**`test_integer_widening.zig`:**

```zig
const std = @import("std");
const builtin = @import("builtin");
const expectEqual = std.testing.expectEqual;
const mem = std.mem;

test "integer widening" {
    const a: u8 = 250;
    const b: u16 = a;
    const c: u32 = b;
    const d: u64 = c;
    const e: u64 = d;
    const f: u128 = e;
    try expectEqual(f, a);
}

test "implicit unsigned integer to signed integer" {
    const a: u8 = 250;
    const b: i16 = a;
    try expectEqual(250, b);
}

test "float widening" {
    const a: f16 = 12.34;
    const b: f32 = a;
    const c: f64 = b;
    const d: f128 = c;
    try expectEqual(d, a);
}

```

**Shell:**

```shell
$ zig test test_integer_widening.zig
1/3 test_integer_widening.test.integer widening...OK
2/3 test_integer_widening.test.implicit unsigned integer to signed integer...OK
3/3 test_integer_widening.test.float widening...OK
All 3 tests passed.

```

#### Type Coercion: Int to Float

[Integers](09-integers.md#Integers) coerce to [Floats](10-floats.md#Floats) if every possible integer value can be stored in the float
without rounding (i.e. the integer's precision does not exceed the float's significand precision).
Larger integer types that cannot be safely coerced must be explicitly casted with [@floatFromInt](#floatFromInt).

| Float Type | Largest Integer Types |
| --- | --- |
| `f16` | `i12` and `u11` |
| `f32` | `i25` and `u24` |
| `f64` | `i54` and `u53` |
| `f80` | `i65` and `u64` |
| `f128` | `i114` and `u113` |
| `c_longdouble` | Varies by target |

**`test_int_to_float_coercion.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "implicit integer to float" {
    var int: u8 = 123;
    _ = ∫
    const float: f32 = int;
    const int_from_float: u8 = @intFromFloat(float);
    try expectEqual(int, int_from_float);
}

```

**Shell:**

```shell
$ zig test test_int_to_float_coercion.zig
1/1 test_int_to_float_coercion.test.implicit integer to float...OK
All 1 tests passed.

```

**`test_failed_int_to_float_coercion.zig`:**

```zig
test "integer type is too large for implicit cast to float" {
    var int: u25 = 123;
    _ = ∫
    const float: f32 = int;
    _ = float;
}

```

**Shell:**

```shell
$ zig test test_failed_int_to_float_coercion.zig
/home/ci/work/zig-bootstrap/zig/doc/langref/test_failed_int_to_float_coercion.zig:4:24: error: expected type 'f32', found 'u25'
    const float: f32 = int;
                       ^~~


```

#### Type Coercion: Float to Int

A compiler error is appropriate because this ambiguous expression leaves the compiler
two choices about the coercion.

- Cast `54.0` to `comptime_int` resulting in `@as(comptime_int, 10)`, which is casted to `@as(f32, 10)`
- Cast `5` to `comptime_float` resulting in `@as(comptime_float, 10.8)`, which is casted to `@as(f32, 10.8)`

**`test_ambiguous_coercion.zig`:**

```zig
// Compile time coercion of float to int
test "implicit cast to comptime_int" {
    const f: f32 = 54.0 / 5;
    _ = f;
}

```

**Shell:**

```shell
$ zig test test_ambiguous_coercion.zig
/home/ci/work/zig-bootstrap/zig/doc/langref/test_ambiguous_coercion.zig:3:25: error: ambiguous coercion of division operands 'comptime_float' and 'comptime_int'; non-zero remainder '4'
    const f: f32 = 54.0 / 5;
                   ~~~~~^~~


```

#### Type Coercion: Slices, Arrays and Pointers

**`test_coerce_slices_arrays_and_pointers.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;
const expectEqualStrings = std.testing.expectEqualStrings;
const expectEqualSlices = std.testing.expectEqualSlices;

// You can assign constant pointers to arrays to a slice with
// const modifier on the element type. Useful in particular for
// String literals.
test "*const [N]T to []const T" {
    const x1: []const u8 = "hello";
    const x2: []const u8 = &[5]u8{ 'h', 'e', 'l', 'l', 111 };
    try expectEqualStrings(x1, x2);

    const y: []const f32 = &[2]f32{ 1.2, 3.4 };
    try expectEqual(1.2, y[0]);
}

// Likewise, it works when the destination type is an error union.
test "*const [N]T to E![]const T" {
    const x1: anyerror![]const u8 = "hello";
    const x2: anyerror![]const u8 = &[5]u8{ 'h', 'e', 'l', 'l', 111 };
    try expectEqualStrings(try x1, try x2);

    const y: anyerror![]const f32 = &[2]f32{ 1.2, 3.4 };
    try expectEqual(1.2, (try y)[0]);
}

// Likewise, it works when the destination type is an optional.
test "*const [N]T to ?[]const T" {
    const x1: ?[]const u8 = "hello";
    const x2: ?[]const u8 = &[5]u8{ 'h', 'e', 'l', 'l', 111 };
    try expectEqualStrings(x1.?, x2.?);

    const y: ?[]const f32 = &[2]f32{ 1.2, 3.4 };
    try expectEqual(1.2, y.?[0]);
}

// In this cast, the array length becomes the slice length.
test "*[N]T to []T" {
    var buf: [5]u8 = "hello".*;
    const x: []u8 = &buf;
    try expectEqualStrings("hello", x);

    const buf2 = [2]f32{ 1.2, 3.4 };
    const x2: []const f32 = &buf2;
    try expectEqualSlices(f32, &[2]f32{ 1.2, 3.4 }, x2);
}

// Single-item pointers to arrays can be coerced to many-item pointers.
test "*[N]T to [*]T" {
    var buf: [5]u8 = "hello".*;
    const x: [*]u8 = &buf;
    try expectEqual('o', x[4]);
    // x[5] would be an uncaught out of bounds pointer dereference!
}

// Likewise, it works when the destination type is an optional.
test "*[N]T to ?[*]T" {
    var buf: [5]u8 = "hello".*;
    const x: ?[*]u8 = &buf;
    try expectEqual('o', x.?[4]);
}

// Single-item pointers can be cast to len-1 single-item arrays.
test "*T to *[1]T" {
    var x: i32 = 1234;
    const y: *[1]i32 = &x;
    const z: [*]i32 = y;
    try expectEqual(1234, z[0]);
}

// Sentinel-terminated slices can be coerced into sentinel-terminated pointers
test "[:x]T to [*:x]T" {
    const buf: [:0]const u8 = "hello";
    const buf2: [*:0]const u8 = buf;
    try expectEqual('o', buf2[4]);
}

```

**Shell:**

```shell
$ zig test test_coerce_slices_arrays_and_pointers.zig
1/8 test_coerce_slices_arrays_and_pointers.test.*const [N]T to []const T...OK
2/8 test_coerce_slices_arrays_and_pointers.test.*const [N]T to E![]const T...OK
3/8 test_coerce_slices_arrays_and_pointers.test.*const [N]T to ?[]const T...OK
4/8 test_coerce_slices_arrays_and_pointers.test.*[N]T to []T...OK
5/8 test_coerce_slices_arrays_and_pointers.test.*[N]T to [*]T...OK
6/8 test_coerce_slices_arrays_and_pointers.test.*[N]T to ?[*]T...OK
7/8 test_coerce_slices_arrays_and_pointers.test.*T to *[1]T...OK
8/8 test_coerce_slices_arrays_and_pointers.test.[:x]T to [*:x]T...OK
All 8 tests passed.

```

See also:

- [C Pointers](46-c.md#C-Pointers)

#### Type Coercion: Optionals

The payload type of [Optionals](30-optionals.md#Optionals), as well as [null](#null), coerce to the optional type.

**`test_coerce_optionals.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "coerce to optionals" {
    const x: ?i32 = 1234;
    const y: ?i32 = null;

    try expectEqual(1234, x.?);
    try expectEqual(null, y);
}

```

**Shell:**

```shell
$ zig test test_coerce_optionals.zig
1/1 test_coerce_optionals.test.coerce to optionals...OK
All 1 tests passed.

```

Optionals work nested inside the [Error Union Type](#Error-Union-Type), too:

**`test_coerce_optional_wrapped_error_union.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "coerce to optionals wrapped in error union" {
    const x: anyerror!?i32 = 1234;
    const y: anyerror!?i32 = null;

    try expectEqual(1234, (try x).?);
    try expectEqual(null, (try y));
}

```

**Shell:**

```shell
$ zig test test_coerce_optional_wrapped_error_union.zig
1/1 test_coerce_optional_wrapped_error_union.test.coerce to optionals wrapped in error union...OK
All 1 tests passed.

```

#### Type Coercion: Error Unions

The payload type of an [Error Union Type](#Error-Union-Type) as well as the [Error Set Type](#Error-Set-Type)
coerce to the error union type:

**`test_coerce_to_error_union.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "coercion to error unions" {
    const x: anyerror!i32 = 1234;
    const y: anyerror!i32 = error.Failure;

    try expectEqual(1234, (try x));
    try std.testing.expectError(error.Failure, y);
}

```

**Shell:**

```shell
$ zig test test_coerce_to_error_union.zig
1/1 test_coerce_to_error_union.test.coercion to error unions...OK
All 1 tests passed.

```

#### Type Coercion: Compile-Time Known Numbers

When a number is [comptime](34-comptime.md#comptime)-known to be representable in the destination type,
it may be coerced:

**`test_coerce_large_to_small.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "coercing large integer type to smaller one when value is comptime-known to fit" {
    const x: u64 = 255;
    const y: u8 = x;
    try expectEqual(255, y);
}

```

**Shell:**

```shell
$ zig test test_coerce_large_to_small.zig
1/1 test_coerce_large_to_small.test.coercing large integer type to smaller one when value is comptime-known to fit...OK
All 1 tests passed.

```

#### Type Coercion: Unions and Enums

Tagged unions can be coerced to enums, and enums can be coerced to tagged unions
when they are [comptime](34-comptime.md#comptime)-known to be a field of the union that has only one possible value, such as
[void](#void):

**`test_coerce_unions_enums.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const E = enum {
    one,
    two,
    three,
};

const U = union(E) {
    one: i32,
    two: f32,
    three,
};

const U2 = union(enum) {
    a: void,
    b: f32,

    fn tag(self: U2) usize {
        switch (self) {
            .a => return 1,
            .b => return 2,
        }
    }
};

test "coercion between unions and enums" {
    const u = U{ .two = 12.34 };
    const e: E = u; // coerce union to enum
    try expectEqual(E.two, e);

    const three = E.three;
    const u_2: U = three; // coerce enum to union
    try expectEqual(E.three, u_2);

    const u_3: U = .three; // coerce enum literal to union
    try expectEqual(E.three, u_3);

    const u_4: U2 = .a; // coerce enum literal to union with inferred enum tag type.
    try expectEqual(1, u_4.tag());

    // The following example is invalid.
    // error: coercion from enum '@EnumLiteral()' to union 'test_coerce_unions_enum.U2' must initialize 'f32' field 'b'
    //var u_5: U2 = .b;
    //try expectEqual(2, u_5.tag());
}

```

**Shell:**

```shell
$ zig test test_coerce_unions_enums.zig
1/1 test_coerce_unions_enums.test.coercion between unions and enums...OK
All 1 tests passed.

```

See also:

- [union](18-union.md#union)
- [enum](17-enum.md#enum)

#### Type Coercion: undefined

[undefined](#undefined) can be coerced to any type.

#### Type Coercion: Tuples to Arrays

[Tuples](#Tuples) can be coerced to arrays, if all of the fields have the same type.

**`test_coerce_tuples_arrays.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const Tuple = struct { u8, u8 };
test "coercion from homogeneous tuple to array" {
    const tuple: Tuple = .{ 5, 6 };
    const array: [2]u8 = tuple;
    _ = array;
}

```

**Shell:**

```shell
$ zig test test_coerce_tuples_arrays.zig
1/1 test_coerce_tuples_arrays.test.coercion from homogeneous tuple to array...OK
All 1 tests passed.

```

### Explicit Casts

Explicit casts are performed via [Builtin Functions](38-builtin-functions.md#Builtin-Functions).
Some explicit casts are safe; some are not.
Some explicit casts perform language-level assertions; some do not.
Some explicit casts are no-ops at runtime; some are not.

- [@bitCast](#bitCast) - change type but maintain bit representation
- [@alignCast](#alignCast) - make a pointer have more alignment
- [@enumFromInt](17-enum.md#enumFromInt) - obtain an enum value based on its integer tag value
- [@errorFromInt](#errorFromInt) - obtain an error code based on its integer value
- [@errorCast](#errorCast) - convert to a smaller error set
- [@floatCast](#floatCast) - convert a larger float to a smaller float
- [@floatFromInt](#floatFromInt) - convert an integer to a float value
- [@intCast](#intCast) - convert between integer types
- [@intFromBool](#intFromBool) - convert true to 1 and false to 0
- [@intFromEnum](#intFromEnum) - obtain the integer tag value of an enum or tagged union
- [@intFromError](#intFromError) - obtain the integer value of an error code
- [@intFromFloat](#intFromFloat) - obtain the integer part of a float value
- [@intFromPtr](#intFromPtr) - obtain the address of a pointer
- [@ptrFromInt](#ptrFromInt) - convert an address to a pointer
- [@ptrCast](#ptrCast) - convert between pointer types
- [@truncate](#truncate) - convert between integer types, chopping off bits

### Peer Type Resolution

Peer Type Resolution occurs in these places:

- [switch](21-switch.md#switch) expressions
- [if](24-if.md#if) expressions
- [while](22-while.md#while) expressions
- [for](23-for.md#for) expressions
- Multiple break statements in a block
- Some [binary operations](#Table-of-Operators)

This kind of type resolution chooses a type that all peer types can coerce into. Here are
some examples:

**`test_peer_type_resolution.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;
const expectEqualStrings = std.testing.expectEqualStrings;

test "peer resolve int widening" {
    const a: i8 = 12;
    const b: i16 = 34;
    const c = a + b;
    try expectEqual(46, c);
    try expectEqual(i16, @TypeOf(c));
}

test "peer resolve small int and float" {
    // This only works for integer types that can coerce to the float type.
    // Larger integer types will cause a compiler error; no float widening occurs.
    var i: u8 = 12;
    var f: f32 = 34;
    _ = .{ &i, &f };
    const x = i + f;
    try expectEqual(x, 46.0);
    try expectEqual(@TypeOf(x), f32);
}

test "peer resolve arrays of different size to const slice" {
    try expectEqualStrings("true", boolToStr(true));
    try expectEqualStrings("false", boolToStr(false));
    try comptime expectEqualStrings("true", boolToStr(true));
    try comptime expectEqualStrings("false", boolToStr(false));
}
fn boolToStr(b: bool) []const u8 {
    return if (b) "true" else "false";
}

test "peer resolve array and const slice" {
    try testPeerResolveArrayConstSlice(true);
    try comptime testPeerResolveArrayConstSlice(true);
}
fn testPeerResolveArrayConstSlice(b: bool) !void {
    const value1 = if (b) "aoeu" else @as([]const u8, "zz");
    const value2 = if (b) @as([]const u8, "zz") else "aoeu";
    try expectEqualStrings("aoeu", value1);
    try expectEqualStrings("zz", value2);
}

test "peer type resolution: ?T and T" {
    try expectEqual(0, peerTypeTAndOptionalT(true, false).?);
    try expectEqual(3, peerTypeTAndOptionalT(false, false).?);
    comptime {
        try expectEqual(0, peerTypeTAndOptionalT(true, false).?);
        try expectEqual(3, peerTypeTAndOptionalT(false, false).?);
    }
}
fn peerTypeTAndOptionalT(c: bool, b: bool) ?usize {
    if (c) {
        return if (b) null else @as(usize, 0);
    }

    return @as(usize, 3);
}

test "peer type resolution: *[0]u8 and []const u8" {
    try expectEqual(0, peerTypeEmptyArrayAndSlice(true, "hi").len);
    try expectEqual(1, peerTypeEmptyArrayAndSlice(false, "hi").len);
    comptime {
        try expectEqual(0, peerTypeEmptyArrayAndSlice(true, "hi").len);
        try expectEqual(1, peerTypeEmptyArrayAndSlice(false, "hi").len);
    }
}
fn peerTypeEmptyArrayAndSlice(a: bool, slice: []const u8) []const u8 {
    if (a) {
        return &[_]u8{};
    }

    return slice[0..1];
}
test "peer type resolution: *[0]u8, []const u8, and anyerror![]u8" {
    {
        var data = "hi".*;
        const slice = data[0..];
        try expectEqual(0, (try peerTypeEmptyArrayAndSliceAndError(true, slice)).len);
        try expectEqual(1, (try peerTypeEmptyArrayAndSliceAndError(false, slice)).len);
    }
    comptime {
        var data = "hi".*;
        const slice = data[0..];
        try expectEqual(0, (try peerTypeEmptyArrayAndSliceAndError(true, slice)).len);
        try expectEqual(1, (try peerTypeEmptyArrayAndSliceAndError(false, slice)).len);
    }
}
fn peerTypeEmptyArrayAndSliceAndError(a: bool, slice: []u8) anyerror![]u8 {
    if (a) {
        return &[_]u8{};
    }

    return slice[0..1];
}

test "peer type resolution: *const T and ?*T" {
    const a: *const usize = @ptrFromInt(0x123456780);
    const b: ?*usize = @ptrFromInt(0x123456780);
    try expectEqual(a, b);
    try expectEqual(b, a);
}

test "peer type resolution: error union switch" {
    // The non-error and error cases are only peers if the error case is just a switch expression;
    // the pattern `if (x) {...} else |err| blk: { switch (err) {...} }` does not consider the
    // non-error and error case to be peers.
    var a: error{ A, B, C }!u32 = 0;
    _ = &a;
    const b = if (a) |x|
        x + 3
    else |err| switch (err) {
        error.A => 0,
        error.B => 1,
        error.C => null,
    };
    try expectEqual(?u32, @TypeOf(b));

    // The non-error and error cases are only peers if the error case is just a switch expression;
    // the pattern `x catch |err| blk: { switch (err) {...} }` does not consider the unwrapped `x`
    // and error case to be peers.
    const c = a catch |err| switch (err) {
        error.A => 0,
        error.B => 1,
        error.C => null,
    };
    try expectEqual(?u32, @TypeOf(c));
}

```

**Shell:**

```shell
$ zig test test_peer_type_resolution.zig
1/9 test_peer_type_resolution.test.peer resolve int widening...OK
2/9 test_peer_type_resolution.test.peer resolve small int and float...OK
3/9 test_peer_type_resolution.test.peer resolve arrays of different size to const slice...OK
4/9 test_peer_type_resolution.test.peer resolve array and const slice...OK
5/9 test_peer_type_resolution.test.peer type resolution: ?T and T...OK
6/9 test_peer_type_resolution.test.peer type resolution: *[0]u8 and []const u8...OK
7/9 test_peer_type_resolution.test.peer type resolution: *[0]u8, []const u8, and anyerror![]u8...OK
8/9 test_peer_type_resolution.test.peer type resolution: *const T and ?*T...OK
9/9 test_peer_type_resolution.test.peer type resolution: error union switch...OK
All 9 tests passed.

```

---

## Zero Bit Types

For some types, [@sizeOf](#sizeOf) is 0:

- [void](#void)
- The [Integers](09-integers.md#Integers) `u0` and `i0`.
- [Arrays](12-arrays.md#Arrays) and [Vectors](13-vectors.md#Vectors) with len 0, or with an element type that is a zero bit type.
- An [enum](17-enum.md#enum) with only 1 tag.
- A [struct](16-struct.md#struct) with all fields being zero bit types.
- A [union](18-union.md#union) with only 1 field which is a zero bit type.

These types can only ever have one possible value, and thus
require 0 bits to represent. Code that makes use of these types is
not included in the final generated code:

**`zero_bit_types.zig`:**

```zig
export fn entry() void {
    var x: void = {};
    var y: void = {};
    x = y;
    y = x;
}

```

When this turns into machine code, there is no code generated in the
body of `entry`, even in [Debug](#Debug) mode. For example, on x86_64:

```

0000000000000010 <entry>:
  10:	55                   	push   %rbp
  11:	48 89 e5             	mov    %rsp,%rbp
  14:	5d                   	pop    %rbp
  15:	c3                   	retq   

```

These assembly instructions do not have any code associated with the void values -
they only perform the function call prologue and epilogue.

### void

`void` can be useful for instantiating generic types. For example, given a
`Map(Key, Value)`, one can pass `void` for the `Value`
type to make it into a `Set`:

**`test_void_in_hashmap.zig`:**

```zig
const std = @import("std");
const expect = std.testing.expect;

test "turn HashMap into a set with void" {
    var map = std.AutoHashMap(i32, void).init(std.testing.allocator);
    defer map.deinit();

    try map.put(1, {});
    try map.put(2, {});

    try expect(map.contains(2));
    try expect(!map.contains(3));

    _ = map.remove(2);
    try expect(!map.contains(2));
}

```

**Shell:**

```shell
$ zig test test_void_in_hashmap.zig
1/1 test_void_in_hashmap.test.turn HashMap into a set with void...OK
All 1 tests passed.

```

Note that this is different from using a dummy value for the hash map value.
By using `void` as the type of the value, the hash map entry type has no value field, and
thus the hash map takes up less space. Further, all the code that deals with storing and loading the
value is deleted, as seen above.

`void` is distinct from `anyopaque`.
`void` has a known size of 0 bytes, and `anyopaque` has an unknown, but non-zero, size.

Expressions of type `void` are the only ones whose value can be ignored. For example, ignoring
a non-`void` expression is a compile error:

**`test_expression_ignored.zig`:**

```zig
test "ignoring expression value" {
    foo();
}

fn foo() i32 {
    return 1234;
}

```

**Shell:**

```shell
$ zig test test_expression_ignored.zig
/home/ci/work/zig-bootstrap/zig/doc/langref/test_expression_ignored.zig:2:8: error: value of type 'i32' ignored
    foo();
    ~~~^~
/home/ci/work/zig-bootstrap/zig/doc/langref/test_expression_ignored.zig:2:8: note: all non-void values must be used
/home/ci/work/zig-bootstrap/zig/doc/langref/test_expression_ignored.zig:2:8: note: to discard the value, assign it to '_'


```

However, if the expression has type `void`, there will be no error. Expression results can be explicitly ignored by assigning them to `_`.

**`test_void_ignored.zig`:**

```zig
test "void is ignored" {
    returnsVoid();
}

test "explicitly ignoring expression value" {
    _ = foo();
}

fn returnsVoid() void {}

fn foo() i32 {
    return 1234;
}

```

**Shell:**

```shell
$ zig test test_void_ignored.zig
1/2 test_void_ignored.test.void is ignored...OK
2/2 test_void_ignored.test.explicitly ignoring expression value...OK
All 2 tests passed.

```

---

## Result Location Semantics

During compilation, every Zig expression and sub-expression is assigned optional result location
information. This information dictates what type the expression should have (its result type), and
where the resulting value should be placed in memory (its result location). The information is
optional in the sense that not every expression has this information: assignment to
`_`, for instance, does not provide any information about the type of an
expression, nor does it provide a concrete memory location to place it in.

As a motivating example, consider the statement `const x: u32 = 42;`. The type
annotation here provides a result type of `u32` to the initialization expression
`42`, instructing the compiler to coerce this integer (initially of type
`comptime_int`) to this type. We will see more examples shortly.

This is not an implementation detail: the logic outlined above is codified into the Zig language
specification, and is the primary mechanism of type inference in the language. This system is
collectively referred to as "Result Location Semantics".

### Result Types

Result types are propagated recursively through expressions where possible. For instance, if the
expression `&e` has result type `*u32`, then
`e` is given a result type of `u32`, allowing the
language to perform this coercion before taking a reference.

The result type mechanism is utilized by casting builtins such as `@intCast`.
Rather than taking as an argument the type to cast to, these builtins use their result type to
determine this information. The result type is often known from context; where it is not, the
`@as` builtin can be used to explicitly provide a result type.

We can break down the result types for each component of a simple expression as follows:

**`result_type_propagation.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;
test "result type propagates through struct initializer" {
    const S = struct { x: u32 };
    const val: u64 = 123;
    const s: S = .{ .x = @intCast(val) };
    // .{ .x = @intCast(val) }   has result type `S` due to the type annotation
    //         @intCast(val)     has result type `u32` due to the type of the field `S.x`
    //                  val      has no result type, as it is permitted to be any integer type
    try expectEqual(@as(u32, 123), s.x);
}

```

**Shell:**

```shell
$ zig test result_type_propagation.zig
1/1 result_type_propagation.test.result type propagates through struct initializer...OK
All 1 tests passed.

```

This result type information is useful for the aforementioned cast builtins, as well as to avoid
the construction of pre-coercion values, and to avoid the need for explicit type coercions in some
cases. The following table details how some common expressions propagate result types, where
`x` and `y` are arbitrary sub-expressions.

| Expression | Parent Result Type | Sub-expression Result Type |
| --- | --- | --- |
| `const val: T = x` | - | `x` is a `T` |
| `var val: T = x` | - | `x` is a `T` |
| `val = x` | - | `x` is a `@TypeOf(val)` |
| `@as(T, x)` | - | `x` is a `T` |
| `&x` | `*T` | `x` is a `T` |
| `&x` | `[]T` | `x` is some array of `T` |
| `f(x)` | - | `x` has the type of the first parameter of `f` |
| `.{x}` | `T` | `x` is a `@FieldType(T, "0")` |
| `.{ .a = x }` | `T` | `x` is a `@FieldType(T, "a")` |
| `T{x}` | - | `x` is a `@FieldType(T, "0")` |
| `T{ .a = x }` | - | `x` is a `@FieldType(T, "a")` |
| `@Int(x, y)` | - | `x` is a `std.builtin.Signedness`, `y` is a `u16` |
| `@typeInfo(x)` | - | `x` is a `type` |
| `x << y` | - | `y` is a `std.math.Log2IntCeil(@TypeOf(x))` |

### Result Locations

In addition to result type information, every expression may be optionally assigned a result
location: a pointer to which the value must be directly written. This system can be used to prevent
intermediate copies when initializing data structures, which can be important for types which must
have a fixed memory address ("pinned" types).

When compiling the simple assignment expression `x = e`, many languages would
create the temporary value `e` on the stack, and then assign it to
`x`, potentially performing a type coercion in the process. Zig approaches this
differently. The expression `e` is given a result type matching the type of
`x`, and a result location of `&x`. For many syntactic
forms of `e`, this has no practical impact. However, it can have important
semantic effects when working with more complex syntax forms.

For instance, if the expression `.{ .a = x, .b = y }` has a result location of
`ptr`, then `x` is given a result location of
`&ptr.a`, and `y` a result location of `&ptr.b`.
Without this system, this expression would construct a temporary struct value entirely on the stack, and
only then copy it to the destination address. In essence, Zig desugars the assignment
`foo = .{ .a = x, .b = y }` to the two statements `foo.a = x; foo.b = y;`.

This can sometimes be important when assigning an aggregate value where the initialization
expression depends on the previous value of the aggregate. The easiest way to demonstrate this is by
attempting to swap fields of a struct or array - the following logic looks sound, but in fact is not:

**`result_location_interfering_with_swap.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;
test "attempt to swap array elements with array initializer" {
    var arr: [2]u32 = .{ 1, 2 };
    arr = .{ arr[1], arr[0] };
    // The previous line is equivalent to the following two lines:
    //   arr[0] = arr[1];
    //   arr[1] = arr[0];
    // So this fails!
    try expectEqual(2, arr[0]); // succeeds
    try expectEqual(1, arr[1]); // fails
}

```

**Shell:**

```shell
$ zig test result_location_interfering_with_swap.zig
1/1 result_location_interfering_with_swap.test.attempt to swap array elements with array initializer...expected 1, found 2
FAIL (TestExpectedEqual)
/home/ci/work/zig-bootstrap/out/host/lib/zig/std/testing.zig:118:17: 0x123a424 in expectEqualInner__anon_42695 (std.zig)
                return error.TestExpectedEqual;
                ^
/home/ci/work/zig-bootstrap/zig/doc/langref/result_location_interfering_with_swap.zig:10:5: 0x123a595 in test.attempt to swap array elements with array initializer (result_location_interfering_with_swap.zig)
    try expectEqual(1, arr[1]); // fails
    ^
0 passed; 0 skipped; 1 failed.
error: the following test command failed with exit code 1:
/home/ci/work/zig-bootstrap/out/zig-local-cache/o/b93ad8e8706156cf1a29297e83e4bc90/test --seed=0x2d82f934

```

The following table details how some common expressions propagate result locations, where
`x` and `y` are arbitrary sub-expressions. Note that
some expressions cannot provide meaningful result locations to sub-expressions, even if they
themselves have a result location.

| Expression | Result Location | Sub-expression Result Locations |
| --- | --- | --- |
| `const val: T = x` | - | `x` has result location `&val` |
| `var val: T = x` | - | `x` has result location `&val` |
| `val = x` | - | `x` has result location `&val` |
| `@as(T, x)` | `ptr` | `x` has no result location |
| `&x` | `ptr` | `x` has no result location |
| `f(x)` | `ptr` | `x` has no result location |
| `.{x}` | `ptr` | `x` has result location `&ptr[0]` |
| `.{ .a = x }` | `ptr` | `x` has result location `&ptr.a` |
| `T{x}` | `ptr` | `x` has no result location (typed initializers do not propagate result locations) |
| `T{ .a = x }` | `ptr` | `x` has no result location (typed initializers do not propagate result locations) |
| `@Int(x, y)` | - | `x` and `y` do not have result locations |
| `@typeInfo(x)` | `ptr` | `x` has no result location |
| `x << y` | `ptr` | `x` and `y` do not have result locations |
