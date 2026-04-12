# Arrays, Vectors, and Slices

*Working with sequential data structures in Zig*

## Arrays

**`test_arrays.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;
const assert = @import("std").debug.assert;
const mem = @import("std").mem;

// array literal
const message = [_]u8{ 'h', 'e', 'l', 'l', 'o' };

// alternative initialization using result location
const alt_message: [5]u8 = .{ 'h', 'e', 'l', 'l', 'o' };

comptime {
    assert(mem.eql(u8, &message, &alt_message));
}

// get the size of an array
comptime {
    assert(message.len == 5);
}

// A string literal is a single-item pointer to an array.
const same_message = "hello";

comptime {
    assert(mem.eql(u8, &message, same_message));
}

test "iterate over an array" {
    var sum: usize = 0;
    for (message) |byte| {
        sum += byte;
    }
    try expectEqual('h' + 'e' + 'l' * 2 + 'o', sum);
}

// modifiable array
var some_integers: [100]i32 = undefined;

test "modify an array" {
    for (&some_integers, 0..) |*item, i| {
        item.* = @intCast(i);
    }
    try expectEqual(10, some_integers[10]);
    try expectEqual(99, some_integers[99]);
}

// array concatenation works if the values are known
// at compile time
const part_one = [_]i32{ 1, 2, 3, 4 };
const part_two = [_]i32{ 5, 6, 7, 8 };
const all_of_it = part_one ++ part_two;
comptime {
    assert(mem.eql(i32, &all_of_it, &[_]i32{ 1, 2, 3, 4, 5, 6, 7, 8 }));
}

// remember that string literals are arrays
const hello = "hello";
const world = "world";
const hello_world = hello ++ " " ++ world;
comptime {
    assert(mem.eql(u8, hello_world, "hello world"));
}

// ** does repeating patterns
const pattern = "ab" ** 3;
comptime {
    assert(mem.eql(u8, pattern, "ababab"));
}

// initialize an array to zero
const all_zero = [_]u16{0} ** 10;

comptime {
    assert(all_zero.len == 10);
    assert(all_zero[5] == 0);
}

// use compile-time code to initialize an array
var fancy_array = init: {
    var initial_value: [10]Point = undefined;
    for (&initial_value, 0..) |*pt, i| {
        pt.* = Point{
            .x = @intCast(i),
            .y = @intCast(i * 2),
        };
    }
    break :init initial_value;
};
const Point = struct {
    x: i32,
    y: i32,
};

test "compile-time array initialization" {
    try expectEqual(4, fancy_array[4].x);
    try expectEqual(8, fancy_array[4].y);
}

// call a function to initialize an array
var more_points = [_]Point{makePoint(3)} ** 10;
fn makePoint(x: i32) Point {
    return Point{
        .x = x,
        .y = x * 2,
    };
}
test "array initialization with function calls" {
    try expectEqual(3, more_points[4].x);
    try expectEqual(6, more_points[4].y);
    try expectEqual(10, more_points.len);
}

```

**Shell:**

```shell
$ zig test test_arrays.zig
1/4 test_arrays.test.iterate over an array...OK
2/4 test_arrays.test.modify an array...OK
3/4 test_arrays.test.compile-time array initialization...OK
4/4 test_arrays.test.array initialization with function calls...OK
All 4 tests passed.

```

See also:

- [for](23-for.md#for)
- [Slices](15-slices.md#Slices)

### Multidimensional Arrays

Multidimensional arrays can be created by nesting arrays:

**`test_multidimensional_arrays.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

const mat4x5 = [4][5]f32{
    [_]f32{ 1.0, 0.0, 0.0, 0.0, 0.0 },
    [_]f32{ 0.0, 1.0, 0.0, 1.0, 0.0 },
    [_]f32{ 0.0, 0.0, 1.0, 0.0, 0.0 },
    [_]f32{ 0.0, 0.0, 0.0, 1.0, 9.9 },
};
test "multidimensional arrays" {
    // mat4x5 itself is a one-dimensional array of arrays.
    try expectEqual(mat4x5[1], [_]f32{ 0.0, 1.0, 0.0, 1.0, 0.0 });

    // Access the 2D array by indexing the outer array, and then the inner array.
    try expectEqual(9.9, mat4x5[3][4]);

    // Here we iterate with for loops.
    for (mat4x5, 0..) |row, row_index| {
        for (row, 0..) |cell, column_index| {
            if (row_index == column_index) {
                try expectEqual(1.0, cell);
            }
        }
    }

    // Initialize a multidimensional array to zeros.
    const all_zero: [4][5]f32 = .{.{0} ** 5} ** 4;
    try expectEqual(0, all_zero[0][0]);
}

```

**Shell:**

```shell
$ zig test test_multidimensional_arrays.zig
1/1 test_multidimensional_arrays.test.multidimensional arrays...OK
All 1 tests passed.

```

### Sentinel-Terminated Arrays

The syntax `[N:x]T` describes an array which has a sentinel element of value `x` at the
index corresponding to the length `N`.

**`test_null_terminated_array.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "0-terminated sentinel array" {
    const array = [_:0]u8{ 1, 2, 3, 4 };

    try expectEqual([4:0]u8, @TypeOf(array));
    try expectEqual(4, array.len);
    try expectEqual(0, array[4]);
}

test "extra 0s in 0-terminated sentinel array" {
    // The sentinel value may appear earlier, but does not influence the compile-time 'len'.
    const array = [_:0]u8{ 1, 0, 0, 4 };

    try expectEqual([4:0]u8, @TypeOf(array));
    try expectEqual(4, array.len);
    try expectEqual(0, array[4]);
}

```

**Shell:**

```shell
$ zig test test_null_terminated_array.zig
1/2 test_null_terminated_array.test.0-terminated sentinel array...OK
2/2 test_null_terminated_array.test.extra 0s in 0-terminated sentinel array...OK
All 2 tests passed.

```

See also:

- [Sentinel-Terminated Pointers](#Sentinel-Terminated-Pointers)
- [Sentinel-Terminated Slices](#Sentinel-Terminated-Slices)

### Destructuring Arrays

Arrays can be destructured:

**`destructuring_arrays.zig`:**

```zig
const print = @import("std").debug.print;

fn swizzleRgbaToBgra(rgba: [4]u8) [4]u8 {
    // readable swizzling by destructuring
    const r, const g, const b, const a = rgba;
    return .{ b, g, r, a };
}

pub fn main() void {
    const pos = [_]i32{ 1, 2 };
    const x, const y = pos;
    print("x = {}, y = {}\n", .{x, y});

    const orange: [4]u8 = .{ 255, 165, 0, 255 };
    print("{any}\n", .{swizzleRgbaToBgra(orange)});
}

```

**Shell:**

```shell
$ zig build-exe destructuring_arrays.zig
$ ./destructuring_arrays
x = 1, y = 2
{ 0, 165, 255, 255 }

```

See also:

- [Destructuring](#Destructuring)
- [Destructuring Tuples](#Destructuring-Tuples)
- [Destructuring Vectors](#Destructuring-Vectors)

---

## Vectors

A vector is a group of booleans, [Integers](09-integers.md#Integers), [Floats](10-floats.md#Floats), or
[Pointers](14-pointers.md#Pointers) which are operated on in parallel, using SIMD instructions if possible.
Vector types are created with the builtin function [@Vector](#Vector).

Vectors generally support the same builtin operators as their underlying base types.
The only exception to this is the keywords `and` and `or` on vectors of bools, since
these operators affect control flow, which is not allowed for vectors.
All other operations are performed element-wise, and return a vector of the same length
as the input vectors. This includes:

- Arithmetic (`+`, `-`, `/`, `*`,
  `@divFloor`, `@sqrt`, `@ceil`,
  `@log`, etc.)
- Bitwise operators (`>>`, `<<`, `&`,
  `|`, `~`, etc.)
- Comparison operators (`<`, `>`, `==`, etc.)
- Boolean not (`!`)

It is prohibited to use a math operator on a mixture of scalars (individual numbers)
and vectors. Zig provides the [@splat](#splat) builtin to easily convert from scalars
to vectors, and it supports [@reduce](#reduce) and array indexing syntax to convert
from vectors to scalars. Vectors also support assignment to and from fixed-length
arrays with comptime-known length.

For rearranging elements within and between vectors, Zig provides the [@shuffle](#shuffle) and [@select](#select) functions.

Operations on vectors shorter than the target machine's native SIMD size will typically compile to single SIMD
instructions, while vectors longer than the target machine's native SIMD size will compile to multiple SIMD
instructions. If a given operation doesn't have SIMD support on the target architecture, the compiler will default
to operating on each vector element one at a time. Zig supports any comptime-known vector length up to 2^32-1,
although small powers of two (2-64) are most typical. Note that excessively long vector lengths (e.g. 2^20) may
result in compiler crashes on current versions of Zig.

**`test_vector.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "Basic vector usage" {
    // Vectors have a compile-time known length and base type.
    const a = @Vector(4, i32){ 1, 2, 3, 4 };
    const b = @Vector(4, i32){ 5, 6, 7, 8 };

    // Math operations take place element-wise.
    const c = a + b;

    // Individual vector elements can be accessed using array indexing syntax.
    try expectEqual(6, c[0]);
    try expectEqual(8, c[1]);
    try expectEqual(10, c[2]);
    try expectEqual(12, c[3]);
}

test "Conversion between vectors, arrays, and slices" {
    // Vectors can be coerced to arrays, and vice versa.
    const arr1: [4]f32 = [_]f32{ 1.1, 3.2, 4.5, 5.6 };
    const vec: @Vector(4, f32) = arr1;
    const arr2: [4]f32 = vec;
    try expectEqual(arr1, arr2);

    // You can also assign from a slice with comptime-known length to a vector using .*
    const vec2: @Vector(2, f32) = arr1[1..3].*;

    const slice: []const f32 = &arr1;
    var offset: u32 = 1; // var to make it runtime-known
    _ = &offset; // suppress 'var is never mutated' error
    // To extract a comptime-known length from a runtime-known offset,
    // first extract a new slice from the starting offset, then an array of
    // comptime-known length
    const vec3: @Vector(2, f32) = slice[offset..][0..2].*;
    try expectEqual(slice[offset], vec2[0]);
    try expectEqual(slice[offset + 1], vec2[1]);
    try expectEqual(vec2, vec3);
}

```

**Shell:**

```shell
$ zig test test_vector.zig
1/2 test_vector.test.Basic vector usage...OK
2/2 test_vector.test.Conversion between vectors, arrays, and slices...OK
All 2 tests passed.

```

TODO talk about C ABI interop  
TODO consider suggesting std.MultiArrayList

See also:

- [@splat](#splat)
- [@shuffle](#shuffle)
- [@select](#select)
- [@reduce](#reduce)

### Relationship with Arrays

Vectors and [Arrays](12-arrays.md#Arrays) each have a well-defined **bit layout**
and therefore support [@bitCast](#bitCast) between each other. [Type Coercion](#Type-Coercion) implicitly peforms
`@bitCast`.

Arrays have well-defined byte layout, but vectors do not, making [@ptrCast](#ptrCast) between
them [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior).

### Destructuring Vectors

Vectors can be destructured:

**`destructuring_vectors.zig`:**

```zig
const print = @import("std").debug.print;

// emulate punpckldq
pub fn unpack(x: @Vector(4, f32), y: @Vector(4, f32)) @Vector(4, f32) {
    const a, const c, _, _ = x;
    const b, const d, _, _ = y;
    return .{ a, b, c, d };
}

pub fn main() void {
    const x: @Vector(4, f32) = .{ 1.0, 2.0, 3.0, 4.0 };
    const y: @Vector(4, f32) = .{ 5.0, 6.0, 7.0, 8.0 };
    print("{}", .{unpack(x, y)});
}

```

**Shell:**

```shell
$ zig build-exe destructuring_vectors.zig
$ ./destructuring_vectors
{ 1, 5, 2, 6 }

```

See also:

- [Destructuring](#Destructuring)
- [Destructuring Tuples](#Destructuring-Tuples)
- [Destructuring Arrays](#Destructuring-Arrays)

---

## Slices

A slice is a pointer and a length. The difference between an array and
a slice is that the array's length is part of the type and known at
compile-time, whereas the slice's length is known at runtime.
Both can be accessed with the `len` field.

**`test_basic_slices.zig`:**

```zig
const expectEqual = @import("std").testing.expectEqual;
const expectEqualSlices = @import("std").testing.expectEqualSlices;

test "basic slices" {
    var array = [_]i32{ 1, 2, 3, 4 };
    var known_at_runtime_zero: usize = 0;
    _ = &known_at_runtime_zero;
    const slice = array[known_at_runtime_zero..array.len];

    // alternative initialization using result location
    const alt_slice: []const i32 = &.{ 1, 2, 3, 4 };

    try expectEqualSlices(i32, slice, alt_slice);

    try expectEqual([]i32, @TypeOf(slice));
    try expectEqual(&array[0], &slice[0]);
    try expectEqual(array.len, slice.len);

    // If you slice with comptime-known start and end positions, the result is
    // a pointer to an array, rather than a slice.
    const array_ptr = array[0..array.len];
    try expectEqual(*[array.len]i32, @TypeOf(array_ptr));

    // You can perform a slice-by-length by slicing twice. This allows the compiler
    // to perform some optimisations like recognising a comptime-known length when
    // the start position is only known at runtime.
    var runtime_start: usize = 1;
    _ = &runtime_start;
    const length = 2;
    const array_ptr_len = array[runtime_start..][0..length];
    try expectEqual(*[length]i32, @TypeOf(array_ptr_len));

    // Using the address-of operator on a slice gives a single-item pointer.
    try expectEqual(*i32, @TypeOf(&slice[0]));
    // Using the `ptr` field gives a many-item pointer.
    try expectEqual([*]i32, @TypeOf(slice.ptr));
    try expectEqual(@intFromPtr(slice.ptr), @intFromPtr(&slice[0]));

    // Slices have array bounds checking. If you try to access something out
    // of bounds, you'll get a safety check failure:
    slice[10] += 1;

    // Note that `slice.ptr` does not invoke safety checking, while `&slice[0]`
    // asserts that the slice has len > 0.

    // Empty slices can be created like this:
    const empty1 = &[0]u8{};
    // If the type is known you can use this short hand:
    const empty2: []u8 = &.{};
    try expectEqual(0, empty1.len);
    try expectEqual(0, empty2.len);

    // A zero-length initialization can always be used to create an empty slice, even if the slice is mutable.
    // This is because the pointed-to data is zero bits long, so its immutability is irrelevant.
}

```

**Shell:**

```shell
$ zig test test_basic_slices.zig
1/1 test_basic_slices.test.basic slices...thread 3973431 panic: index out of bounds: index 10, len 4
/home/ci/work/zig-bootstrap/zig/doc/langref/test_basic_slices.zig:41:10: 0x123c484 in test.basic slices (test_basic_slices.zig)
    slice[10] += 1;
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
/home/ci/work/zig-bootstrap/out/zig-local-cache/o/51504f11d441dd6c0281f1f7f280703f/test --seed=0x982cd4c9

```

This is one reason we prefer slices to pointers.

**`test_slices.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;
const expectEqualStrings = std.testing.expectEqualStrings;
const fmt = std.fmt;

test "using slices for strings" {
    // Zig has no concept of strings. String literals are const pointers
    // to null-terminated arrays of u8, and by convention parameters
    // that are "strings" are expected to be UTF-8 encoded slices of u8.
    // Here we coerce *const [5:0]u8 and *const [6:0]u8 to []const u8
    const hello: []const u8 = "hello";
    const world: []const u8 = "ä¸ç";

    var all_together: [100]u8 = undefined;
    // You can use slice syntax with at least one runtime-known index on an
    // array to convert an array into a slice.
    var start: usize = 0;
    _ = &start;
    const all_together_slice = all_together[start..];
    // String concatenation example.
    const hello_world = try fmt.bufPrint(all_together_slice, "{s} {s}", .{ hello, world });

    // Generally, you can use UTF-8 and not worry about whether something is a
    // string. If you don't need to deal with individual characters, no need
    // to decode.
    try expectEqualStrings("hello ä¸ç", hello_world);
}

test "slice pointer" {
    var array: [10]u8 = undefined;
    const ptr = &array;
    try expectEqual(*[10]u8, @TypeOf(ptr));

    // A pointer to an array can be sliced just like an array:
    var start: usize = 0;
    var end: usize = 5;
    _ = .{ &start, &end };
    const slice = ptr[start..end];
    // The slice is mutable because we sliced a mutable pointer.
    try expectEqual([]u8, @TypeOf(slice));
    slice[2] = 3;
    try expectEqual(3, array[2]);

    // Again, slicing with comptime-known indexes will produce another pointer
    // to an array:
    const ptr2 = slice[2..3];
    try expectEqual(1, ptr2.len);
    try expectEqual(3, ptr2[0]);
    try expectEqual(*[1]u8, @TypeOf(ptr2));
}

```

**Shell:**

```shell
$ zig test test_slices.zig
1/2 test_slices.test.using slices for strings...OK
2/2 test_slices.test.slice pointer...OK
All 2 tests passed.

```

See also:

- [Pointers](14-pointers.md#Pointers)
- [for](23-for.md#for)
- [Arrays](12-arrays.md#Arrays)

### Sentinel-Terminated Slices

The syntax `[:x]T` is a slice which has a runtime-known length
and also guarantees a sentinel value at the element indexed by the length. The type does not
guarantee that there are no sentinel elements before that. Sentinel-terminated slices allow element
access to the `len` index.

**`test_null_terminated_slice.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "0-terminated slice" {
    const slice: [:0]const u8 = "hello";

    try expectEqual(5, slice.len);
    try expectEqual(0, slice[5]);
}

```

**Shell:**

```shell
$ zig test test_null_terminated_slice.zig
1/1 test_null_terminated_slice.test.0-terminated slice...OK
All 1 tests passed.

```

Sentinel-terminated slices can also be created using a variation of the slice syntax
`data[start..end :x]`, where `data` is a many-item pointer,
array or slice and `x` is the sentinel value.

**`test_null_terminated_slicing.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "0-terminated slicing" {
    var array = [_]u8{ 3, 2, 1, 0, 3, 2, 1, 0 };
    var runtime_length: usize = 3;
    _ = &runtime_length;
    const slice = array[0..runtime_length :0];

    try expectEqual([:0]u8, @TypeOf(slice));
    try expectEqual(3, slice.len);
}

```

**Shell:**

```shell
$ zig test test_null_terminated_slicing.zig
1/1 test_null_terminated_slicing.test.0-terminated slicing...OK
All 1 tests passed.

```

Sentinel-terminated slicing asserts that the element in the sentinel position of the backing data is
actually the sentinel value. If this is not the case, safety-checked [Illegal Behavior](41-illegal-behavior.md#Illegal-Behavior) results.

**`test_sentinel_mismatch.zig`:**

```zig
const std = @import("std");
const expectEqual = std.testing.expectEqual;

test "sentinel mismatch" {
    var array = [_]u8{ 3, 2, 1, 0 };

    // Creating a sentinel-terminated slice from the array with a length of 2
    // will result in the value `1` occupying the sentinel element position.
    // This does not match the indicated sentinel value of `0` and will lead
    // to a runtime panic.
    var runtime_length: usize = 2;
    _ = &runtime_length;
    const slice = array[0..runtime_length :0];

    _ = slice;
}

```

**Shell:**

```shell
$ zig test test_sentinel_mismatch.zig
1/1 test_sentinel_mismatch.test.sentinel mismatch...thread 3970800 panic: sentinel mismatch: expected 0, found 1
/home/ci/work/zig-bootstrap/zig/doc/langref/test_sentinel_mismatch.zig:13:24: 0x123a49f in test.sentinel mismatch (test_sentinel_mismatch.zig)
    const slice = array[0..runtime_length :0];
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
/home/ci/work/zig-bootstrap/out/zig-local-cache/o/b5e8530f0b814f26e90157b381a3a786/test --seed=0xe43c76a2

```

See also:

- [Sentinel-Terminated Pointers](#Sentinel-Terminated-Pointers)
- [Sentinel-Terminated Arrays](#Sentinel-Terminated-Arrays)
