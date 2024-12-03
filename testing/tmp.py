from pytest_fixture_forms import FixtureForms
import pytest


class KeyId(FixtureForms):
    @pytest.fixture
    def arn(self):
        # self is an instance of KeyId with form="arn"
        return f"arn:aws:{self.region}"

    @pytest.fixture
    def id(self):
        return "123"

@pytest.fixture(autouse=True)
def region(key_id_prototype):
    # We can access the form before the value is computed
    if key_id_prototype.form == "arn":
        key_id_prototype.region = "us-east-1"


def test_key_id(key_id):
    # key_id has both form and value set
    assert key_id.form in ["arn", "id"]
    if key_id.form == "arn":
        assert key_id.value.startswith("arn:aws:")
    else:
        assert key_id.value == "123"
