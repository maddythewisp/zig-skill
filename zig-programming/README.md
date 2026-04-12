# Zig Programming Skill

Comprehensive Zig 0.16.0 programming skill for AI coding agents, including async I/O, 223 tested recipes, reference documentation, templates, and examples.

## Installation

Symlink or copy this directory into your agent's skills directory:

```bash
# Claude Code
ln -s "$(pwd)" ~/.claude/skills/zig-programming

# Codex
ln -s "$(pwd)" ~/.codex/skills/zig-programming
```

Restart the agent after installation.

## Structure

```
zig-programming/
├── SKILL.md                 # Main skill instructions (agent reads this)
├── references/              # Zig 0.16.0 documentation by topic (22 files)
├── recipes/                 # 223 tested code recipes
├── examples/                # 9 complete working programs
├── assets/templates/        # 7 code templates
└── tools/
    └── consolidator.py      # Doc consolidation tool
```

## Updating References

To regenerate reference docs from the official Zig documentation:

```bash
# From repo root:
python converter/zig_docs_converter.py --version master --output converter/docs-master
python zig-programming/tools/consolidator.py converter/docs-master zig-programming/references
```
