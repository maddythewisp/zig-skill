## Hello World

**`hello.zig`:**

```zig
const std = @import("std");

pub fn main(init: std.process.Init) !void {
    try std.Io.File.stdout().writeStreamingAll(init.io, "Hello, World!\n");
}

```

**Shell:**

```shell
$ zig build-exe hello.zig
$ ./hello
Hello, World!

```

Most of the time, it is more appropriate to write to stderr rather than stdout, and
whether or not the message is successfully written to the stream is irrelevant.
Also, formatted printing often comes in handy. For this common case,
there is a simpler API:

**`hello_again.zig`:**

```zig
const std = @import("std");

pub fn main() void {
    std.debug.print("Hello, {s}!\n", .{"World"});
}

```

**Shell:**

```shell
$ zig build-exe hello_again.zig
$ ./hello_again
Hello, World!

```

In this case, the `!` may be omitted from the return
type of `main` because no errors are returned from the function.

See also:

- [Values](06-values.md#Values)
- [Tuples](#Tuples)
- [@import](#import)
- [Errors](29-errors.md#Errors)
- [Entry Point](#Entry-Point)
- [Source Encoding](50-source-encoding.md#Source-Encoding)
- [try](#try)
