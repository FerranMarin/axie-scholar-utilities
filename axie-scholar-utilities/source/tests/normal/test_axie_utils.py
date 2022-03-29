import pytest

from axie.utils import load_json


def test_load_json_safeguard():
    with pytest.raises(Exception) as e:
        load_json("non_existent.json")
    assert str(e.value) == ("File path non_existent.json does not exist. "
                            "Please provide a correct one")


def test_load_json(tmpdir):
    f = tmpdir.join("test.json")
    f.write('{"foo": "bar"}')
    loaded = load_json(f)
    assert loaded == {"foo": "bar"}


def test_load_json_not_json(tmpdir):
    f = tmpdir.join("test.txt")
    f.write("foo bar")
    with pytest.raises(Exception) as e:
        load_json(f)
    assert str(e.value) == f"File in path {f} is not a correctly encoded JSON."
