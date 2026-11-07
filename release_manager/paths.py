"""Canonical repo-root resolution for the Release Manager.

The RM reads/writes shared data (releases/, scene_intelligence/*.json). If the
server is launched from a git worktree, `Path(__file__).parent.parent` resolves to
the WORKTREE's copy, so its data diverges from the main repo. `repo_root()` instead
resolves to the MAIN working tree via git's common-dir (a linked worktree's
common-dir points at the main repo's .git), so data always lands in one place
regardless of where the server runs. Falls back to the code location if git is
unavailable.
"""
import subprocess
from pathlib import Path


def repo_root():
    """Return the main repo root, robust to running from a git worktree."""
    fallback = Path(__file__).resolve().parent.parent
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(fallback), capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            gcd = Path(out.stdout.strip())
            if not gcd.is_absolute():
                gcd = fallback / gcd
            root = gcd.resolve().parent
            # sanity: the real root has the releases/ dir
            if (root / "releases").is_dir():
                return root
    except (OSError, subprocess.SubprocessError):
        pass
    return fallback
