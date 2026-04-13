---
name: zig-programming
description: >
  Zig 0.16.0 programming expertise with correct API patterns, 303 tested recipes,
  and standard library reference. Includes critical 0.16 API cheatsheet, async I/O
  patterns, and recipe lookup by topic and API name.
---

# Zig 0.16.0 Programming Skill

## Zig 0.16 API Cheatsheet

**This is the most critical section.** Zig 0.16 reorganized the stdlib. All I/O goes through `std.Io`.

### I/O Parameter Convention

All I/O functions take `io: std.Io` as a **value** (NOT a pointer):
```zig
pub fn readFile(io: std.Io, path: []const u8) ![]u8 { ... }
// In tests: const io: std.Io = std.testing.io;
```

### File Operations

```zig
// Open / Create / Delete
const file = try std.Io.Dir.openFile(.cwd(), io, path, .{});
const file = try std.Io.Dir.createFile(.cwd(), io, path, .{});
try std.Io.Dir.deleteFile(.cwd(), io, path);
defer file.close(io);

// Read entire file
const data = try std.Io.Dir.readFileAlloc(.cwd(), io, path, allocator, .unlimited);

// Buffered write (MUST flush)
var wbuf: [4096]u8 = undefined;
var writer = file.writer(io, &wbuf);
try writer.interface.writeAll(content);
try writer.flush();

// Unbuffered write
try file.writeStreamingAll(io, data);

// Read (scatter list - note the &.{&buf} pattern)
const n = try file.readStreaming(io, &.{&buffer});
// readStreaming returns error.EndOfStream at EOF, not 0

// Positional read/write (no seeking needed)
const n = try file.readPositionalAll(io, &buffer, offset);
try file.writePositionalAll(io, data, offset);

// Seek via Writer (File has no seekTo)
var wb: [1]u8 = undefined;
var fw = file.writer(io, &wb);
try fw.seekTo(0);

// Stat / Length
const stat = try file.stat(io);  // returns .size, .permissions, .kind
const len = try file.length(io);
try file.setLength(io, new_len);

// File struct literal (requires .flags)
const f = std.Io.File{ .handle = fd, .flags = .{ .nonblocking = false } };
```

### Directory Operations

```zig
try std.Io.Dir.createDir(.cwd(), io, "dir", .default_dir);
try std.Io.Dir.createDirPath(.cwd(), io, "a/b/c");
var dir = try std.Io.Dir.openDir(.cwd(), io, path, .{});
defer dir.close(io);
try std.Io.Dir.deleteTree(.cwd(), io, path);
try std.Io.Dir.rename(.cwd(), old, .cwd(), new, io);
try std.Io.Dir.writeFile(.cwd(), io, .{ .sub_path = path, .data = content });

// With Dir handle (for testable code)
const file = try dir.createFile(io, "name.txt", .{});
const file = try dir.openFile(io, "name.txt", .{});

// Iteration (must open with .iterate = true for fresh iteration)
var idir = try dir.openDir(io, ".", .{ .iterate = true });
defer idir.close(io);
var iter = idir.iterate();
while (try iter.next(io)) |entry| { ... }

// Testing
var tmp = std.testing.tmpDir(.{});
defer tmp.cleanup();
```

### Data Structures (changed in 0.16)

```zig
// ArrayList - use .empty, pass allocator to methods
var list = std.ArrayList(T).empty;
try list.append(allocator, value);
list.deinit(allocator);

// HashMap - init unchanged
var map = std.AutoHashMap(K, V).init(allocator);
defer map.deinit();

// PriorityQueue
var pq = std.PriorityQueue(T, Ctx, cmpFn).empty;
try pq.push(allocator, value);
```

### Networking

```zig
const net = std.Io.net;

// TCP server
const addr = net.IpAddress{ .ip4 = net.Ip4Address.loopback(port) };
var server = try addr.listen(io, .{ .reuse_address = true });
defer server.deinit(io);
var client = try server.accept(io);  // returns Stream

// UDP socket
const addr = net.IpAddress{ .ip4 = net.Ip4Address.unspecified(port) };
var socket = try addr.bind(io, .{ .mode = .dgram });
defer socket.close(io);

// TCP client
var stream = try addr.connect(io, .{});
defer stream.close(io);

// Socket options (posix.setsockopt still works)
try std.posix.setsockopt(socket.handle, ...);
```

### Process, Time, Threading

```zig
// Spawn process
var child = try std.process.spawn(io, .{
    .argv = &.{ "cmd", "arg" },
    .stdin = .ignore, .stdout = .ignore, .stderr = .ignore,
});
_ = try child.wait(io);

// Clock
const ts = std.Io.Clock.awake.now(io);  // Io.Timestamp with .nanoseconds (i96)
const wall = std.Io.Clock.real.now(io);

// Sleep
io.sleep(.fromMilliseconds(100), .awake);

// Threading (WaitGroup removed in 0.16)
const t = try std.Thread.spawn(.{}, func, .{args});
t.join();

// Mutex
var mutex: std.atomic.Mutex = .unlocked;
mutex.lock();
defer mutex.unlock();
```

### Other Changes

```zig
// Allocator
var da = std.heap.DebugAllocator(.{}).init;  // replaces GeneralPurposeAllocator

// Custom format
pub fn format(self: T, writer: *std.Io.Writer) std.Io.Writer.Error!void { ... }
// Use {f} specifier: std.debug.print("{f}", .{value});

// Permissions (enum, not struct)
const perms = std.Io.File.Permissions.fromMode(mode);
// Or use stat.permissions directly

// Random
var prng = std.Random.DefaultPrng.init(seed);
const random = prng.random();
```

### Removed APIs (do NOT use)

These no longer exist in `std.posix` or `std.fs`:
`posix.socket`, `posix.close`, `posix.dup`, `posix.pipe`, `posix.bind`,
`posix.listen`, `posix.accept`, `posix.recv`, `posix.send`, `posix.fcntl`,
`file.seekTo`, `file.read`, `file.getPos`, `file.setEndPos`,
`fs.cwd()`, `fs.File`, `ArrayList(T).init(alloc)`

For raw syscalls, use `std.os.linux` directly (e.g., `linux.dup`, `linux.pipe2`, `linux.socketpair`).

---

## Async I/O Quick Reference

```zig
// async: operations CAN proceed out-of-order (default choice)
var fut_a = io.async(doWork, .{io, data_a});
var fut_b = io.async(doWork, .{io, data_b});
try fut_a.await(io);
try fut_b.await(io);

// concurrent: operations MUST run simultaneously (producer-consumer)
var fut = io.concurrent(producer, .{io, queue}) catch |err| switch (err) {
    error.ConcurrencyUnavailable => { /* fallback */ },
    else => return err,
};
defer fut.cancel(io);  // always cancel on scope exit
```

**Use `io.async()` by default.** Only use `io.concurrent()` when operations MUST run in parallel.
For deep dive: read `references/async-vs-concurrent.md`.

---

## Recipe Lookup

303 tested recipes in `zig-bbq-cookbook/code/`. Each file is self-contained with tests.
Run with `zig test <file>`. Read any recipe with `Read zig-bbq-cookbook/code/{path}/recipe_X_Y.zig`.

### By Topic

| Topic | Directory | Count |
|-------|-----------|-------|
| Zig Bootcamp | `code/00-bootcamp/` | 14 |
| Foundation | `code/01-foundation/` | 5 |
| Data Structures | `code/02-core/01-data-structures/` | 20 |
| Strings & Text | `code/02-core/02-strings-and-text/` | 14 |
| Numbers & Time | `code/02-core/03-numbers-dates-times/` | 12 |
| Iterators | `code/02-core/04-iterators-generators/` | 13 |
| Files & I/O | `code/02-core/05-files-io/` | 22 |
| Data Encoding | `code/03-advanced/06-data-encoding/` | 9 |
| Functions | `code/03-advanced/07-functions/` | 11 |
| Structs & Objects | `code/03-advanced/08-structs-unions-objects/` | 22 |
| Metaprogramming | `code/03-advanced/09-metaprogramming/` | 17 |
| Modules & Build | `code/03-advanced/10-modules-build-system/` | 11 |
| Networking & HTTP | `code/04-specialized/11-network-web/` | 13 |
| Concurrency | `code/04-specialized/12-concurrency/` | 8 |
| Utility Scripting | `code/04-specialized/13-utility-scripting/` | 15 |
| Testing & Debug | `code/04-specialized/14-testing-debugging/` | 14 |
| C Interop | `code/04-specialized/15-c-interoperability/` | 7 |
| Build System | `code/05-zig-paradigms/16-zig-build-system/` | 7 |
| Advanced Comptime | `code/05-zig-paradigms/17-advanced-comptime/` | 7 |
| Memory Management | `code/05-zig-paradigms/18-memory-management/` | 6 |
| WebAssembly | `code/05-zig-paradigms/19-webassembly-freestanding/` | 6 |
| High-Perf Networking | `code/05-zig-paradigms/20-high-perf-networking/` | 6 |

### By API

For a full API-to-recipe mapping, read `references/api-recipe-index.md`.

Key recipes for common tasks:

| Need | Recipe files |
|------|-------------|
| File read/write | `05-files-io/recipe_5_1` |
| File copy/move | `13-utility-scripting/recipe_13_6` |
| Temp files | `05-files-io/recipe_5_17` |
| Dir handles (testable I/O) | `05-files-io/recipe_5_20` |
| Binary I/O | `06-data-encoding/recipe_6_9` |
| JSON parse | `06-data-encoding/recipe_6_1`, `recipe_6_2` |
| HTTP client | `11-network-web/recipe_11_1` |
| TCP server | `20-high-perf-networking/recipe_20_1` |
| UDP multicast | `20-high-perf-networking/recipe_20_5` |
| ArrayList patterns | `00-bootcamp/recipe_0_6` |
| HashMap patterns | `01-data-structures/recipe_1_7`, `recipe_1_12` |
| Thread spawn/join | `12-concurrency/recipe_12_10` |
| Process spawn | `13-utility-scripting/recipe_13_14` |
| Custom allocator | `18-memory-management/recipe_18_1` |
| Visitor pattern | `08-structs-unions-objects/recipe_8_20` |
| Comptime generics | `09-metaprogramming/recipe_9_1` |
| C FFI | `15-c-interoperability/recipe_15_1` |

---

## Reference Files

Read these on-demand for deeper knowledge:

| Topic | File | When to read |
|-------|------|-------------|
| Language basics | `references/core-language.md` | New to Zig |
| Control flow | `references/control-flow.md` | if/while/for/switch details |
| Functions & errors | `references/functions-errors.md` | Error handling patterns |
| Memory | `references/memory-management.md` | Allocator questions |
| Comptime | `references/comptime.md` | Compile-time programming |
| Data structures | `references/data-structures.md` | Stdlib containers |
| Stdlib builtins | `references/stdlib-builtins.md` | Grep this file, don't read whole |
| Async deep dive | `references/async-vs-concurrent.md` | async vs concurrent distinction |
| C interop | `references/c-interop.md` | FFI, @cImport, linking |
| Build system | `references/build-system.md` | build.zig configuration |
| Testing | `references/testing-quality.md` | Test framework |
| Version migration | `references/version-differences.md` | Porting from older Zig |
| API-recipe index | `references/api-recipe-index.md` | Find recipe by API name |

---

## Templates

Copy and customize from `assets/templates/`:
- `basic-program.zig` — Minimal program with allocator
- `build.zig` — Build configuration
- `test.zig` — Test file structure
- `cli-application.zig` — CLI with arg parsing
- `library-module.zig` — Library module structure
- `c-interop-module.zig` — C FFI module
- `async-function.zig` — Async I/O patterns

---

## Workflows

### Writing New Code
1. Check the API cheatsheet above for correct 0.16 syntax
2. Find a relevant recipe and read the .zig file
3. Handle errors explicitly with `try`/`catch`/`errdefer`
4. Pass `io: std.Io` and allocators as parameters
5. Write `test` blocks alongside implementation

### Debugging Compilation Errors
1. Check "Removed APIs" list — you may be using a 0.15 pattern
2. Common 0.16 issues: missing `io` parameter, wrong `readStreaming` scatter list type,
   `ArrayList(T){}` instead of `.empty`, `File.read()` instead of `readStreaming`
3. Use `std.debug.print()` for inspection, `zig test` to isolate

### Best Practices
1. **Explicit error handling** — Use `try`, `catch`, or error unions
2. **Defer cleanup** — `defer file.close(io)`, `errdefer` for error paths
3. **Pass allocators and io** — Never use global state
4. **Leverage comptime** — Use compile-time execution for generics
5. **Write tests inline** — `test "description" {}` blocks
6. **Pass `io: std.Io` (value, not pointer)** to I/O functions
7. **Default to `io.async()` over `io.concurrent()`**
