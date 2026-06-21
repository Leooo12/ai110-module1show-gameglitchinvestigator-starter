import json

from logic_utils import load_high_scores, save_high_scores, update_high_score


def test_load_missing_file_returns_empty(tmp_path):
    path = str(tmp_path / "nope.json")
    assert load_high_scores(path) == {}


def test_load_corrupt_file_returns_empty(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text("not valid json {", encoding="utf-8")
    assert load_high_scores(str(path)) == {}


def test_load_ignores_non_integer_scores(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text(json.dumps({"Easy": 90, "Normal": "oops"}), encoding="utf-8")
    assert load_high_scores(str(path)) == {"Easy": 90}


def test_save_then_load_roundtrip(tmp_path):
    path = str(tmp_path / "scores.json")
    save_high_scores({"Hard": 50}, path)
    assert load_high_scores(path) == {"Hard": 50}


def test_first_score_is_always_a_record(tmp_path):
    path = str(tmp_path / "scores.json")
    is_record, best = update_high_score("Normal", 70, path)
    assert is_record is True
    assert best == 70


def test_higher_score_replaces_previous(tmp_path):
    path = str(tmp_path / "scores.json")
    update_high_score("Normal", 70, path)
    is_record, best = update_high_score("Normal", 90, path)
    assert is_record is True
    assert best == 90


def test_lower_score_does_not_replace(tmp_path):
    path = str(tmp_path / "scores.json")
    update_high_score("Normal", 90, path)
    is_record, best = update_high_score("Normal", 60, path)
    assert is_record is False
    assert best == 90


def test_difficulties_tracked_independently(tmp_path):
    path = str(tmp_path / "scores.json")
    update_high_score("Easy", 80, path)
    update_high_score("Hard", 40, path)
    scores = load_high_scores(path)
    assert scores == {"Easy": 80, "Hard": 40}
