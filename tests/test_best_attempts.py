import json

from logic_utils import (
    load_best_attempts,
    save_best_attempts,
    update_best_attempts,
)


def test_load_missing_file_returns_empty(tmp_path):
    path = str(tmp_path / "nope.json")
    assert load_best_attempts(path) == {}


def test_load_corrupt_file_returns_empty(tmp_path):
    path = tmp_path / "attempts.json"
    path.write_text("not valid json {", encoding="utf-8")
    assert load_best_attempts(str(path)) == {}


def test_load_ignores_non_positive_and_non_int_values(tmp_path):
    path = tmp_path / "attempts.json"
    path.write_text(
        json.dumps({"Easy": 3, "Normal": 0, "Hard": -2, "Other": "oops"}),
        encoding="utf-8",
    )
    assert load_best_attempts(str(path)) == {"Easy": 3}


def test_save_then_load_roundtrip(tmp_path):
    path = str(tmp_path / "attempts.json")
    save_best_attempts({"Hard": 5}, path)
    assert load_best_attempts(path) == {"Hard": 5}


def test_first_attempt_is_always_a_record(tmp_path):
    path = str(tmp_path / "attempts.json")
    is_record, best = update_best_attempts("Normal", 4, path)
    assert is_record is True
    assert best == 4


def test_fewer_attempts_replaces_previous(tmp_path):
    path = str(tmp_path / "attempts.json")
    update_best_attempts("Normal", 4, path)
    is_record, best = update_best_attempts("Normal", 2, path)
    assert is_record is True
    assert best == 2


def test_more_attempts_does_not_replace(tmp_path):
    path = str(tmp_path / "attempts.json")
    update_best_attempts("Normal", 2, path)
    is_record, best = update_best_attempts("Normal", 5, path)
    assert is_record is False
    assert best == 2


def test_difficulties_tracked_independently(tmp_path):
    path = str(tmp_path / "attempts.json")
    update_best_attempts("Easy", 3, path)
    update_best_attempts("Hard", 6, path)
    assert load_best_attempts(path) == {"Easy": 3, "Hard": 6}
