# open-skills

A collection of some AI skills

## Install with symlinks

Requires Python 3.8+ on macOS or Linux. Run from this repository:

```sh
# Preview only; does not create directories or links.
python3 scripts/install_skills.py --dry-run

# Install every skill for all three tools. Safe to run repeatedly.
python3 scripts/install_skills.py

# Select tools or skills; both flags can be repeated.
python3 scripts/install_skills.py --target codex --target claude --skill icloud-sync-repair

# Explicitly repoint existing symlinks from another repository, after previewing.
python3 scripts/install_skills.py --replace-links --dry-run
python3 scripts/install_skills.py --replace-links
```

| Tool | Default user skill directory |
|---|---|
| Codex | `~/.agents/skills` (current official location) |
| AGY / Antigravity CLI | `~/.gemini/antigravity-cli/skills` |
| Claude Code | `~/.claude/skills` |

Directories are configurable for older versions or custom profiles:

```sh
# Use this machine's existing legacy Codex skill directory instead.
python3 scripts/install_skills.py --target codex --codex-dir ~/.codex/skills

# For AGY versions using the shared global customization root.
python3 scripts/install_skills.py --target agy --agy-dir ~/.gemini/config/skills

# Override Claude Code's skill directory for a custom profile.
python3 scripts/install_skills.py --target claude --claude-dir /path/to/profile/skills
```

- Only immediate subdirectories of `skills/` containing `SKILL.md` are installed. Each entire skill directory is linked, including scripts, references and assets.
- Links use absolute paths resolved from the installer location, not the shell's working directory. Repository paths containing spaces are supported.
- Existing links to the same source are skipped, including equivalent relative links. Re-running does not create nested links or duplicate files. Source edits become available through the links immediately.
- By default, files, real directories, broken links and links to other sources are **never overwritten**. The script checks all selected destinations before writing; any known conflict exits with status `1` and makes no changes. Move the conflicting entry aside before retrying, or use `--replace-links` to explicitly repoint conflicting symlinks. This option replaces only the link, never its target or a real file/directory.
- Other I/O failures also return `1`; links already created before such a failure are retained, and re-running safely resumes. Success returns `0`; invalid command-line arguments return `2`.
- The script never deletes stale skills. After moving this repository, use `--replace-links` to repair its old links. Restart/reload the target application if its skill list is cached.
- Choose one Codex installation directory; installing the same skill in multiple discovery roots can create duplicate entries. See the [official Codex skills documentation](https://developers.openai.com/codex/skills/) and [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

# listing

| skill | explain |
|---|---|
| openspec-compound | Add knowledge precipitation and reuse capabilities to OpenSpec workflows, and refine reusable scenarios in changes to openspec/solutions/ knowledge base. |
| youtube-to-article | Analyze and interpret YouTube videos, summarize and generate articles that can be published. |
| icloud-sync-repair | Diagnose iCloud/CloudKit sync failures using device logs and schema exports, apply safe repairs, and verify recovery. |
