from release_manager.paths import repo_root


def test_repo_root_points_at_main_working_tree():
    root = repo_root()
    # the canonical root is the one that actually holds the data dirs
    assert (root / "releases").is_dir()
    assert (root / "scene_intelligence").is_dir()
    # and it is NOT a linked worktree path
    assert ".config/superpowers/worktrees" not in str(root)
