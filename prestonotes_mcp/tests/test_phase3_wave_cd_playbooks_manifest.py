"""Guard Wave C–D playbooks referenced by CI manifest are present."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_wave_cd_playbooks_tracked() -> None:
    manifest = (REPO_ROOT / "scripts/ci/required-paths.manifest").read_text(encoding="utf-8")
    for rel in (
        "docs/ai/playbooks/run-journey-timeline.md",
        "docs/ai/playbooks/refresh-wiz-doc-cache.md",
        "docs/ai/playbooks/bootstrap-customer.md",
    ):
        assert rel in manifest, f"{rel} must be listed in required-paths.manifest"
        path = REPO_ROOT / rel
        assert path.is_file(), f"missing {rel}"
        assert path.stat().st_size > 200, f"{rel} should be non-trivial content"
