import pytest

from pytest_fixture_forms import FixtureForms


class AdvancedFixtureForms(FixtureForms):
    def __init__(self, *args, **kwargs):
        self.custom_form_property = None
        super().__init__(*args, **kwargs)


class SomeFixtureForm(AdvancedFixtureForms):
    @pytest.fixture
    def form1(self, set_custom_form_property):
        assert self.custom_form_property == "custom form property value"
        return "1"


@pytest.fixture
def set_custom_form_property(some_fixture_form_prototype: SomeFixtureForm):
    some_fixture_form_prototype.custom_form_property = "custom form property value"


def test_advanced_fixture_forms(some_fixture_form: SomeFixtureForm):
    assert some_fixture_form.custom_form_property == "custom form property value"
    assert some_fixture_form.value == "1"
    print(some_fixture_form)