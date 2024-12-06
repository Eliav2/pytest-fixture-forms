import pytest

from pytest_fixture_forms import FixtureForms


class MyForm(FixtureForms):
    """
    This class dynamically defines the following fixtures:
        - my_form - current instance of the parameter
        - my_form_form - current form of the parameter
        each fixture method in this class is considered a form of the parameter, and would generate the following fixtures:
        - my_form_<form> - value of the parameter in the form of <form>
    """
    @pytest.fixture
    def form_requesting_parameterized_fixture(self, parameterized_fixture):
        return parameterized_fixture



@pytest.fixture(params=["param1", "param2"])
def parameterized_fixture(request):
    return request.param


def test_my_form(my_form: MyForm):
    assert my_form.value in ["something", "something else", "fixture value", "param1", "param2"]
    print(my_form)
