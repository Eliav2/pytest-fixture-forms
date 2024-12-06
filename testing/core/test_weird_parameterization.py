import pytest

from pytest_fixture_forms import FixtureForms


class SomeEdgeParam1(FixtureForms):
    @pytest.fixture
    def val1(self):
        return "1"

    @pytest.fixture
    def val2(self):
        return "2"


class SomeEdgeParam2(FixtureForms):
    @pytest.fixture
    def val1(self):
        return "1"

    @pytest.fixture
    def val2(self):
        return "2"


@pytest.mark.parametrize("some_edge_param1_val1", ["1", "1"])
@pytest.mark.parametrize("some_edge_param2_val1", ["9", "9"])
@pytest.mark.parametrize("some_edge_param1_form", ["val1"])
@pytest.mark.parametrize("some_edge_param2_form", ["val1"])
def test_weird_parameterization(
    some_edge_param1,
    some_edge_param2,
    some_edge_param1_val1,
    some_edge_param2_val1,
    some_edge_param1_form,
    some_edge_param2_form,
):
    assert some_edge_param1.value == "1"
    assert some_edge_param2.value == "9"

    assert some_edge_param1_val1 == "1"
    assert some_edge_param2_val1 == "9"


@pytest.mark.parametrize("some_edge_param1_val1", ["1", "1"])
@pytest.mark.parametrize("some_edge_param2_val1", ["9", "9"])
def test_weird_parameterization2(
    some_edge_param1,
    some_edge_param2,
    some_edge_param1_val1,
    some_edge_param2_val1,
    some_edge_param1_form,
    some_edge_param2_form,
):
    assert some_edge_param1.value in ["1", "2"]
    assert some_edge_param2.value in ["2", "9"]
