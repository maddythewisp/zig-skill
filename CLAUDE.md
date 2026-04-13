# Zig Skill Repository

This repo provides a Zig 0.16.0 programming skill for AI coding agents.

## Structure

- `zig-programming/` — The skill (symlinked into `~/.claude/skills/`)
- `zig-bbq-cookbook/` — Submodule with 303 tested recipe .zig files

## Key Files

- `zig-programming/SKILL.md` — API cheatsheet and recipe lookup (invoke with `/zig-programming`)
- `zig-programming/references/api-recipe-index.md` — Find recipes by API name
- `zig-bbq-cookbook/code/` — All recipe source files, run with `zig test <file>`

## Zig 0.16 Quick Reminders

- I/O parameter is `io: std.Io` (value type, NOT pointer `*std.Io`)
- In tests use `const io: std.Io = std.testing.io;`
- File ops: `std.Io.Dir.openFile(.cwd(), io, path, .{})`, `file.close(io)`
- ArrayList: `std.ArrayList(T).empty`, pass allocator to methods
- No `fs.cwd()`, `file.seekTo`, `file.read`, `posix.socket`, `posix.close`
