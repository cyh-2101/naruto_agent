from pathlib import Path


def test_default_suite_has_no_live_marker_or_windows_backend_construction() -> None:
    root = Path(__file__).parent
    offenders: list[str] = []
    for path in root.glob("test_*.py"):
        if path.name == Path(__file__).name:
            continue
        source = path.read_text(encoding="utf-8")
        if "@pytest.mark.live" in source or "WindowsInputBackend(" in source:
            offenders.append(path.name)
    assert offenders == []
