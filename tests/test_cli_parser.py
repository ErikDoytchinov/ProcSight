import sys

import psutil
import pytest

from procsight.cli.parser import get_params


class _FakeIterProc:
    def __init__(self, pid: int, name: str, cmd: list[str] | None = None):
        self.info = {"pid": pid, "name": name, "cmdline": cmd or []}


def test_cli_requires_pid_or_name(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog"])
    with pytest.raises(SystemExit):
        get_params()


def test_cli_accepts_pid(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["prog", "--pid", "1234", "--interval", "0.1"]
    )  # speed up
    args = get_params()
    assert args.pid == 1234
    assert args.interval == 0.1


def test_cli_name_single_match(monkeypatch):
    # Simulate a single matching process
    def fake_iter(attrs=None):
        yield _FakeIterProc(111, "python3", ["python3", "app.py"])

    monkeypatch.setattr(psutil, "process_iter", fake_iter)
    monkeypatch.setattr(sys, "argv", ["prog", "--name", "python", "--interval", "0.1"])

    args = get_params()
    assert args.pid == 111


def test_cli_name_no_match(monkeypatch):
    def fake_iter(attrs=None):
        if False:
            yield  # pragma: no cover
        return

    monkeypatch.setattr(psutil, "process_iter", fake_iter)
    monkeypatch.setattr(sys, "argv", ["prog", "--name", "doesnotexist"])

    with pytest.raises(SystemExit):
        get_params()
