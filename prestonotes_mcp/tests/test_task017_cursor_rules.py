"""Guard TASK-017 orchestrator + task router rules and manifest entries."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_update_customer_notes_orchestrator_rules_tracked() -> None:
    manifest = (REPO_ROOT / "scripts/ci/required-paths.manifest").read_text(encoding="utf-8")
    assert ".cursor/rules/10-task-router.mdc" in manifest
    assert ".cursor/rules/20-orchestrator.mdc" in manifest
    for rel in (
        ".cursor/rules/10-task-router.mdc",
        ".cursor/rules/20-orchestrator.mdc",
    ):
        path = REPO_ROOT / rel
        assert path.is_file(), f"missing {rel}"
        head = path.read_text(encoding="utf-8").split("---", 2)
        assert len(head) >= 3, f"{rel} must have YAML frontmatter"
        front = head[1]
        assert "alwaysApply: false" in front, (
            f"{rel} must not be always-on (conflicts with workflow.mdc)"
        )
