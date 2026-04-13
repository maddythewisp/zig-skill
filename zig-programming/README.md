# Zig Programming Skill

Zig 0.16.0 programming skill for AI coding agents. Includes a correct API cheatsheet, 303 tested recipes (via BBQ Cookbook submodule), reference documentation, templates, and examples.

## Installation

```bash
# Claude Code
ln -s "$(pwd)" ~/.claude/skills/zig-programming

# Codex
ln -s "$(pwd)" ~/.codex/skills/zig-programming
```

Or use the install script from the parent repo: `./install.sh`

## Structure

```
zig-programming/
├── SKILL.md                 # Main skill (API cheatsheet + recipe lookup)
├── references/              # Zig 0.16.0 documentation by topic (23 files)
│   └── api-recipe-index.md  # API name → recipe file mapping
├── recipes/
│   └── recipes-index.json   # Compact recipe metadata (303 recipes)
├── examples/                # Code pattern examples
├── assets/templates/        # Code templates
├── scripts/
│   └── query_recipes.py     # Recipe search tool
└── tools/
    └── consolidator.py      # Doc consolidation tool
```

Recipes are in the `zig-bbq-cookbook/` submodule as tested .zig files.
SKILL.md points to them directly — no prose duplication.
