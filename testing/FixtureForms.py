from pytest_fixture_forms import FixtureForms
import pytest


class KeyId(FixtureForms):
    """
    This class dynamically defines the following fixtures:
        - key_id - current instance of the parameter
        - key_id_form - current form of the parameter
        each fixture method in this class is considered a form of the parameter, and would generate the following fixtures:
        - key_id_<form> - value of the parameter in the form of <form>
    """

    @pytest.fixture
    def default(self):
        return "alias/aws/s3"


# you can also test your param independently
def test_key_id(key_id: KeyId):
    print(f"{KeyId.__name__}.{key_id.form}={key_id.value}")
    assert bool(key_id)
    assert bool(key_id.value)
