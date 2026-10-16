#!/usr/bin/env python3
"""Install repository skills into Codex, AGY and Claude Code using symlinks."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from uuid import uuid4


REPOSITORY = Path(__file__).resolve().parents[1]
SKILLS = (REPOSITORY / 'skills').resolve()
TARGETS = ('codex', 'agy', 'claude')


@dataclass(frozen=True)
class Link:
    source: Path
    destination: Path


def link_status(link, replace_links=False):
    if link.destination.is_symlink():
        try:
            if link.destination.resolve() == link.source.resolve():
                return 'skip'
        except (OSError, RuntimeError):
            pass
        return 'replace' if replace_links else 'conflict'
    if link.destination.exists():
        return 'conflict'
    return 'create'


def replace_symlink(link):
    temporary = link.destination.parent / f'.open-skills-{uuid4().hex}.tmp'
    try:
        temporary.symlink_to(link.source, target_is_directory=True)
        if not link.destination.is_symlink():
            raise ValueError(f'Destination is no longer a symlink; refusing to replace: {link.destination}')
        temporary.replace(link.destination)
    finally:
        if temporary.is_symlink():
            temporary.unlink()


def skill_directories(names):
    available = {
        directory.name: directory.resolve()
        for directory in SKILLS.iterdir()
        if not directory.name.startswith('.') and directory.is_dir()
        and (directory / 'SKILL.md').is_file()
    }
    if not available:
        raise ValueError(f'No skills containing SKILL.md found in {SKILLS}')
    if names:
        unknown = sorted(set(names) - available.keys())
        if unknown:
            raise ValueError('Unknown skill(s): ' + ', '.join(unknown))
    return [(name, available[name]) for name in sorted(set(names or available))]


def install(arguments):
    skills = skill_directories(arguments.skill)
    roots = {
        target: Path(getattr(arguments, f'{target}_dir')).expanduser().resolve()
        for target in dict.fromkeys(arguments.target or TARGETS)
    }
    for root in roots.values():
        if root == SKILLS or SKILLS in root.parents:
            raise ValueError(f'Installation directory must not be inside the source skills directory: {root}')
        ancestor = root
        while not ancestor.exists() and ancestor != ancestor.parent:
            ancestor = ancestor.parent
        if not ancestor.is_dir():
            raise ValueError(f'Installation directory is blocked by a non-directory: {ancestor}')
    links = []
    seen = set()
    for target, root in roots.items():
        print(f'{target}: {root}')
        for name, source in skills:
            destination = root / name
            if destination not in seen:
                seen.add(destination)
                links.append(Link(source, destination))
    planned = [(link, link_status(link, arguments.replace_links)) for link in links]
    for link, status in planned:
        print(f'{status.upper():8} {link.destination} -> {link.source}')
    if any(status == 'conflict' for _, status in planned):
        print('Conflicts found; no changes made. Move existing entries aside, or use --replace-links to repoint symlinks only.', file=sys.stderr)
        return 1
    if arguments.dry_run:
        print('Dry run complete; no files or directories changed.')
        return 0
    created = skipped = replaced = 0
    for link, _ in planned:
        status = link_status(link, arguments.replace_links)
        if status == 'skip':
            skipped += 1
            continue
        if status == 'conflict':
            raise ValueError(f'Destination changed during installation; refusing to overwrite: {link.destination}')
        if status == 'replace':
            replace_symlink(link)
            replaced += 1
            continue
        link.destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            link.destination.symlink_to(link.source, target_is_directory=True)
            created += 1
        except FileExistsError:
            if link_status(link) != 'skip':
                raise ValueError(f'Destination appeared during installation; refusing to overwrite: {link.destination}')
            skipped += 1
    print(f'Done: {created} created, {replaced} symlink(s) repointed, {skipped} already installed. Restart or reload the target tools to discover skills.')
    return 0


def main():
    home = Path.home()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', action='append', choices=TARGETS,
                        help='Install for this tool only; repeat to select several (default: all three)')
    parser.add_argument('--skill', action='append', metavar='NAME',
                        help='Install this skill only; repeat to select several (default: all skills)')
    parser.add_argument('--dry-run', action='store_true', help='Show the plan without changing anything')
    parser.add_argument('--replace-links', action='store_true',
                        help='Repoint conflicting symlinks, including broken ones; never replace real files/directories')
    parser.add_argument('--codex-dir', default=str(home / '.agents/skills'), metavar='PATH',
                        help='Codex skill directory (default: ~/.agents/skills; override for ~/.codex/skills)')
    parser.add_argument('--agy-dir', default=str(home / '.gemini/antigravity-cli/skills'), metavar='PATH',
                        help='AGY CLI skill directory (default: ~/.gemini/antigravity-cli/skills)')
    parser.add_argument('--claude-dir', default=str(home / '.claude/skills'), metavar='PATH',
                        help='Claude Code skill directory (default: ~/.claude/skills)')
    arguments = parser.parse_args()
    try:
        return install(arguments)
    except (OSError, RuntimeError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
