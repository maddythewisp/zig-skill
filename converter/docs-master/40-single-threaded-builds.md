## Single Threaded Builds

Zig has a compile option `-fsingle-threaded` which has the following effects:

- All [Thread Local Variables](#Thread-Local-Variables) are treated as regular [Container Level Variables](46-c.md#Container-Level-Variables).
- The overhead of [Async Functions](37-async-functions.md#Async-Functions) becomes equivalent to function call overhead.
- The `@import("builtin").single_threaded` becomes `true`
  and therefore various userland APIs which read this variable become more efficient.
  For example `std.Mutex` becomes
  an empty data structure and all of its functions become no-ops.
