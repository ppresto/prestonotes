"""Guard TASK-018 / TASK-019 playbooks are tracked and present (Wave C–D)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_run_exec_briefing_and_debug_pipeline_playbooks_tracked() -> None:
    manifest = (REPO_ROOT / "scripts/ci/required-paths.manifest").read_text(encoding="utf-8")
    for rel in (
        "docs/ai/playbooks/run-exec-briefing.md",
        "docs/ai/playbooks/debug-pipeline.md",
    ):
        assert rel in manifest, f"{rel} must be listed in required-paths.manifest"
        path = REPO_ROOT / rel
        assert path.is_file(), f"missing {rel}"
        assert path.stat().st_size > 200, f"{rel} should be non-trivial content"
