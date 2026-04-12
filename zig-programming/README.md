# Zig Programming Skill for Claude Code

Comprehensive Zig 0.16.0 programming expertise for Claude Code, including async I/O, 223 tested recipes, reference documentation, templates, and examples.

## Installation

Symlink or copy this directory into your Claude Code skills directory:

```bash
# Symlink (recommended - updates with git pull)
ln -s "$(pwd)" ~/.claude/skills/zig-programming

# Or copy
cp -r . ~/.claude/skills/zig-programming
```

Restart Claude Code after installation.

## Structure

```
zig-programming/
├── SKILL.md                 # Main skill instructions (Claude reads this)
├── references/              # Zig 0.16.0 documentation by topic
│   ├── core-language.md
│   ├── control-flow.md
│   ├── functions-errors.md
│   ├── memory-management.md
│   ├── comptime.md
│   ├── async-overview.md
│   ├── async-vs-concurrent.md
│   └── ...                  # 22 files total
├── recipes/                 # 223 tested code recipes
├── examples/                # 9 complete working programs
├── assets/templates/        # 7 code templates
└── build/                   # Build tools (not distributed)
    └── consolidator.py
```

## Updating References

To regenerate reference docs from the official Zig documentation:

```bash
# From repo root:
python converter/zig_docs_converter.py --version master --output converter/docs-master
python zig-programming/build/consolidator.py converter/docs-master zig-programming/references
```
