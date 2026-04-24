from pathlib import Path


def test_pre_commit_config_lists_expected_official_repos() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "https://github.com/astral-sh/ruff-pre-commit" in text
    assert "https://github.com/shellcheck-py/shellcheck-py" in text
    assert "https://github.com/adrienverge/yamllint" in text
    assert "https://github.com/antonbabenko/pre-commit-terraform" in text
