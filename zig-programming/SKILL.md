---
name: zig-programming
description: >
  Provides comprehensive Zig 0.16.0 programming language expertise including syntax, standard library,
  build system, memory management, error handling, async I/O, and C interoperability. Use this skill when
  working with Zig code, learning Zig concepts, debugging compilation errors, or building Zig applications.
---

# Zig Programming Language Skill

This skill provides expertise in Zig 0.16.0, a general-purpose programming language focused on robustness, optimality, and maintainability. Includes reference documentation, async I/O patterns, 223 tested recipes, code templates, and examples.

## Table of Contents

- [Bundled Resources](#bundled-resources)
  - [References](#references) - Documentation organized by topic
  - [Recipes](#recipes) - 223 tested recipes organized by topic
  - [Templates](#templates) - Starting points for common tasks
  - [Examples](#examples) - Practical code samples
- [Workflows](#workflows)
- [Best Practices](#best-practices)

## Bundled Resources

### References

Load documentation progressively based on task complexity:

**New to Zig?** Start with fundamentals in order:
1. `references/core-language.md` - Basic syntax, types, operators
2. `references/control-flow.md` - If, while, for, switch
3. `references/functions-errors.md` - Functions and error handling
4. `references/quick-reference.md` - Syntax quick lookup

**Solving specific problems?** Jump directly to:
- **Error handling** - `references/functions-errors.md` + `references/patterns-error-testing.md`
- **Memory/allocators** - `references/memory-management.md` + `references/patterns-memory-comptime.md`
- **Data structures** - `references/arrays-slices.md`, `references/structs-methods.md`, `references/enums-unions.md`, `references/pointers-references.md`
- **Struct/array/enum patterns** - `references/patterns-data-structures.md`
- **Stdlib lookup** - grep `references/stdlib-builtins.md` (large file)
- **C interop** - `references/c-interop.md` + `references/patterns-integration.md`
- **Build system** - `references/build-system.md` + `references/patterns-integration.md`
- **Async I/O** - `references/async-overview.md` + `references/async-vs-concurrent.md`

**Advanced topics:**
- `references/comptime.md` - Compile-time execution and generics
- `references/patterns-memory-comptime.md` - Advanced memory and comptime patterns
- `references/testing-quality.md` - Testing framework and best practices
- `references/async-overview.md` - Async I/O design philosophy and `std.Io` interface
- `references/async-vs-concurrent.md` - Critical async vs concurrent distinction

### Recipes

The skill includes **223 tested recipes** from the Zig BBQ Cookbook. All recipes include complete, compilable code verified against Zig 0.16.0.

**Finding recipes by topic:**
- `recipes/fundamentals.md` - Philosophy, basics (19 recipes)
- `recipes/data-structures.md` - Arrays, hashmaps, sets (20 recipes)
- `recipes/strings-text.md` - String processing (14 recipes)
- `recipes/memory-allocators.md` - Allocator patterns (6 recipes)
- `recipes/comptime-metaprogramming.md` - Compile-time (24 recipes)
- `recipes/structs-objects.md` - Structs, unions (22 recipes)
- `recipes/functions.md` - Function patterns (11 recipes)
- `recipes/files-io.md` - File operations (19 recipes)
- `recipes/networking.md` - HTTP, sockets (18 recipes)
- `recipes/concurrency.md` - Threading, atomics (8 recipes)
- `recipes/build-system.md` - Build.zig, modules (18 recipes)
- `recipes/testing-debugging.md` - Testing (14 recipes)
- `recipes/c-interop.md` - C FFI (7 recipes)
- `recipes/data-encoding.md` - JSON, CSV, XML (9 recipes)
- `recipes/iterators.md` - Iterator patterns (8 recipes)
- `recipes/webassembly.md` - WASM targets (6 recipes)

**Recipe format:** Each recipe includes Problem, Solution, Discussion sections plus full tested code.

**When to use recipes vs references:**
- **Recipes**: "How do I..." questions, practical tasks, working code examples
- **References**: "What is..." questions, API lookup, comprehensive documentation

### Templates

Copy and customize these starting points:
- `assets/templates/basic-program.zig` - Basic program with allocator
- `assets/templates/build.zig` - Build configuration
- `assets/templates/test.zig` - Test file structure
- `assets/templates/cli-application.zig` - CLI app with arg parsing
- `assets/templates/library-module.zig` - Library/module structure
- `assets/templates/c-interop-module.zig` - C interop module
- `assets/templates/async-function.zig` - Async I/O function patterns

### Examples

Complete, runnable code demonstrating patterns:
- `examples/string_manipulation.zig` - String processing
- `examples/memory_management.zig` - Allocator patterns
- `examples/error_handling.zig` - Error handling
- `examples/c_interop.zig` - C FFI
- `examples/comptime_example.zig` - Compile-time programming
- `examples/build_example/` - Multi-file project
- `examples/basic_async.zig` - Async I/O basics with `io.async()`
- `examples/concurrent_tasks.zig` - Producer-consumer with `io.concurrent()`
- `examples/cancellation.zig` - Async cancellation and cleanup patterns

## Workflows

### Writing New Code

1. **Start from template** - Copy appropriate template from `assets/templates/`
2. **Handle errors explicitly** - Use `try`, `catch`, or `errdefer`
3. **Pass allocators** - Never use global state, pass allocators as parameters
4. **Add tests immediately** - Write `test` blocks alongside implementation
5. **Document public APIs** - Use `///` doc comments for exported functions

### Writing Async I/O Code

Zig 0.16 introduces async I/O via the `std.Io` interface. Key principles:

1. **Accept `io: *std.Io` parameter** - Like allocators, pass explicitly to functions needing async
2. **Use `io.async()` by default** - Operations can proceed out-of-order; sequential awaiting is valid
3. **Use `io.concurrent()` sparingly** - Only when operations MUST run simultaneously (producer-consumer)
4. **Always handle cancellation** - Use `defer future.cancel(io)` for resource cleanup
5. **Test with blocking I/O first** - Reveals dependency issues before adding concurrency

**Critical distinction: async ≠ concurrent**
- `io.async()`: operations *can* proceed out-of-order (works with blocking I/O too)
- `io.concurrent()`: operations *must* run simultaneously (fails if parallelism unavailable)

**Quick pattern:**
```zig
fn process(io: *std.Io, data: []const u8) !void {
    var fut_a = io.async(save, .{io, data, "a.txt"});
    var fut_b = io.async(save, .{io, data, "b.txt"});
    try fut_a.await(io);
    try fut_b.await(io);
}
```

**Load references:** `references/async-overview.md` and `references/async-vs-concurrent.md`
**Load examples:** `examples/basic_async.zig`, `examples/concurrent_tasks.zig`, `examples/cancellation.zig`

### Debugging Compilation Errors

**Zig-specific gotchas:**
- **Comptime type resolution** - Use `@TypeOf()` inspection or add explicit casts
- **Allocator lifetime issues** - Verify `defer` cleanup order and `errdefer` on error paths
- **Optional unwrapping** - Use `.?` only when certain; prefer `orelse` or `if` unwrap for safety

**Debug tools:** `std.debug.print()` for inspection, `-Doptimize=Debug` for stack traces, `zig test` to isolate issues

### Explaining Concepts

To teach Zig concepts effectively:
1. **Load relevant reference** - Start with the appropriate reference file for the topic
2. **Show runnable code** - Use complete examples from `examples/` directory
3. **Highlight uniqueness** - Emphasize Zig's distinguishing features (explicit allocators, comptime, no hidden control flow)
4. **Reference stdlib** - Point to specific standard library functions when applicable

## Best Practices

Core Zig idioms:

1. **Explicit error handling** - Use `try`, `catch`, or error unions; never ignore errors
2. **Defer cleanup** - Use `defer` for cleanup, `errdefer` for error-path cleanup
3. **Pass allocators** - Never use global state; pass allocators explicitly as parameters
4. **Leverage comptime** - Use compile-time execution for generic programming
5. **Write tests inline** - Use `test "description" {}` blocks alongside implementation
6. **Document public APIs** - Add `///` doc comments for exported functions
7. **Handle optionals explicitly** - Use `orelse`, `.?`, or `if` unwrapping
8. **No hidden control flow** - Zig has no hidden allocations or exceptions
9. **Pass Io explicitly** - Like allocators, pass `io: *std.Io` as a parameter for async-capable functions
10. **Default to `io.async()` over `io.concurrent()`** - Only use concurrent when simultaneous execution is required
