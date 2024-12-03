from pytest_fixture_forms import FixtureForms
import pytest


class MyForm(FixtureForms):
    """
    This class dynamically defines the following fixtures:
        - my_form - current instance of the parameter
        - my_form_form - current form of the parameter
        each fixture method in this class is considered a form of the parameter, and would generate the following fixtures:
        - my_form_<form> - value of the parameter in the form of <form>
    """

    @pytest.fixture
    def form1(self):
        return "something"

    @pytest.fixture
    def form2(self):
        return "something else"

    @pytest.fixture
    def form_requesting_fixture(self, some_fixture):
        return some_fixture

    @pytest.fixture
    def form_requesting_parameterized_fixture(self, parameterized_fixture):
        return parameterized_fixture

    @pytest.fixture
    def form_requesting_nested_fixture(self, nested_fixture):
        return nested_fixture


@pytest.fixture
def some_fixture():
    return "fixture value"


@pytest.fixture
def nested_fixture(some_fixture):
    return some_fixture


@pytest.fixture(params=["param1", "param2"])
def parameterized_fixture(request):
    return request.param


def test_my_form(my_form: MyForm):
    assert my_form.value in ["something", "something else", "fixture value", "param1", "param2"]
    print(my_form)


class TestForms:
    def test_my_form_form1(self, my_form_form1):
        assert my_form_form1 == "something"

    def test_my_form_form2(self, my_form_form2):
        assert my_form_form2 == "something else"

    def test_my_form_form_requesting_fixture(self, my_form_form_requesting_fixture):
        assert my_form_form_requesting_fixture == "fixture value"

    def test_my_form_form_requesting_parameterized_fixture(self, my_form_form_requesting_parameterized_fixture):
        assert my_form_form_requesting_parameterized_fixture in ["param1", "param2"]

    @pytest.mark.parametrize("parameterized_fixture", ["param3", "param4"])
    def test_my_form_form_requesting_parameterized_fixture_parametrized(
        self, my_form_form_requesting_parameterized_fixture, parameterized_fixture
    ):
        assert my_form_form_requesting_parameterized_fixture in ["param3", "param4"]

    def test_my_form_form_requesting_nested_fixture(self, my_form_form_requesting_nested_fixture):
        assert my_form_form_requesting_nested_fixture == "fixture value"


class MyForm2(FixtureForms):
    """
    This class dynamically defines the following fixtures:
        - my_form2 - current instance of the parameter
        - my_form2_form - current form of the parameter
        each fixture method in this class is considered a form of the parameter, and would generate the following fixtures:
        - my_form2_<form> - value of the parameter in the form of <form>
    """

    @pytest.fixture
    def form1(self):
        return "MyForm2_form1"

    @pytest.fixture
    def form2(self):
        return "MyForm2_form2"


def test_form_combination(my_form: MyForm, my_form2: MyForm2):
    assert my_form.value in ["something", "something else", "fixture value", "param1", "param2"]
    assert my_form2.value in ["MyForm2_form1", "MyForm2_form2"]
    print(my_form)
    print(my_form2)


@pytest.mark.parametrize("my_form_form", ["form1", "form2"])
@pytest.mark.parametrize("my_form2_form", ["form1"])
def test_form_combination_parameterized1(my_form: MyForm, my_form2: MyForm2, my_form_form, my_form2_form):
    assert my_form.value in ["something", "something else"]
    assert my_form2.value in ["MyForm2_form1"]
    print(my_form)
    print(my_form2)


@pytest.mark.parametrize("my_form_form", ["form1"])
def test_form_combination_parameterized2(my_form: MyForm, my_form2: MyForm2, my_form_form, my_form2_form):
    assert my_form.value in ["something"]
    assert my_form2.value in ["MyForm2_form1", "MyForm2_form2"]
