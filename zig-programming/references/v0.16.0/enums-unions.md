# Enums and Unions

*Tagged unions, enums, and variant types in Zig*

## enum

**`test_enums.zig`:**

```zig
const expect = @import("std").testing.expect;
const expectEqual = @import("std").testing.expectEqual;
const expectEqualStrings = @import("std").testing.expectEqualStrings;
const mem = @import("std").mem;

// Declare an enum.
const Type = enum {
    ok,
    not_ok,
};

// Declare a specific enum field.
const c = Type.ok;

// If you want access to the ordinal value of an enum, you
// can specify the tag type.
const Value = enum(u2) {
    zero,
    one,
    two,
};
// Now you can cast between u2 and Value.
// The ordinal value starts from 0, counting up by 1 from the previous member.
test "enum ordinal value" {
    try expectEqual(0, @intFromEnum(Value.zero));
    try expectEqual(1, @intFromEnum(Value.one));
    try expectEqual(2, @intFromEnum(Value.two));
}

// You can override the ordinal value for an enum.
const Value2 = enum(u32) {
    hundred = 100,
    thousand = 1000,
    million = 1000000,
};
test "set enum ordinal value" {
    try expectEqual(100, @intFromEnum(Value2.hundred));
    try expectEqual(1000, @intFromEnum(Value2.thousand));
    try expectEqual(1000000, @intFromEnum(Value2.million));
}

// You can also override only some values.
const Value3 = enum(u4) {
    a,
    b = 8,
    c,
    d = 4,
    e,
};
test "enum implicit ordinal values and overridden values" {
    try expectEqual(0, @intFromEnum(Value3.a));
    try expectEqual(8, @intFromEnum(Value3.b));
    try expectEqual(9, @intFromEnum(Value3.c));
    try expectEqual(4, @intFromEnum(Value3.d));
    try expectEqual(5, @intFromEnum(Value3.e));
}

// Enums can have methods, the same as structs and unions.
// Enum methods are not special, they are only namespaced
// functions that you can call with dot syntax.
const Suit = enum {
    clubs,
    spades,
    diamonds,
    hearts,

    pub fn isClubs(self: Suit) bool {
        return self == Suit.clubs;
    }
};
test "enum method" {
    const p = Suit.spades;
    try expect(!p.isClubs());
}

// An enum can be switched upon.
const Foo = enum {
    string,
    number,
    none,
};
test "enum switch" {
    const p = Foo.number;
    const what_is_it = switch (p) {
        Foo.string => "this is a string",
        Foo.number => "this is a number",
        Foo.none => "this is a none",
    };
    try expectEqualStrings(what_is_it, "this is a number");
}

// @typeInfo can be used to access the integer tag type of an enum.
const Small = enum {
    one,
    two,
    three,
    four,
};
test "std.meta.Tag" {
    try expectEqual(u2, @typeInfo(Small).@"enum".tag_type);
}

// @typeInfo tells us the field count and the fields names:
test "@typeInfo" {
    try expectEqual(4, @typeInfo(Small).@"enum".fields.len);
    try expectEqualStrings(@typeInfo(Small).@"enum".fields[1].name, "two");
}

// @tagName gives a [:0]const u8 representation of an enum value:
test "@tagName" {
    try expectEqualStrings(@tagName(Small.three), "three");
}

```

**Shell:**

```shell
$ zig test test_enums.zig
1/8 test_enums.test.enum ordinal value...OK
2/8 test_enums.test.set enum ordinal value...OK
3/8 test_enums.test.enum implicit ordinal values and overridden values...OK
4/8 test_enums.test.enum method...OK
5/8 test_enums.test.enum switch...OK
6/8 test_enums.test.std.meta.Tag...OK
7/8 test_enums.test.@typeInfo...OK
8/8 test_enums.test.@tagName...OK
All 8 tests passed.

```

See also:

- [@typeInfo](#typeInfo)
- [@tagName](#tagName)
- [@sizeOf](#sizeOf)

### extern enum

By default, enums are not guaranteed to be compatible with the C ABI:

**`enum_export_error.zig`:**

```zig
const Foo = enum { a, b, c };
export fn entry(foo: Foo) void {
    _ = foo;
}

```

**Shell:**

```shell
$ zig build-obj enum_export_error.zig -target x86_64-linux
/home/ci/work/zig-bootstrap/zig/doc/langref/enum_export_error.zig:2:17: error: parameter of type 'enum_export_error.Foo' not allowed in function with calling convention 'x86_64_sysv'
export fn entry(foo: Foo) void {
                ^~~~~~~~
/home/ci/work/zig-bootstrap/zig/doc/langref/enum_export_error.zig:1:13: note: integer tag type of enum is inferred
const Foo = enum { a, b, c };
            ^~~~~~~~~~~~~~~~
/home/ci/work/zig-bootstrap/zig/doc/langref/enum_export_error.zig:1:13: note: consider explicitly specifying the integer tag type
/home/ci/work/zig-bootstrap/zig/doc/langref/enum_export_error.zig:1:13: note: enum declared here
referenced by:
    root: /home/ci/work/zig-bootstrap/out/host/lib/zig/std/start.zig:13:22
    comptime: /home/ci/work/zig-bootstrap/out/host/lib/zig/std/start.zig:20:9
    2 reference(s) hidden; use '-freference-trace=4' to see all references


```

For a C-ABI-compatible enum, provide an explicit tag type to
the enum:

**`enum_export.zig`:**

```zig
const Foo = enum(c_int) { a, b, c };
export fn entry(foo: Foo) void {
    _ = foo;
}

```

**Shell:**

```shell
$ zig build-obj enum_export.zig

```

### Enum Literals

Enum literals allow specifying the name of an enum field without specifying the enum type:

**`test_enum_literals.zig`:**

```zig
const std = @import("std");
const expect = std.testing.expect;
const expectEqual = std.testing.expectEqual;

const Color = enum {
    auto,
    off,
    on,
};

test "enum literals" {
    const color1: Color = .auto;
    const color2 = Color.auto;
    try expectEqual(color1, color2);
}

test "switch using enum literals" {
    const color = Color.on;
    const result = switch (color) {
        .auto => false,
        .on => true,
        .off => false,
    };
    try expect(result);
}

```

**Shell:**

```shell
$ zig test test_enum_literals.zig
1/2 test_enum_literals.test.enum literals...OK
2/2 test_enum_literals.test.switch using enum literals...OK
All 2 tests passed.

```

### Non-exhaustive enum

A non-exhaustive enum can be created by adding a trailing `_` field.
The enum must specify a tag type and cannot consume every enumeration value.

[@enumFromInt](#enumFromInt) on a non-exhaustive enum involves the safety semantics
of [@intCast](#intCast) to the integer tag type, but beyond that always results in
a well-defined enum value.

A switch on a non-exhaustive enum can include a `_` prong as an alternative to an `else` prong.
With a `_` prong the compiler errors if all the known tag names are not handled by the switch.

**`test_switch_non-exhaustive.zig`:**

```zig
const std = @import("std");
const expect = std.testing.expect;

const Number = enum(u8) {
    one,
    two,
    three,
    _,
};

test "switch on non-exhaustive enum" {
    const number = Number.one;
    const result = switch (number) {
        .one => true,
        .two, .three => false,
        _ => false,
    };
    try expect(result);
    const is_one = switch (number) {
        .one => true,
        else => false,
    };
    try expect(is_one);
}

```

**Shell:**

```shell
$ zig test test_switch_non-exhaustive.zig
1/1 test_switch_non-exhaustive.test.switch on non-exhaustive enum...OK
All 1 tests passed.

```

---

## union

A bare `union` defines a set of possible types that a value
can be as a list of fields. Only one field can be active at a time.
The in-memory representation of bare unions is not guaranteed.
Bare unions cannot be used to reinterpret memory. For that, use [@ptrCast](#ptrCast),
or use an [extern union](#extern-union) or a [packed union](#packed-union) which have
guaranteed in-memory layout.
[Accessing the non-active field](#Wrong-Union-Field-Access) is
safety-checked [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior):

**`test_wrong_union_access.zig`:**

```zig
const Payload = union {
    int: i64,
    float: f64,
    boolean: bool,
};
test "simple union" {
    var payload = Payload{ .int = 1234 };
    payload.float = 12.34;
}

```

**Shell:**

```shell
$ zig test test_wrong_union_access.zig
1/1 test_wrong_union_access.test.simple union...thread 3972040 panic: access of union field 'float' while field 'int' is active
/home/ci/work/zig-bootstrap/zig/doc/langref/test_wrong_union_access.zig:8:12: 0x123a432 in test.simple union (test_wrong_union_access.zig)
    payload.float = 12.34;
           ^
/home/ci/work/zig-bootstrap/out/host/lib/zig/compiler/test_runner.zig:291:25: 0x11f4636 in mainTerminal (test_runner.zig)
        if (test_fn.func()) |_| {
                        ^
/home/ci/work/zig-bootstrap/out/host/lib/zig/compiler/test_runner.zig:73:28: 0x11f3e52 in main (test_runner.zig)
        return mainTerminal(init);
                           ^
/home/ci/work/zig-bootstrap/out/host/lib/zig/std/start.zig:686:88: 0x11f07b6 in callMain (std.zig)
    if (fn_info.params[0].type.? == std.process.Init.Minimal) return wrapMain(root.main(.{
                                                                                       ^
/home/ci/work/zig-bootstrap/out/host/lib/zig/std/start.zig:190:5: 0x11f01c1 in _start (std.zig)
    asm volatile (switch (native_arch) {
    ^
error: the following test command terminated with signal ABRT:
/home/ci/work/zig-bootstrap/out/zig-local-cache/o/f20cc5c09b12fc0e8ea2cdd2590759e7/test --seed=0xb860019a

```

You can activate another field by assigning the entire union:

**`test_simple_union.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const Payload = union {
    int: i64,
    float: f64,
    boolean: bool,
};
test "simple union" {
    var payload = Payload{ .int = 1234 };
    try expectEqual(1234, payload.int);
    payload = Payload{ .float = 12.34 };
    try expectEqual(12.34, payload.float);
}

```

**Shell:**

```shell
$ zig test test_simple_union.zig
1/1 test_simple_union.test.simple union...OK
All 1 tests passed.

```

In order to use [switch](21-switch.md#switch) with a union, it must be a [Tagged union](#Tagged-union).

To initialize a union when the tag is a [comptime](34-comptime.md#comptime)-known name, see [@unionInit](#unionInit).

### Tagged union

Unions can be declared with an enum tag type.
This turns the union into a *tagged* union, which makes it eligible
to use with [switch](21-switch.md#switch) expressions. When switching on tagged unions,
the tag value can be obtained using an additional capture.
Tagged unions coerce to their tag type: [Type Coercion: Unions and Enums](#Type-Coercion-Unions-and-Enums).

**`test_tagged_union.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const ComplexTypeTag = enum {
    ok,
    not_ok,
};
const ComplexType = union(ComplexTypeTag) {
    ok: u8,
    not_ok: void,
};

test "switch on tagged union" {
    const c = ComplexType{ .ok = 42 };
    try expectEqual(ComplexTypeTag.ok, @as(ComplexTypeTag, c));

    switch (c) {
        .ok => |value| try expectEqual(42, value),
        .not_ok => unreachable,
    }

    switch (c) {
        .ok => |_, tag| {
            // Because we're in the '.ok' prong, 'tag' is compile-time known to be '.ok':
            comptime std.debug.assert(tag == .ok);
        },
        .not_ok => unreachable,
    }
}

test "get tag type" {
    try expectEqual(ComplexTypeTag, std.meta.Tag(ComplexType));
}

```

**Shell:**

```shell
$ zig test test_tagged_union.zig
1/2 test_tagged_union.test.switch on tagged union...OK
2/2 test_tagged_union.test.get tag type...OK
All 2 tests passed.

```

In order to modify the payload of a tagged union in a switch expression,
place a `*` before the variable name to make it a pointer:

**`test_switch_modify_tagged_union.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const ComplexTypeTag = enum {
    ok,
    not_ok,
};
const ComplexType = union(ComplexTypeTag) {
    ok: u8,
    not_ok: void,
};

test "modify tagged union in switch" {
    var c = ComplexType{ .ok = 42 };

    switch (c) {
        ComplexTypeTag.ok => |*value| value.* += 1,
        ComplexTypeTag.not_ok => unreachable,
    }

    try expectEqual(43, c.ok);
}

```

**Shell:**

```shell
$ zig test test_switch_modify_tagged_union.zig
1/1 test_switch_modify_tagged_union.test.modify tagged union in switch...OK
All 1 tests passed.

```

Unions can be made to infer the enum tag type.
Further, unions can have methods just like structs and enums.

**`test_union_method.zig`:**

```zig
const std = @import("std");
const expect = std.testing.expect;

const Variant = union(enum) {
    int: i32,
    boolean: bool,

    // void can be omitted when inferring enum tag type.
    none,

    fn truthy(self: Variant) bool {
        return switch (self) {
            Variant.int => |x_int| x_int != 0,
            Variant.boolean => |x_bool| x_bool,
            Variant.none => false,
        };
    }
};

test "union method" {
    var v1: Variant = .{ .int = 1 };
    var v2: Variant = .{ .boolean = false };
    var v3: Variant = .none;

    try expect(v1.truthy());
    try expect(!v2.truthy());
    try expect(!v3.truthy());
}

```

**Shell:**

```shell
$ zig test test_union_method.zig
1/1 test_union_method.test.union method...OK
All 1 tests passed.

```

Unions with inferred enum tag types can also assign ordinal values to their inferred tag.
This requires the tag to specify an explicit integer type.
[@intFromEnum](#intFromEnum) can be used to access the ordinal value corresponding to the active field.

**`test_tagged_union_with_tag_values.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const Tagged = union(enum(u32)) {
    int: i64 = 123,
    boolean: bool = 67,
};

test "tag values" {
    const int: Tagged = .{ .int = -40 };
    try expectEqual(123, @intFromEnum(int));

    const boolean: Tagged = .{ .boolean = false };
    try expectEqual(67, @intFromEnum(boolean));
}

```

**Shell:**

```shell
$ zig test test_tagged_union_with_tag_values.zig
1/1 test_tagged_union_with_tag_values.test.tag values...OK
All 1 tests passed.

```

[@tagName](#tagName) can be used to return a [comptime](34-comptime.md#comptime)
`[:0]const u8` value representing the field name:

**`test_tagName.zig`:**

```zig
const std = @import("std");
const expectEqualSlices = std.testing.expectEqualSlices;

const Small2 = union(enum) {
    a: i32,
    b: bool,
    c: u8,
};
test "@tagName" {
    try expectEqualSlices(u8, "a", @tagName(Small2.a));
}

```

**Shell:**

```shell
$ zig test test_tagName.zig
1/1 test_tagName.test.@tagName...OK
All 1 tests passed.

```

### extern union

An `extern union` has memory layout guaranteed to be compatible with
the target C ABI.

See also:

- [extern struct](#extern-struct)

### packed union

A `packed union` has well-defined in-memory layout and is eligible
to be in a [packed struct](#packed-struct).

All fields in a packed union must have the same [@bitSizeOf](#bitSizeOf).

Equating packed unions results in a comparison of the backing integer,
and only works for the `==` and `!=` [Operators](11-operators.md#Operators).

**`test_packed_union_equality.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "packed union equality" {
    const U = packed union {
        a: u4,
        b: i4,
    };
    const x: U = .{ .a = 3 };
    const y: U = .{ .b = 3 };
    try expectEqual(x, y);
}

```

**Shell:**

```shell
$ zig test test_packed_union_equality.zig
1/1 test_packed_union_equality.test.packed union equality...OK
All 1 tests passed.

```

### Anonymous Union Literals

[Anonymous Struct Literals](#Anonymous-Struct-Literals) syntax can be used to initialize unions without specifying
the type:

**`test_anonymous_union.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const Number = union {
    int: i32,
    float: f64,
};

test "anonymous union literal syntax" {
    const i: Number = .{ .int = 42 };
    const f = makeNumber();
    try expectEqual(42, i.int);
    try expectEqual(12.34, f.float);
}

fn makeNumber() Number {
    return .{ .float = 12.34 };
}

```

**Shell:**

```shell
$ zig test test_anonymous_union.zig
1/1 test_anonymous_union.test.anonymous union literal syntax...OK
All 1 tests passed.

```

---

## opaque

`opaque {}` declares a new type with an unknown (but non-zero) size and alignment.
It can contain declarations the same as [structs](16-struct.md#struct), [unions](18-union.md#union),
and [enums](17-enum.md#enum).

This is typically used for type safety when interacting with C code that does not expose struct details.
Example:

**`test_opaque.zig`:**

```zig
const Derp = opaque {};
const Wat = opaque {};

extern fn bar(d: *Derp) void;
fn foo(w: *Wat) callconv(.c) void {
    bar(w);
}

test "call foo" {
    foo(undefined);
}

```

**Shell:**

```shell
$ zig test test_opaque.zig
/home/ci/work/zig-bootstrap/zig/doc/langref/test_opaque.zig:6:9: error: expected type '*test_opaque.Derp', found '*test_opaque.Wat'
    bar(w);
        ^
/home/ci/work/zig-bootstrap/zig/doc/langref/test_opaque.zig:6:9: note: pointer type child 'test_opaque.Wat' cannot cast into pointer type child 'test_opaque.Derp'
/home/ci/work/zig-bootstrap/zig/doc/langref/test_opaque.zig:2:13: note: opaque declared here
const Wat = opaque {};
            ^~~~~~~~~
/home/ci/work/zig-bootstrap/zig/doc/langref/test_opaque.zig:1:14: note: opaque declared here
const Derp = opaque {};
             ^~~~~~~~~
/home/ci/work/zig-bootstrap/zig/doc/langref/test_opaque.zig:4:18: note: parameter type declared here
extern fn bar(d: *Derp) void;
                 ^~~~~
referenced by:
    test.call foo: /home/ci/work/zig-bootstrap/zig/doc/langref/test_opaque.zig:10:8


```
