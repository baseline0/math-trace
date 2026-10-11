#!/usr/bin/env python
"""Generate CHANGELOG.md entries from conventional commits since last tag."""

import re
import subprocess
from datetime import datetime
from pathlib import Path


def get_latest_tag() -> str | None:
    """Get the most recent git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def get_commits_since(ref: str | None = None) -> list[dict]:
    """Get conventional commits since ref (or all if ref is None)."""
    commit_range = f"{ref}..HEAD" if ref else "HEAD"

    try:
        result = subprocess.run(
            ["git", "log", commit_range, "--pretty=format:%s|%b"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return []

    commits = []
    lines = result.stdout.strip().split("\n")

    for line in lines:
        if not line or "|" not in line:
            continue

        subject, _ = line.split("|", 1)
        match = re.match(r"^(feat|fix|chore|docs|refactor|test|perf|ci)(?:\((.+?)\))?!?: (.+)$", subject)

        if match:
            commit_type, scope, description = match.groups()
            commits.append(
                {
                    "type": commit_type,
                    "scope": scope or None,
                    "description": description,
                    "subject": subject,
                }
            )

    return commits


def group_commits(commits: list[dict]) -> dict[str, list[dict]]:
    """Group commits by type."""
    grouped = {}
    type_order = ["feat", "fix", "perf", "refactor", "test", "docs", "chore"]

    for commit_type in type_order:
        grouped[commit_type] = [c for c in commits if c["type"] == commit_type]

    return {k: v for k, v in grouped.items() if v}


def format_changelog_section(version: str, commits: list[dict]) -> str:
    """Format commits as changelog markdown section."""
    grouped = group_commits(commits)
    date = datetime.now().strftime("%Y-%m-%d")

    type_labels = {
        "feat": "✨ Features",
        "fix": "🐛 Fixes",
        "perf": "⚡ Performance",
        "refactor": "♻️  Refactoring",
        "test": "🧪 Tests",
        "docs": "📚 Documentation",
        "chore": "🔧 Chores",
    }

    lines = [f"## [{version}] — {date}\n"]

    for commit_type, commit_list in grouped.items():
        label = type_labels.get(commit_type, commit_type.title())
        lines.append(f"### {label}\n")

        for commit in commit_list:
            scope_str = f"({commit['scope']}) " if commit["scope"] else ""
            lines.append(f"- {scope_str}{commit['description']}\n")

        lines.append("")

    return "".join(lines)


def update_changelog(version: str, new_section: str) -> None:
    """Prepend new changelog section to CHANGELOG.md."""
    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        changelog_path.write_text(new_section)
        return

    existing = changelog_path.read_text()

    # Remove old "Generated from conventional commits" header if present
    header = "# Changelog\n\nGenerated from conventional commits. See git log for full history.\n\n"
    if existing.startswith("# Changelog"):
        # Extract everything after the header
        parts = existing.split("\n", 3)
        existing = parts[3] if len(parts) > 3 else ""

    updated = header + new_section + existing
    changelog_path.write_text(updated)


def main() -> None:
    """Generate and update CHANGELOG.md."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: generate-changelog.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    latest_tag = get_latest_tag()

    commits = get_commits_since(latest_tag)

    if not commits:
        print(f"ℹ️  No conventional commits found since {latest_tag or 'beginning'}")
        return

    section = format_changelog_section(version, commits)
    update_changelog(version, section)

    print(f"✅ Generated {len(commits)} commits for v{version}")
    print("📝 Updated CHANGELOG.md")


if __name__ == "__main__":
    main()
