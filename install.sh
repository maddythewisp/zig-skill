#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/zig-programming" && pwd)"
SKILL_NAME="zig-programming"

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "Error: $SKILL_DIR/SKILL.md not found"
    exit 1
fi

installed=0

# Claude Code
claude_dir="$HOME/.claude/skills"
if [ -d "$HOME/.claude" ]; then
    mkdir -p "$claude_dir"
    target="$claude_dir/$SKILL_NAME"
    if [ -L "$target" ]; then
        echo "Claude Code: updating existing symlink"
        rm "$target"
    elif [ -e "$target" ]; then
        echo "Claude Code: $target already exists (not a symlink), skipping"
    fi
    if [ ! -e "$target" ]; then
        ln -s "$SKILL_DIR" "$target"
        echo "Claude Code: installed -> $target"
        installed=1
    fi
else
    echo "Claude Code: ~/.claude not found, skipping"
fi

# Codex
codex_dir="$HOME/.codex/skills"
if [ -d "$HOME/.codex" ]; then
    mkdir -p "$codex_dir"
    target="$codex_dir/$SKILL_NAME"
    if [ -L "$target" ]; then
        echo "Codex: updating existing symlink"
        rm "$target"
    elif [ -e "$target" ]; then
        echo "Codex: $target already exists (not a symlink), skipping"
    fi
    if [ ! -e "$target" ]; then
        ln -s "$SKILL_DIR" "$target"
        echo "Codex: installed -> $target"
        installed=1
    fi
else
    echo "Codex: ~/.codex not found, skipping"
fi

if [ "$installed" -eq 0 ]; then
    echo ""
    echo "No agents found. Make sure ~/.claude or ~/.codex exists, then re-run."
    exit 1
fi
