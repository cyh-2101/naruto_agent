from pathlib import Path

from naruto_agent.cli import doctor


def test_doctor_has_reduced_non_windows_report(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(doctor.sys, "platform", "linux")
    report, windows, messages = doctor.collect_report(tmp_path)
    assert report["Native Windows"] == "False"
    assert report["Window candidates"] == "not available on this platform"
    assert windows == []
    assert any("No emulator candidate" in message for message in messages)
