# API-to-Recipe Index

Maps standard library APIs to cookbook recipe files containing working examples.
All recipes are in `zig-bbq-cookbook/code/`. Run with `zig test <file>`.

## File I/O (`std.Io.Dir`, `std.Io.File`)

| API | Key Recipes |
|-----|-------------|
| `Io.Dir.openFile` | 5.1, 5.4, 5.5, 5.8, 5.10, 5.16, 5.20, 5.21 |
| `Io.Dir.createFile` | 5.1, 5.2, 5.3, 5.5, 5.8, 5.16, 5.17, 5.20, 5.21 |
| `Io.Dir.deleteFile` | 5.1, 5.2, 5.3, 5.5, 5.16, 5.17, 5.21 |
| `Io.Dir.readFileAlloc` | 5.1, 5.3, 5.5, 5.7, 5.17, 5.20, 5.21, 13.7 |
| `Io.Dir.createDirPath` | 5.12, 5.20, 5.22, 13.6, 13.7, 13.8 |
| `Io.Dir.openDir` | 5.13, 5.14, 5.17, 5.20, 5.22, 13.6, 13.7 |
| `Io.Dir.deleteTree` | 5.5, 5.12, 5.13, 5.14, 5.17, 5.22, 13.6, 13.7 |
| `Io.Dir.rename` | 5.5, 5.22, 13.6, 13.10 |
| `Io.Dir.writeFile` | 13.7 |
| `file.writer(io, &buf)` | 5.1, 5.2, 5.3, 5.4, 5.7, 5.21, 6.4, 13.1 |
| `file.reader(io, &buf)` | 5.1, 5.4, 5.7, 5.8, 5.9, 13.1, 13.3 |
| `file.writeStreamingAll` | 5.5, 5.8, 5.9, 5.10, 5.13, 5.16, 5.17, 5.18, 5.20, 5.21 |
| `file.readStreaming` | 5.10, 5.16, 5.19, 5.21, 6.4, 6.9, 11.9, 13.6 |
| `file.readPositionalAll` | 5.8, 5.9, 5.16, 5.17, 5.21 |
| `file.writePositionalAll` | 5.1, 5.2, 5.8, 5.21 |
| `file.stat(io)` | 5.4, 5.5, 5.10, 5.14, 5.20, 5.21, 6.9, 13.6 |
| `file.createMemoryMap` | 6.9 |
| `Writer.interface.writeAll` | 5.1, 5.3, 5.4, 5.7, 5.21 |
| `Writer.flush()` | 5.1, 5.2, 5.3, 5.4, 5.7, 5.21 |
| `Writer.print()` | 5.1, 5.2, 5.3 |
| `Io.Writer.fixed()` | 5.6, 6.9, 7.1, 8.1, 8.2, 11.9, 13.1, 13.2 |
| `Io.Reader.fixed()` | 5.6, 6.1, 6.9, 13.1, 13.3 |
| `testing.tmpDir` | 5.17, 5.20, 5.22, 6.3, 6.9, 14.4, 20.2 |

## Data Structures

| API | Key Recipes |
|-----|-------------|
| `std.ArrayList` | 0.6, 0.7, 0.12, 1.1, 1.3, 1.5, 1.6, 1.10 |
| `std.AutoHashMap` | 1.4, 1.6, 1.7, 1.9, 1.10, 1.12, 1.15, 1.17 |
| `std.StringHashMap` | 0.7, 1.9, 1.10, 1.11, 1.12, 1.15, 1.17, 1.20 |
| `std.PriorityQueue` | 1.4, 1.5, 1.12 |
| `std.BoundedArray` | 1.3 |

## String & Formatting

| API | Key Recipes |
|-----|-------------|
| `std.mem.eql` | 0.3, 0.6, 0.10, 2.1, 2.2, 2.7, 2.8 |
| `std.mem.indexOf` | 2.1, 2.3, 2.4, 2.5, 5.1, 5.11 |
| `std.mem.splitScalar` | 2.1, 2.11, 5.3, 13.1 |
| `std.fmt.allocPrint` | 0.3, 2.5, 2.9, 3.3, 3.4, 5.5, 5.17 |
| `std.fmt.bufPrint` | 2.9, 5.2, 5.17, 5.20, 8.1, 8.2, 11.7 |
| `std.ascii.lowerString` | 1.12, 2.6, 2.13 |
| `std.unicode` | 2.12, 2.14 |

## JSON & Data Encoding

| API | Key Recipes |
|-----|-------------|
| `std.json.parseFromSlice` | 6.1, 6.2, 11.2 |
| `std.json.stringify` | 6.2, 11.2 |
| `std.json.Scanner` | 6.2, 13.9 |
| SQLite (C interop) | 6.6 |
| CSV parsing | 6.3 |
| Binary struct I/O | 6.9 |

## Concurrency & Threading

| API | Key Recipes |
|-----|-------------|
| `std.Thread.spawn` | 5.12, 11.7, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.10 |
| `std.Thread.join` | 11.7, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.10 |
| `std.atomic.Mutex` | 8.3, 11.7, 12.1, 12.2, 12.3, 12.4, 12.5 |
| `std.atomic.Value` | 11.7, 12.3, 12.4, 12.5, 12.6, 12.7, 12.10 |
| `io.sleep` | 3.12, 5.12, 11.7, 12.1, 12.3, 12.4, 12.5, 12.10 |

## Networking

| API | Key Recipes |
|-----|-------------|
| `IpAddress.listen` (TCP server) | 20.1 |
| `IpAddress.bind` (UDP) | 20.5 |
| `IpAddress.connect` | (see 11.1 for HTTP client) |
| `Server.accept` | 20.1 |
| `posix.setsockopt` | 20.2, 20.5 |
| HTTP client | 11.1 |
| JSON API client | 11.2 |
| WebSocket | 11.3 |
| HTTP server | 11.4 |
| File upload/download | 11.9 |
| Packet parsing | 20.3 |
| Zero-copy (sendfile) | 20.2 |

## Process & System

| API | Key Recipes |
|-----|-------------|
| `std.process.spawn` | 13.5, 13.14 |
| `Io.Clock.awake.now` | 3.12, 5.2, 5.5, 5.6, 5.12, 8.18, 9.1 |
| `Io.Clock.real.now` | 5.17, 13.10 |
| File descriptor ops | 5.16 |
| Serial port I/O | 5.18 |
| Temp files | 5.17 |
| Dir handles (testable I/O) | 5.20 |
| File position gotchas | 5.21 |
| File copy/move | 13.6 |
| Archive/extract | 13.7 |
| Logging | 13.10 |
| Browser launch | 13.14 |

## Memory & Allocators

| API | Key Recipes |
|-----|-------------|
| `std.mem.Allocator` interface | 0.12, 18.1 |
| Custom allocator | 18.1 |
| Arena allocator | 0.12, 18.2 |
| FixedBufferAllocator | 18.5 |
| Object pool | 18.4 |
| Memory-mapped I/O | 18.3, 6.9 |
| Memory debugging | 18.6 |

## Comptime & Metaprogramming

| API | Key Recipes |
|-----|-------------|
| `@typeInfo` | 9.1, 9.5, 9.12, 9.15, 17.1, 17.4 |
| `@Type` / `@Struct` / `@Enum` | 9.16 |
| `@field` | 9.1, 9.6, 9.10, 9.12 |
| `inline for` | 9.1, 9.4, 9.5, 9.8 |
| Comptime string processing | 17.2 |
| Comptime assertions | 17.3 |
| Generic data structures | 17.4 |
| Comptime dependency injection | 17.5 |
| Build-time resource embedding | 17.6 |
| Comptime memoization | 17.7 |

## Recipe File Path Convention

Recipe `X.Y` is at:
- Chapter 0: `code/00-bootcamp/recipe_0_Y.zig`
- Chapter 1-5: `code/02-core/{section}/recipe_{chapter}_{Y}.zig`
- Chapter 6-10: `code/03-advanced/{section}/recipe_{chapter}_{Y}.zig`
- Chapter 11-15: `code/04-specialized/{section}/recipe_{chapter}_{Y}.zig`
- Chapter 16-20: `code/05-zig-paradigms/{section}/recipe_{chapter}_{Y}.zig`
