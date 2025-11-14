import builtins
from pathlib import Path

import pytest

import business_analyzer as ba
from consulting.data_processing import sanitize_filename


def test_sanitize_filename_basic():
    assert sanitize_filename("Acme Corp!") == "Acme_Corp"
    assert sanitize_filename("") == "business"


def test_prompt_int_reprompts_and_parses_commas(monkeypatch):
    # inputs: invalid -> negative -> valid
    seq = iter(["abc", "-5", "1,234"])  # should end as 1234
    monkeypatch.setattr(builtins, "input", lambda *_: next(seq))
    assert ba.prompt_int("Number of employees") == 1234


def test_prompt_float_parses_currency(monkeypatch):
    seq = iter(["$1,250,000"])  # should parse to 1250000.0
    monkeypatch.setattr(builtins, "input", lambda *_: next(seq))
    assert ba.prompt_float("Annual revenue") == 1250000.0


def test_prompt_challenges_early_stop(monkeypatch):
    # Provide two challenges then blank
    seq = iter(["A", "B", ""])  # stops early
    monkeypatch.setattr(builtins, "input", lambda *_: next(seq))
    assert ba.prompt_challenges(max_items=3) == ["A", "B"]


def test_confirm_variants(monkeypatch):
    seq = iter(["yes", "no", "", "Y", "N"])  # last two uppercase
    monkeypatch.setattr(builtins, "input", lambda *_: next(seq))
    assert ba.confirm("Proceed?", default=False) is True
    assert ba.confirm("Proceed?", default=True) is False
    # Empty answer returns default
    assert ba.confirm("Proceed?", default=True) is True
    assert ba.confirm("Proceed?", default=False) is True  # 'Y'
    assert ba.confirm("Proceed?", default=True) is False  # 'N'


@pytest.mark.parametrize("ch1,ch2,ch3", [("Ops", "Data", ""), ("Ops", "", ""), ("", "", "")])
def test_main_creates_files(monkeypatch, tmp_path: Path, ch1, ch2, ch3):
    # Prepare input sequence: name, industry, employees, revenue, challenges x3, confirm yes
    inputs = iter([
        "Acme Corp",  # name
        "Retail",     # industry
        "42",         # employees
        "$1,000,000", # revenue
        ch1, ch2, ch3, # challenges (may stop early)
        "y",          # confirm
    ])
    monkeypatch.setattr(builtins, "input", lambda *_: next(inputs))
    # Speed up progress animation
    monkeypatch.setattr(ba, "progress", lambda *args, **kwargs: None)
    monkeypatch.chdir(tmp_path)

    ba.main()

    base = sanitize_filename("Acme Corp")
    json_path = tmp_path / f"{base}.json"
    report_path = tmp_path / f"{base}_report.txt"
    assert json_path.exists(), "JSON file should be created"
    assert report_path.exists(), "Report file should be created"
