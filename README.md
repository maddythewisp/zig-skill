# Zig Programming Skill

Comprehensive Zig 0.16.0 programming skill for AI coding agents, including async I/O patterns, 223 tested recipes, reference documentation, templates, and examples.

## Installation

Run the install script to symlink into all detected agents (Claude Code, Codex):

```bash
./install.sh
```

Or install manually:

```bash
# Claude Code
ln -s /path/to/zig-programming ~/.claude/skills/zig-programming

# Codex
ln -s /path/to/zig-programming ~/.codex/skills/zig-programming
```

Restart the agent after installation.

### Verify Installation

```bash
# Claude Code
ls ~/.claude/skills/zig-programming/SKILL.md

# Codex
ls ~/.codex/skills/zig-programming/SKILL.md
```

## What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| **References** | 22 files | Zig 0.16.0 documentation organized by topic |
| **Recipes** | 223 | Tested code recipes from [BBQ Cookbook](https://github.com/whit3rabbit/zig-bbq-cookbook) |
| **Templates** | 7 | CLI app, library, build.zig, tests, C interop, async |
| **Examples** | 9 | Complete working programs including async I/O |

### Reference Topics

- Core language, control flow, functions, error handling
- Data structures, structs, enums, unions, pointers, arrays/slices
- Memory management, comptime, testing
- Build system, C interop, stdlib/builtins
- Async I/O overview, async vs concurrent patterns
- Pattern collections (data structures, errors, memory, integration)

### Recipe Topics

Fundamentals, data structures, strings, memory/allocators, comptime, structs, functions, file I/O, networking, concurrency, build system, testing, C interop, data encoding, iterators, WebAssembly.

## Usage

The skill activates automatically when working with Zig code:

```
"How do I iterate with an index in Zig?"
→ Provides for loop syntax with examples

"Show me how to use ArenaAllocator"
→ Loads relevant recipe with tested code

"How does async I/O work in Zig 0.16?"
→ Loads async-overview.md and shows io.async() patterns
```

## Repository Structure

```
zig-programming/             # The skill (install this directory)
├── SKILL.md                 # Main skill instructions
├── references/              # Zig 0.16.0 documentation
├── recipes/                 # 223 BBQ Cookbook recipes
├── examples/                # Complete working programs
└── assets/templates/        # Code templates
converter/                   # Zig HTML docs converter tool
```

## Updating References

To regenerate reference docs from the official Zig documentation:

```bash
# Convert official HTML docs to markdown
python converter/zig_docs_converter.py --version master --output converter/docs-master

# Consolidate into themed reference files
python zig-programming/tools/consolidator.py converter/docs-master zig-programming/references
```

## Links

- **BBQ Cookbook**: [github.com/whit3rabbit/zig-bbq-cookbook](https://github.com/whit3rabbit/zig-bbq-cookbook)
- **Official Zig Docs**: [ziglang.org/documentation](https://ziglang.org/documentation/)

## License

MIT License. Zig documentation content follows Zig project licensing.
