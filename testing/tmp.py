from pytest_fixture_forms import FixtureForms
import pytest


class KeyId(FixtureForms):
    @pytest.fixture
    def id(self):
        return "123"

@pytest.fixture
def some_fixture():
    return "fixture value"

def test_key_id(some_fixture,key_id):
    # key_id has both form and value set
    assert key_id.form in ["arn", "id"]
    if key_id.form == "arn":
        assert key_id.value.startswith("arn:aws:")
    else:
        assert key_id.value == "123"
