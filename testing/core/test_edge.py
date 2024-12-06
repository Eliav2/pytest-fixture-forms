import pytest
from pytest_fixture_forms import FixtureForms


class ClassWithOneForm(FixtureForms):
    @pytest.fixture
    def best_form(self):
        return "best"


def test_class_with_one_form(class_with_one_form):
    assert class_with_one_form.value == "best"


class ClassWithOneParameterizedForm(FixtureForms):
    @pytest.fixture(params=["param1", "param2"])
    def best_form(self, request):
        return request.param


def test_class_with_one_parameterized_form(class_with_one_parameterized_form):
    assert class_with_one_parameterized_form.value in ["param1", "param2"]
