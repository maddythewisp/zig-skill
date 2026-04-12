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
